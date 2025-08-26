"""
简化的离线worker消息恢复模块
"""
import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from redis.asyncio.lock import Lock as AsyncLock

import msgpack

logger = logging.getLogger(__name__)


class OfflineWorkerRecovery:
    """离线worker消息恢复处理器"""
    
    def __init__(self, async_redis_client, consumer_manager=None, redis_prefix='jettask', worker_prefix='WORKER', queue_formatter=None):
        self.async_redis_client = async_redis_client
        self.consumer_manager = consumer_manager
        self.redis_prefix = redis_prefix
        self.worker_prefix = worker_prefix
        self._stop_recovery = False
        # 队列格式化函数，默认使用 prefix:QUEUE:queue_name 格式
        self.queue_formatter = queue_formatter or (lambda q: f"{self.redis_prefix}:QUEUE:{q}")
        
    async def recover_offline_workers(self,
                                     queue: str,
                                     current_consumer_name: str = None,
                                     event_queue: Optional[asyncio.Queue] = None,
                                     process_message_callback: Optional[callable] = None,
                                     consumer_group_suffix: Optional[str] = None) -> int:
        """
        恢复指定队列的离线worker的pending消息
        """
        total_recovered = 0
        
        try:
            # 获取当前consumer名称
            if not current_consumer_name and self.consumer_manager:
                current_consumer_name = self.consumer_manager.get_consumer_name(queue)
            
            if not current_consumer_name:
                logger.error(f"Cannot get current consumer name for queue {queue}")
                return 0
                
            # logger.info(f"Starting recovery for queue {queue} with consumer {current_consumer_name}")
            
            # 获取所有离线worker
            offline_workers = await self._find_offline_workers(queue)
            # logger.info(f'{offline_workers=}')
            if not offline_workers:
                logger.debug(f"No offline workers found for queue {queue}")
                return 0
                
            logger.info(f"Found {len(offline_workers)} offline workers for queue {queue}")
            
            # 处理每个离线worker
            for worker_key, worker_data in offline_workers:
                if self._stop_recovery:
                    logger.info("Stopping recovery due to shutdown signal")
                    break
                
                # logger.info(f"Processing offline worker: {worker_key}")
                recovered = await self._recover_worker_messages(
                    queue=queue,
                    worker_key=worker_key,
                    worker_data=worker_data,
                    current_consumer_name=current_consumer_name,
                    event_queue=event_queue,
                    process_message_callback=process_message_callback,
                    consumer_group_suffix=consumer_group_suffix
                )
                
                total_recovered += recovered
                
        except Exception as e:
            logger.error(f"Error recovering offline workers for queue {queue}: {e}")
            
        return total_recovered
        
    async def _find_offline_workers(self, queue: str) -> List[Tuple[str, Dict]]:
        """查找指定队列的离线worker"""
        offline_workers = []
        
        try:
            # 扫描所有worker
            pattern = f"{self.redis_prefix}:{self.worker_prefix}:*"
            cursor = 0
            while True:
                cursor, keys = await self.async_redis_client.scan(
                    cursor=cursor,
                    match=pattern,
                    count=100
                )
                
                for worker_key in keys:
                    if isinstance(worker_key, bytes):
                        worker_key = worker_key.decode('utf-8')
                    
                    # 跳过非worker键
                    if any(x in worker_key for x in [':HISTORY:', ':REUSE:LOCK', ':REUSING']):
                        continue
                    
                    try:
                        worker_data = await self.async_redis_client.hgetall(worker_key)
                        if not worker_data:
                            continue
                        
                        # 解码二进制数据
                        decoded_worker_data = {}
                        for k, v in worker_data.items():
                            key = k.decode('utf-8') if isinstance(k, bytes) else k
                            value = v.decode('utf-8') if isinstance(v, bytes) else v
                            decoded_worker_data[key] = value
                        
                        # logger.info(f'{worker_key=} {decoded_worker_data=}')
                        # logger.info(f'{decoded_worker_data=}')
                        # 检查worker是否离线且消息未转移
                        is_alive = decoded_worker_data.get('is_alive', 'false').lower() == 'true'
                        messages_transferred = decoded_worker_data.get('messages_transferred', 'false').lower() == 'true'
                        # logger.info(f'{worker_key=} {is_alive=} {messages_transferred=} {not is_alive and not messages_transferred}')
                        # 找到离线且消息未转移的worker
                        if not is_alive and not messages_transferred:
                            queues_str = decoded_worker_data.get('queues', '')
                            worker_queues = queues_str.split(',') if queues_str else []
                            
                            # logger.info(f'{worker_queues=} {queue=}')
                            # 检查这个worker是否负责当前队列
                            if queue in worker_queues:
                                offline_workers.append((worker_key, decoded_worker_data))
                                
                    except Exception as e:
                        logger.error(f"Error processing worker key {worker_key}: {e}")
                        continue
                
                # 当cursor返回0时，表示扫描完成
                if cursor == 0:
                    break
                    
        except Exception as e:
            logger.error(f"Error finding offline workers: {e}")
            
        return offline_workers
        
    async def _recover_worker_messages(self,
                                      queue: str,
                                      worker_key: str,
                                      worker_data: Dict,
                                      current_consumer_name: str,
                                      event_queue: Optional[asyncio.Queue] = None,
                                      process_message_callback: Optional[callable] = None,
                                      consumer_group_suffix: Optional[str] = None) -> int:
        """
        恢复单个worker的pending消息
        
        简化逻辑：
        1. 使用离线worker的consumer_id构建consumer名称：{consumer_id}-{queue}
        2. 默认group名称就是{prefixed_queue}
        3. 直接获取并转移该consumer的pending消息
        """
        total_claimed = 0
        
        try:
            # worker_data 现在已经是解码后的字典
            consumer_id = worker_data.get('consumer_id')
            
            # 构建离线worker的consumer名称
            offline_consumer = f"{consumer_id}-{queue}"
            
            logger.info(f"Recovering messages from offline worker: {offline_consumer}")
            
            # 检查是否是同一个worker（避免自己接管自己的消息）
            if current_consumer_name == offline_consumer or current_consumer_name.startswith(f"{offline_consumer}:"):
                logger.info(f"Skipping {offline_consumer} - same worker")
                return 0
                
            # 使用分布式锁防止并发处理
            lock_key = f"{self.redis_prefix}:CLAIM:LOCK:{offline_consumer}"
            lock = AsyncLock(
                self.async_redis_client,
                lock_key,
                timeout=60,
                blocking=False  # 不阻塞，直接跳过
            )
            
            if not await lock.acquire():
                logger.info(f"Another process is claiming messages for {offline_consumer}")
                return 0
                
            try:
                # 获取Stream的key
                prefixed_queue = self.queue_formatter(queue)
                logger.debug(f"Stream key: {prefixed_queue}, type: {type(prefixed_queue)}")
                
                # 获取所有的consumer groups
                all_groups = await self._get_consumer_groups(prefixed_queue)
                logger.info(f"Found {len(all_groups)} groups for stream {prefixed_queue}")
                
                for group_name in all_groups:
                    # 获取该group的所有consumers
                    try:
                        consumers_info = await self.async_redis_client.xinfo_consumers(prefixed_queue, group_name)
                        logger.debug(f"Consumers in group {group_name}: {consumers_info}")
                        
                        for consumer_info in consumers_info:
                            # 二进制Redis客户端返回的字典键是字符串，值是bytes
                            consumer_name = consumer_info.get('name', b'')
                            if isinstance(consumer_name, bytes):
                                consumer_name = consumer_name.decode('utf-8')
                            
                            pending_count = consumer_info.get('pending', 0)
                            logger.info(f'{offline_consumer=} {consumer_name=}')
                            # 检查是否是离线worker的consumer
                            # 离线consumer名称格式：{consumer_id}-{queue} 或 {consumer_id}-{queue}:{task_name}
                            if consumer_name.startswith(f"{offline_consumer}"):
                                logger.info(f'{consumer_info=}')
                                if pending_count > 0:
                                    logger.info(f"Found {pending_count} pending messages for {consumer_name} in group {group_name}")
                                    
                                    # 确定新的consumer名称
                                    # 如果原consumer有task后缀，新consumer也要有相同的task后缀
                                    if ':' in consumer_name and ':' in group_name:
                                        # 提取task后缀
                                        task_suffix = consumer_name.split(':', 1)[1]
                                        # 新consumer也要有相同的task后缀
                                        if ':' in current_consumer_name:
                                            # 如果当前consumer已经有后缀，保持它
                                            new_consumer = current_consumer_name
                                        else:
                                            # 添加task后缀
                                            new_consumer = f"{current_consumer_name}:{task_suffix}"
                                    else:
                                        new_consumer = current_consumer_name
                                    
                                    logger.info(f"Claiming messages from {consumer_name} to {new_consumer}")
                                    
                                    # 转移pending消息
                                    claimed = await self._claim_messages(
                                        prefixed_queue, group_name,
                                        consumer_name, new_consumer
                                    )
                                    
                                    if claimed:
                                        total_claimed += len(claimed)
                                        logger.info(f"Successfully claimed {len(claimed)} messages")
                                        
                                        # 处理转移的消息
                                        if process_message_callback:
                                            for msg_id, msg_data in claimed:
                                                await process_message_callback(msg_id, msg_data, queue, consumer_id)
                                        elif event_queue:
                                            for msg_id, msg_data in claimed:
                                                await self._put_to_event_queue(
                                                    msg_id, msg_data, queue,
                                                    event_queue, new_consumer,
                                                    group_name, consumer_name
                                                )
                    except Exception as e:
                        logger.error(f"Error processing group {group_name}: {e}")
                
                # 标记该worker的消息已转移（即使没有消息也要标记，避免重复处理）
                await self.async_redis_client.hset(worker_key, 'messages_transferred', 'true')
                if total_claimed > 0:
                    logger.info(f"Transferred total {total_claimed} messages from worker {consumer_id}")
                else:
                    logger.info(f"No messages to transfer from worker {consumer_id}, marked as processed")
                    
            finally:
                await lock.release()
                
        except Exception as e:
            logger.error(f"Error recovering messages: {e}")
            
        return total_claimed
        
    async def _get_consumer_groups(self, stream_key: str, suffix: Optional[str] = None) -> List[str]:
        """获取Stream的consumer groups"""
        groups = []
        try:
            # 确保stream_key是字符串类型（如果是bytes会出问题）
            if isinstance(stream_key, bytes):
                stream_key = stream_key.decode('utf-8')
            
            all_groups = await self.async_redis_client.xinfo_groups(stream_key)
            logger.debug(f"Raw groups info for {stream_key}: {all_groups}")
            
            for group_info in all_groups:
                # 二进制Redis客户端返回的字典键是字符串，值是bytes
                group_name = group_info.get('name', b'')
                logger.debug(f"Processing group: {group_info}, group_name type: {type(group_name)}")
                
                # 解码group名称
                if isinstance(group_name, bytes):
                    group_name = group_name.decode('utf-8')
                
                # 过滤空的group名称
                if group_name:
                    if suffix:
                        if group_name.endswith(suffix):
                            groups.append(group_name)
                    else:
                        groups.append(group_name)
                        logger.debug(f"Added group: {group_name}")
        except Exception as e:
            logger.error(f"Error getting consumer groups for {stream_key}: {e}")
        return groups
        
    async def _claim_messages(self, stream_key: str, group_name: str, 
                             old_consumer: str, new_consumer: str) -> List[Tuple[bytes, Dict]]:
        """转移pending消息"""
        all_claimed = []
        last_id = '-'
        
        try:
            # 确保参数是bytes类型
            if isinstance(stream_key, str):
                stream_key = stream_key.encode('utf-8')
            if isinstance(group_name, str):
                group_name = group_name.encode('utf-8')
            
            logger.debug(f"_claim_messages: stream_key={stream_key}, group_name={group_name}, old_consumer={old_consumer}, new_consumer={new_consumer}")
                
            while True:
                # 获取pending消息
                pending_batch = await self.async_redis_client.xpending_range(
                    stream_key, group_name,
                    min=last_id, max='+',
                    count=100
                )
                
                logger.debug(f"Got {len(pending_batch) if pending_batch else 0} pending messages")
                
                if not pending_batch:
                    break
                
                # 过滤出属于旧consumer的消息
                message_ids = []
                for msg in pending_batch:
                    msg_consumer = msg.get('consumer') or msg.get(b'consumer')
                    if isinstance(msg_consumer, bytes):
                        msg_consumer = msg_consumer.decode('utf-8')
                    
                    if msg_consumer == old_consumer:
                        msg_id = msg.get('message_id') or msg.get(b'message_id')
                        message_ids.append(msg_id)
                
                if message_ids:
                    # 使用XCLAIM转移消息
                    logger.info(f"Claiming {len(message_ids)} messages from {old_consumer} to {new_consumer}")
                    
                    claimed = await self.async_redis_client.xclaim(
                        stream_key, group_name,
                        new_consumer,
                        min_idle_time=0,
                        message_ids=message_ids,
                        force=True
                    )
                    
                    if claimed:
                        all_claimed.extend(claimed)
                
                # 更新游标
                if pending_batch:
                    last_msg_id = pending_batch[-1].get('message_id') or pending_batch[-1].get(b'message_id')
                    if isinstance(last_msg_id, bytes):
                        last_msg_id = last_msg_id.decode('utf-8')
                    # 增加ID以获取下一批
                    parts = last_msg_id.split('-')
                    if len(parts) == 2:
                        last_id = f"{parts[0]}-{int(parts[1]) + 1}"
                    else:
                        break
                else:
                    break
                    
        except Exception as e:
            logger.error(f"Error claiming messages: {e}")
            
        return all_claimed
        
    async def _put_to_event_queue(self, msg_id, msg_data, queue, event_queue, 
                                 consumer, group_name, old_consumer):
        """将转移的消息放入event_queue"""
        try:
            # 解析消息数据
            if b'data' in msg_data:
                event_data = msgpack.unpackb(msg_data[b'data'], raw=False)
            else:
                event_data = msg_data
            
            # 构建事件
            event = {
                'event_id': msg_id.decode() if isinstance(msg_id, bytes) else msg_id,
                'event_data': event_data,
                'queue': queue,
                'consumer': consumer,
                'group_name': group_name,
                '_recovery': True,
                '_claimed_from': old_consumer
            }
            
            await event_queue.put(event)
            
        except Exception as e:
            logger.error(f"Error putting message to event queue: {e}")
            
    def stop(self):
        """停止恢复处理"""
        self._stop_recovery = True
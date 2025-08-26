from ..utils.serializer import dumps_str, loads_str
import time
import threading
import logging
import contextlib
import asyncio
from collections import defaultdict, deque, Counter
from typing import List, Optional, TYPE_CHECKING, Union

import redis
from redis import asyncio as aioredis


from ..utils.helpers import get_hostname
import os
from .consumer_manager import ConsumerManager, ConsumerStrategy
from .offline_worker_recovery import OfflineWorkerRecovery

logger = logging.getLogger('app')


class EventPool(object):
    STATE_MACHINE_NAME = "STATE_MACHINE"
    TIMEOUT = 60 * 5

    def __init__(
        self,
        redis_client: redis.StrictRedis,
        async_redis_client: aioredis.StrictRedis,
        queues: list = None,
        redis_url: str = None,
        consumer_strategy: str = None,
        consumer_config: dict = None,
        redis_prefix: str = None,
        app=None,  # 添加app参数
    ) -> None:
        self.redis_client = redis_client
        self.async_redis_client = async_redis_client
        
        # 创建用于二进制数据的Redis客户端（用于Stream操作）
        from ..core.app import get_binary_redis_pool, get_async_binary_redis_pool
        binary_pool = get_binary_redis_pool(redis_url or 'redis://localhost:6379/0')
        self.binary_redis_client = redis.StrictRedis(connection_pool=binary_pool)
        async_binary_pool = get_async_binary_redis_pool(redis_url or 'redis://localhost:6379/0')
        self.async_binary_redis_client = aioredis.StrictRedis(connection_pool=async_binary_pool)
        
        self.queues = queues
        self._redis_url = redis_url or 'redis://localhost:6379/0'
        self.redis_prefix = redis_prefix or 'jettask'
        self.app = app  # 保存app引用
        
        # 初始化消费者管理器
        strategy = ConsumerStrategy(consumer_strategy) if consumer_strategy else ConsumerStrategy.HEARTBEAT
        # 确保配置中包含队列信息和redis_prefix
        manager_config = consumer_config or {}
        manager_config['queues'] = queues or []
        manager_config['redis_prefix'] = redis_prefix or 'jettask'
        
        # 保存consumer_config供后续使用
        self.consumer_config = manager_config
        
        self.consumer_manager = ConsumerManager(
            redis_client=redis_client,
            strategy=strategy,
            config=manager_config
        )
        
        # 创建带前缀的队列名称映射
        self.prefixed_queues = {}
        
        # 用于跟踪广播消息
        self._broadcast_message_tracker = {}
        
        self.solo_routing_tasks = {}
        self.solo_running_state = {}
        self.solo_urgent_retry = {}
        self.batch_routing_tasks = {}
        self.task_scheduler = {}
        self.running_task_state_mappings = {}
        self.delay_tasks = []
        self.solo_agg_task = {}
        self.rlock = threading.RLock()
        self._claimed_message_ids = set()  # 跟踪已认领的消息ID，防止重复处理
        self._stop_reading = False  # 用于控制停止读取的标志
        self._queue_stop_flags = {queue: False for queue in (queues or [])}  # 每个队列的停止标志
        # 延迟任务分布式锁的key
        self._delay_lock_key = f"{self.redis_prefix}:DELAY_LOCK"
    
    def _put_task(self, event_queue: Union[deque, asyncio.Queue], task, urgent: bool = False):
        """统一的任务放入方法"""
        # 如果是deque，使用原有逻辑
        if isinstance(event_queue, deque):
            if urgent:
                event_queue.appendleft(task)
            else:
                event_queue.append(task)
        # 如果是asyncio.Queue，则暂时只能按顺序放入（Queue不支持优先级）
        elif isinstance(event_queue, asyncio.Queue):
            # 对于asyncio.Queue，我们需要在async上下文中操作
            # 这里先保留接口，具体实现在async方法中
            pass
    
    async def _async_put_task(self, event_queue: asyncio.Queue, task, urgent: bool = False):
        """异步任务放入方法"""
        await event_queue.put(task)

    def init_routing(self):
        for queue in self.queues:
            self.solo_agg_task[queue] = defaultdict(list)
            self.solo_routing_tasks[queue] = defaultdict(list)
            self.solo_running_state[queue]  = defaultdict(bool)
            self.batch_routing_tasks[queue]  = defaultdict(list)
            self.task_scheduler[queue] = defaultdict(int)
            self.running_task_state_mappings[queue] = defaultdict(dict)
            
    def get_prefixed_queue_name(self, queue: str) -> str:
        """为队列名称添加前缀"""
        return f"{self.redis_prefix}:QUEUE:{queue}"
    
    def get_redis_client(self, asyncio: bool = False, binary: bool = False):
        """获取Redis客户端
        
        Args:
            asyncio: 是否使用异步客户端
            binary: 是否使用二进制客户端（用于Stream操作）
        """
        if binary:
            return self.async_binary_redis_client if asyncio else self.binary_redis_client
        return self.async_redis_client if asyncio else self.redis_client

    def create_group(self):
        """创建消费组 - 现在consumer group在listen_event_by_task中动态创建"""
        for queue in self.queues:
            prefixed_queue = self.get_prefixed_queue_name(queue)
            
            # 创建默认消费组（用于兼容性）
            with contextlib.suppress(Exception):
                prefixed_queue_bytes = prefixed_queue.encode() if isinstance(prefixed_queue, str) else prefixed_queue
                self.binary_redis_client.xgroup_create(
                    name=prefixed_queue_bytes,
                    groupname=prefixed_queue_bytes,
                    id=b"0",
                    mkstream=True,
                )

    def send_event(self, queue, message: dict, asyncio: bool = False):
        # 使用二进制客户端进行Stream操作
        client = self.get_redis_client(asyncio, binary=True)
        prefixed_queue = self.get_prefixed_queue_name(queue)
        # 确保键是bytes类型，但值不需要编码（msgpack已经返回二进制）
        prefixed_queue_bytes = prefixed_queue.encode() if isinstance(prefixed_queue, str) else prefixed_queue
        stream_data = {b'data': dumps_str(message)}  # 使用bytes键
        try:
            event_id = client.xadd(prefixed_queue_bytes, stream_data)
            # 将bytes类型的event_id转换为字符串返回
            if isinstance(event_id, bytes):
                event_id = event_id.decode('utf-8')
            return event_id
        except redis.exceptions.ResponseError as e:
            # 如果队列不存在，创建它
            if "ERR" in str(e):
                logger.warning(f'队列 {prefixed_queue} 不存在，正在创建...')
                try:
                    # 先创建队列
                    event_id = client.xadd(prefixed_queue_bytes, stream_data)
                    # 再创建消费者组
                    with contextlib.suppress(Exception):
                        client.xgroup_create(
                            name=prefixed_queue_bytes,
                            groupname=prefixed_queue_bytes,
                            id=b"0"
                        )
                    # 将bytes类型的event_id转换为字符串返回
                    if isinstance(event_id, bytes):
                        event_id = event_id.decode('utf-8')
                    return event_id
                except Exception as create_error:
                    logger.error(f'创建队列失败: {create_error}')
                    raise
            else:
                raise

    def batch_send_event(self, queue, messages: List[dict], asyncio: bool = False):
        # 使用二进制客户端进行Stream操作
        client = self.get_redis_client(asyncio, binary=True)
        pipe = client.pipeline()
        prefixed_queue = self.get_prefixed_queue_name(queue)
        prefixed_queue_bytes = prefixed_queue.encode() if isinstance(prefixed_queue, str) else prefixed_queue
        if asyncio:
            return self._batch_send_event(prefixed_queue_bytes, messages, pipe)
        for message in messages:
            # 确保消息格式正确
            if 'data' in message:
                binary_message = {b'data': message['data'] if isinstance(message['data'], bytes) else dumps_str(message['data'])}
            else:
                binary_message = message
            pipe.xadd(prefixed_queue_bytes, binary_message)
        return pipe.execute()

    async def _batch_send_event(self, prefixed_queue, messages: List[dict], pipe):
        for message in messages:
            # 确保消息格式正确
            if 'data' in message:
                binary_message = {b'data': message['data'] if isinstance(message['data'], bytes) else dumps_str(message['data'])}
            else:
                binary_message = message
            await pipe.xadd(prefixed_queue, binary_message)
        return await pipe.execute()
    
    def is_urgent(self, routing_key):
        is_urgent = self.solo_urgent_retry.get(routing_key, False)
        if is_urgent == True:
            del self.solo_urgent_retry[routing_key]
        return is_urgent
    
    @classmethod
    def separate_by_key(cls, lst):
        groups = {}
        for item in lst:
            key = item[0]['routing_key']
            if key not in groups:
                groups[key] = []
            groups[key].append(item)
        result = []
        group_values = list(groups.values())
        while True:
            exists_data = False
            for values in group_values:
                try:
                    result.append(values.pop(0))
                    exists_data = True
                except:
                    pass
            if not exists_data:
                break
        return result
    
    async def _unified_task_checker(self, event_queue: asyncio.Queue, checker_type: str = 'solo_agg'):
        """统一的任务检查器，减少代码重复"""
        last_solo_running_state = defaultdict(dict)
        last_wait_time = defaultdict(int)
        queue_batch_tasks = defaultdict(list)
        left_queue_batch_tasks = defaultdict(list)
        
        # 延迟任务专用状态
        delay_tasks = getattr(self, 'delay_tasks', []) if checker_type == 'delay' else []
        
        while True:
            has_work = False
            current_time = time.time()
            
            if checker_type == 'delay':
                # 延迟任务逻辑
                put_count = 0
                need_del_index = []
                for i in range(len(delay_tasks)):
                    schedule_time = delay_tasks[i][0]
                    task = delay_tasks[i][1]
                    if schedule_time <= current_time:
                        try:
                            await self._async_put_task(event_queue, task)
                            need_del_index.append(i)
                            put_count += 1
                            has_work = True
                        except IndexError:
                            pass
                for i in need_del_index:
                    del delay_tasks[i]
                    
            elif checker_type == 'solo_agg':
                # Solo聚合任务逻辑
                for queue in self.queues:
                    for agg_key, tasks in self.solo_agg_task[queue].items():
                        if not tasks:
                            continue
                            
                        has_work = True
                        need_del_index = []
                        need_lock_routing_keys = []
                        sort_by_tasks = self.separate_by_key(tasks)
                        max_wait_time = 5
                        max_records = 3
                        
                        for index, (routing, task) in enumerate(sort_by_tasks):
                            routing_key = routing['routing_key']
                            max_records = routing.get('max_records', 1)
                            max_wait_time = routing.get('max_wait_time', 0)
                            
                            with self.rlock:
                                if self.solo_running_state[queue].get(routing_key, 0) > 0:
                                    continue
                                    
                            if len(queue_batch_tasks[queue] + left_queue_batch_tasks[queue]) >= max_records:
                                break 
                                
                            task["routing"] = routing

                            if self.is_urgent(routing_key):
                                left_queue_batch_tasks[queue].append(task)
                            else:
                                queue_batch_tasks[queue].append(task)
                            need_lock_routing_keys.append(routing_key)
                            need_del_index.append(index)

                        for routing_key, count in Counter(need_lock_routing_keys).items():
                            with self.rlock:
                                self.solo_running_state[queue][routing_key] = count
                                
                        if last_solo_running_state[queue] != self.solo_running_state[queue]:
                            last_solo_running_state[queue] = self.solo_running_state[queue].copy()
                            
                        tasks = [task for index, task in enumerate(sort_by_tasks) if index not in need_del_index]
                        self.solo_agg_task[queue][agg_key] = tasks
                        
                        if (len(queue_batch_tasks[queue] + left_queue_batch_tasks[queue]) >= max_records or 
                            (last_wait_time[queue] and last_wait_time[queue] < current_time - max_wait_time)):
                            for task in queue_batch_tasks[queue]:
                                await self._async_put_task(event_queue, task)
                            for task in left_queue_batch_tasks[queue]:
                                await self._async_put_task(event_queue, task)    
                            queue_batch_tasks[queue] = []
                            left_queue_batch_tasks[queue] = []
                            last_wait_time[queue] = 0
                        elif last_wait_time[queue] == 0:
                            last_wait_time[queue] = current_time
            
            # 统一的睡眠策略
            sleep_time = self._get_optimal_sleep_time(has_work, checker_type)
            await asyncio.sleep(sleep_time)
    
    def _get_optimal_sleep_time(self, has_work: bool, checker_type: str) -> float:
        """获取最优睡眠时间"""
        if checker_type == 'delay':
            return 0.001 if has_work else 1.0
        elif has_work:
            return 0.001  # 有工作时极短休眠
        else:
            return 0.01   # 无工作时短暂休眠
    
    
    async def async_check_solo_agg_tasks(self, event_queue: asyncio.Queue):
        """异步版本的聚合任务检查"""
        await self._unified_task_checker(event_queue, checker_type='solo_agg')
    
    async def check_solo_agg_tasks(self, event_queue: asyncio.Queue):
        """聚合任务检查"""
        await self._unified_task_checker(event_queue, checker_type='solo_agg')
    
    def check_sole_tasks(self, event_queue: Union[deque, asyncio.Queue]):
        agg_task_mappings = {queue:  defaultdict(list) for queue in self.queues}
        agg_wait_task_mappings = {queue:  defaultdict(float) for queue in self.queues}
        task_max_wait_time_mapping = {}
        make_up_for_index_mappings = {queue:  defaultdict(int) for queue in self.queues} 
        while True:
            put_count = 0
            for queue in self.queues:
                agg_task = agg_task_mappings[queue]
                for routing_key, tasks in self.solo_routing_tasks[queue].items():
                    schedule_time = self.task_scheduler[queue][routing_key]
                    if tasks:
                        for task in tasks:
                            prev_routing = task[0]
                            if agg_key:= prev_routing.get('agg_key'):
                                if not self.running_task_state_mappings[queue][agg_key]:
                                    self.solo_running_state[queue][routing_key] = False
                                    break 
                    if (
                        schedule_time <= time.time()
                        and self.solo_running_state[queue][routing_key] == False
                    ) :
                            try:
                                routing, task = tasks.pop(0)
                            except IndexError:
                                continue
                            task["routing"] = routing
                            
                            agg_key = routing.get('agg_key')
                            if agg_key is not None:
                                start_time = agg_wait_task_mappings[queue][agg_key]
                                if not start_time:
                                    agg_wait_task_mappings[queue][agg_key] = time.time()
                                    start_time = agg_wait_task_mappings[queue][agg_key]
                                agg_task[agg_key].append(task)
                                max_wait_time = routing.get('max_wait_time', 3)
                                task_max_wait_time_mapping[agg_key] = max_wait_time
                                if len(agg_task[agg_key])>=routing.get('max_records', 100) or time.time()-start_time>=max_wait_time:
                                    logger.info(f'{agg_key=} {len(agg_task[agg_key])} 已满，准备发车！{routing.get("max_records", 100)} {time.time()-start_time} {max_wait_time}')
                                    for task in agg_task[agg_key]:
                                        task['routing']['version'] = 1
                                        self.running_task_state_mappings[queue][agg_key][task['event_id']] = time.time()
                                        self._put_task(event_queue, task, urgent=self.is_urgent(routing_key))
                                    agg_task[agg_key] = []
                                    make_up_for_index_mappings[queue][agg_key] = 0 
                                    agg_wait_task_mappings[queue][agg_key] = 0
                            else:
                                self._put_task(event_queue, task, urgent=self.is_urgent(routing_key))
                            self.solo_running_state[queue][routing_key] = True
                            put_count += 1
                for agg_key in agg_task.keys():
                    if not agg_task[agg_key]:
                        continue
                    start_time = agg_wait_task_mappings[queue][agg_key]
                    max_wait_time = task_max_wait_time_mapping[agg_key]
                    if make_up_for_index_mappings[queue][agg_key]>= len(agg_task[agg_key])-1:
                        make_up_for_index_mappings[queue][agg_key] = 0
                    routing = agg_task[agg_key][make_up_for_index_mappings[queue][agg_key]]['routing']
                    routing_key = routing['routing_key']
                    self.solo_running_state[queue][routing_key] = False
                    make_up_for_index_mappings[queue][agg_key] += 1
                    if time.time()-start_time>=max_wait_time:
                        logger.info(f'{agg_key=} {len(agg_task[agg_key])}被迫发车！ {time.time()-start_time} {max_wait_time}')
                        for task in agg_task[agg_key]:
                            task['routing']['version'] = 1
                            self.running_task_state_mappings[queue][agg_key][task['event_id']] = time.time()
                            self._put_task(event_queue, task, urgent=self.is_urgent(routing_key))
                        agg_task[agg_key] = []
                        make_up_for_index_mappings[queue][agg_key] = 0
                        agg_wait_task_mappings[queue][agg_key] = 0
            # 优化：根据处理任务数量动态调整休眠时间
            if not put_count:
                time.sleep(0.001)
            elif put_count < 5:
                time.sleep(0.0005)  # 少量任务时极短休眠
                
    async def check_batch_tasks(self, event_queue: asyncio.Queue):
        """批量任务检查 - 已简化为统一检查器"""
        # 批量任务逻辑已整合到其他检查器中，这个函数保留以兼容
        await asyncio.sleep(0.1)

    async def check_delay_tasks(self, event_queue: asyncio.Queue):
        """延迟任务检查"""
        await self._unified_task_checker(event_queue, checker_type='delay')

    def _handle_redis_error(self, error: Exception, consecutive_errors: int, queue: str = None) -> tuple[bool, int]:
        """处理Redis错误的通用方法
        返回: (should_recreate_connection, new_consecutive_errors)
        """
        if isinstance(error, redis.exceptions.ConnectionError):
            logger.error(f'Redis连接错误: {error}')
            consecutive_errors += 1
            if consecutive_errors >= 5:
                logger.error(f'连续连接失败{consecutive_errors}次，重新创建连接')
                return True, 0
            return False, consecutive_errors
            
        elif isinstance(error, redis.exceptions.ResponseError):
            if "NOGROUP" in str(error) and queue:
                logger.warning(f'队列 {queue} 或消费者组不存在')
                return False, consecutive_errors
            else:
                logger.error(f'Redis错误: {error}')
                consecutive_errors += 1
                return False, consecutive_errors
        else:
            logger.error(f'意外错误: {error}')
            consecutive_errors += 1
            return False, consecutive_errors

    def _process_message_common(self, event_id: str, event_data: dict, queue: str, event_queue, is_async: bool = False, consumer_name: str = None):
        """通用的消息处理逻辑，供同步和异步版本使用"""
        # 检查消息是否已被认领，防止重复处理
        if event_id in self._claimed_message_ids:
            logger.debug(f"跳过已认领的消息 {event_id}")
            return event_id
        
        # 解析消息中的实际数据
        # event_data 格式: {b'data': b'{"name": "...", "event_id": "...", ...}'}
        actual_event_id = event_id  # 默认使用Stream ID
        parsed_event_data = None  # 解析后的数据
        
        # 检查是否有data字段（Stream消息格式）
        if 'data' in event_data or b'data' in event_data:
            data_field = event_data.get('data') or event_data.get(b'data')
            if data_field:
                try:
                    # 直接解析二进制数据，不需要解码
                    if isinstance(data_field, bytes):
                        parsed_data = loads_str(data_field)
                    else:
                        parsed_data = data_field
                    # 检查是否有原始的event_id（延迟任务会有）
                    if 'event_id' in parsed_data:
                        actual_event_id = parsed_data['event_id']
                    # 使用解析后的数据作为event_data
                    parsed_event_data = parsed_data
                except (ValueError, UnicodeDecodeError):
                    pass  # 解析失败，使用默认的Stream ID
        
        # 如果成功解析了数据，使用解析后的数据；否则使用原始数据
        final_event_data = parsed_event_data if parsed_event_data is not None else event_data
        
        routing = final_event_data.get("routing")
        
        # 从consumer_name中提取group_name
        # consumer_name格式: "YYDG-xxx:task_name"  
        # group_name格式: "prefixed_queue:task_name"
        group_name = None
        if consumer_name and ':' in consumer_name:
            # 从consumer_name中提取task_name
            task_name_part = consumer_name.split(':', 1)[1]
            prefixed_queue = self.get_prefixed_queue_name(queue)
            group_name = f"{prefixed_queue}:{task_name_part}"
        
        task_item = {
            "queue": queue,
            "event_id": actual_event_id,
            "event_data": final_event_data,  # 使用解析后的数据
            "consumer": consumer_name,  # 添加消费者信息
            "group_name": group_name,  # 添加group_name用于ACK
        }
        
        push_flag = True
        if routing:
            # routing 现在直接是对象，不需要反序列化
            if agg_key := routing.get('agg_key'):
                self.solo_agg_task[queue][agg_key].append(
                    [routing, task_item]
                )
                push_flag = False
        
        if push_flag:
            if is_async:
                # 这里不能直接await，需要返回一个标记
                return ('async_put', task_item)
            else:
                self._put_task(event_queue, task_item)
        
        return event_id
    
    async def _start_offline_worker_processor_with_restart(self, queue: str, event_queue: asyncio.Queue):
        """启动带自动重启机制的离线worker处理器"""
        async def supervisor():
            """监督器任务，负责重启失败的处理器"""
            restart_count = 0
            max_restarts = 10
            
            while not self._stop_reading and restart_count < max_restarts:
                try:
                    logger.info(f"Starting offline worker processor for queue {queue} (attempt {restart_count + 1})")
                    await self._process_offline_workers(queue, event_queue)
                    # 如果正常退出（stop_reading为True），则不重启
                    if self._stop_reading:
                        logger.info(f"Offline worker processor for queue {queue} stopped normally")
                        break
                except asyncio.CancelledError:
                    logger.info(f"Offline worker processor for queue {queue} cancelled")
                    break
                except Exception as e:
                    restart_count += 1
                    import traceback 
                    traceback.print_exc()
                    logger.error(f"Offline worker processor for queue {queue} crashed: {e}")
                    if restart_count < max_restarts:
                        wait_time = min(restart_count * 5, 30)  # 递增等待时间，最多30秒
                        logger.info(f"Restarting offline worker processor for queue {queue} in {wait_time} seconds...")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(f"Offline worker processor for queue {queue} failed {max_restarts} times, giving up")
            
        # 创建监督器任务
        asyncio.create_task(supervisor())

    async def _process_offline_workers(self, queue: str, event_queue: asyncio.Queue):
        """定期检测离线worker并使用XCLAIM转移其pending消息 - 使用独立的恢复模块"""
        logger.info(f"Started offline worker processor for queue {queue}")
        
        # 创建离线worker恢复器
        recovery = OfflineWorkerRecovery(
            async_redis_client=self.async_binary_redis_client,
            redis_prefix=self.redis_prefix,
            worker_prefix='WORKER',
            consumer_manager=self.consumer_manager
        )
        
        # 等待consumer manager初始化
        wait_times = [0.1, 0.2, 0.4, 0.8, 1.6, 3.2]
        for wait_time in wait_times:
            try:
                current_consumer = self.consumer_manager.get_consumer_name(queue)
                if current_consumer:
                    logger.info(f"Consumer manager initialized for queue {queue}, consumer: {current_consumer}")
                    break
            except Exception as e:
                logger.debug(f"Consumer manager not ready yet, waiting {wait_time}s: {e}")
                await asyncio.sleep(wait_time)
        
        logger.info(f"Offline worker processor for queue {queue} is now active")
        
        # 扫描间隔
        scan_interval = 1  # 每30秒扫描一次
        
        while not self._stop_reading:
            try:
                # 调用恢复模块进行恢复
                # 不传递process_message_callback，让它使用event_queue
                recovered = await recovery.recover_offline_workers(
                    queue=queue,
                    event_queue=event_queue
                )
                
                if recovered > 0:
                    logger.info(f"Recovered {recovered} messages for queue {queue}")
                    
            except Exception as e:
                import traceback
                traceback.print_exc()
                logger.error(f"Error in offline worker processor for queue {queue}: {e}")
            
            # 等待下一次扫描
            await asyncio.sleep(scan_interval)
        
        logger.info(f"Stopped offline worker processor for queue {queue}")
    

    async def listening_event(self, event_queue: asyncio.Queue, prefetch_multiplier: int = 1):
        """监听事件 - 每个task都有独立的consumer group，天然支持广播"""
        
        # 创建一个字典来存储每个队列的延迟任务 - 使用list + Lock更高效
        # 创建一个字典来存储每个队列的延迟任务 - 使用list + Lock更高效
        delayed_tasks_lists = {}
        delayed_tasks_locks = {}
        for queue in self.queues:
            delayed_tasks_lists[queue] = []
            delayed_tasks_locks[queue] = asyncio.Lock()
        
        async def scan_delayed_tasks_for_queue(queue: str, task_list: list, task_lock: asyncio.Lock):
            """为单个队列独立扫描延迟任务"""
            base_interval = self.consumer_config.get('scan_interval', 0.05)  # 基础间隔50ms
            max_interval = 0.5  # 最大间隔500ms
            
            logger.info(f'Starting delayed task scanner for queue {queue}, interval={base_interval}')
            
            while not self._stop_reading:
                try:
                    current_time = time.time()
                    
                    # 扫描并获取下一个任务的到期时间
                    await self._scan_and_load_delayed_tasks_to_list(queue, task_list, task_lock)
                    
                    # 动态调整扫描间隔
                    # 如果有任务被加载，使用较短的间隔
                    # 否则可以使用较长的间隔以节省CPU
                    if task_list:
                        sleep_time = base_interval
                    else:
                        # 检查下一个任务的到期时间
                        delayed_queue_key = f"{self.redis_prefix}:DELAYED_QUEUE:{queue}"
                        result = await self.async_binary_redis_client.zrange(
                            delayed_queue_key, 0, 0, withscores=True
                        )
                        
                        if result:
                            next_task_time = result[0][1]
                            # 计算到下一个任务的时间，但不超过max_interval
                            sleep_time = min(max_interval, max(base_interval, next_task_time - current_time - 0.01))
                        else:
                            sleep_time = max_interval
                            
                except Exception as e:
                    logger.error(f"Error scanning delayed tasks for queue {queue}: {e}")
                    sleep_time = base_interval
                
                await asyncio.sleep(sleep_time)
        
        async def listen_event_by_task(queue, task_name):
            """为单个任务监听事件"""
            check_backlog = True
            lastid = "0-0"
            consecutive_errors = 0
            max_consecutive_errors = 5
            
            # 使用task_name作为consumer group
            prefixed_queue = self.get_prefixed_queue_name(queue)
            group_name = f"{prefixed_queue}:{task_name}"
            
            # 使用consumer_manager获取consumer名称，以便启动心跳等功能
            # print(f'listening_event {queue=}')
            managed_consumer_name = self.consumer_manager.get_consumer_name(queue)
            # 但是为了保持每个task独立的consumer，还是需要加上task_name
            consumer_name = f"{managed_consumer_name}:{task_name}"
            
            # 获取该队列的延迟任务列表和锁
            delayed_list = delayed_tasks_lists.get(queue)
            delayed_lock = delayed_tasks_locks.get(queue)
            
            while not self._stop_reading:
                # 批量获取并处理延迟任务（使用list更高效）
                if delayed_list:
                    # 原子地交换list内容
                    async with delayed_lock:
                        if delayed_list:
                            # 快速拷贝并清空原list
                            tasks_to_process = delayed_list.copy()
                            delayed_list.clear()
                        else:
                            tasks_to_process = []
                    
                    # 处理所有延迟任务
                    if tasks_to_process:
                        my_tasks = []  # 属于当前task的任务
                        other_tasks = []  # 属于其他task的任务
                        
                        for delayed_task in tasks_to_process:
                            # 检查任务是否属于当前task
                            task_data = delayed_task.get('data', {})
                            if isinstance(task_data, str):
                                import json
                                task_data = json.loads(task_data)
                            
                            msg_task_name = task_data.get('name')
                            if msg_task_name == task_name:
                                my_tasks.append((delayed_task, task_data))
                            else:
                                other_tasks.append(delayed_task)
                        
                        # 处理属于当前task的所有任务
                        for delayed_task, task_data in my_tasks:
                            event_id = delayed_task.get('event_id', f"delayed-{time.time()}")
                            task_data['_task_name'] = task_name
                            
                            # 记录延迟精度（用于调试）
                            if 'execute_at' in task_data:
                                delay_error = time.time() - task_data['execute_at']
                                if abs(delay_error) > 0.1:  # 超过100ms才记录
                                    logger.info(f'延迟任务 {event_id} 执行误差: {delay_error*1000:.1f}ms')
                            
                            result = self._process_message_common(
                                event_id, task_data, queue, event_queue,
                                is_async=True, consumer_name=consumer_name
                            )
                            if isinstance(result, tuple) and result[0] == 'async_put':
                                await self._async_put_task(event_queue, result[1])
                        
                        # 把不属于当前task的任务放回list
                        if other_tasks:
                            async with delayed_lock:
                                delayed_list.extend(other_tasks)
                
                # 然后处理正常的Stream消息
                if check_backlog:
                    myid = lastid
                else:
                    myid = ">"
                
                try:
                    # 读取消息，使用二进制客户端
                    prefixed_queue_bytes = prefixed_queue.encode() if isinstance(prefixed_queue, str) else prefixed_queue
                    # group_name_bytes = group_name.encode() if isinstance(group_name, str) else group_name
                    # consumer_name_bytes = consumer_name.encode() if isinstance(consumer_name, str) else consumer_name
                    myid_bytes = myid.encode() if isinstance(myid, str) else myid
                    # 动态调整阻塞时间：如果有延迟任务待处理，使用0（非阻塞）
                    # 否则使用阻塞时间以节省CPU
                    block_time = 1000  # 1秒阻塞
                    # 移除debug的print语句
                    
                    messages = await self.async_binary_redis_client.xreadgroup(
                        groupname=group_name,
                        consumername=consumer_name,
                        streams={prefixed_queue_bytes: myid_bytes},
                        count=prefetch_multiplier,
                        block=block_time
                    )
                    # logger.info(f'{group_name=} {consumer_name=} {block_time=}')
                    consecutive_errors = 0
                    # if check_backlog and messages:
                    #     logger.info(f'先消费之前的消息 {group_name=} ')
                    # logger.info(f'{check_backlog=} {messages=}')
                    if not messages:
                        check_backlog = False
                        # 当使用阻塞模式时，xreadgroup已经等待了block_time毫秒
                        # 不需要额外的sleep，这会导致不必要的CPU占用
                        continue
                    
                    check_backlog = len(messages[0][1]) > 0
                    
                    # 收集需要跳过的消息ID
                    skip_message_ids = []
                    
                    for message in messages:
                        for event in message[1]:
                            event_id = event[0]
                            lastid = event_id
                            # 将bytes类型的event_id转换为字符串
                            if isinstance(event_id, bytes):
                                event_id = event_id.decode('utf-8')
                            event_data = event[1]
                            
                            # 解析消息内容，决定是否处理
                            should_process = True
                            
                            try:
                                # 解析data字段中的消息
                                if b'data' in event_data or 'data' in event_data:
                                    data_field = event_data.get(b'data') or event_data.get('data')
                                    
                                    # 直接解析二进制数据，不需要解码
                                    parsed_data = loads_str(data_field)
                                    
                                    # 跳过延迟任务（延迟任务由延迟扫描器处理）
                                    if parsed_data.get('is_delayed') == 1:
                                        should_process = False
                                        continue
                                    
                                    # 检查是否是广播消息
                                    is_broadcast = parsed_data.get('_broadcast', False)
                                    target_tasks = parsed_data.get('_target_tasks', None)
                                    
                                    if is_broadcast:
                                        # 广播消息：默认所有task都处理，除非被target_tasks排除
                                        if target_tasks and task_name not in target_tasks:
                                            should_process = False
                                    else:
                                        # 普通消息：必须有name字段且匹配当前task才处理
                                        msg_task_name = parsed_data.get('name')
                                        if not msg_task_name or msg_task_name != task_name:
                                            should_process = False
                                    
                                    if should_process:
                                        # 添加task_name到数据中（用于执行器识别任务）
                                        parsed_data['_task_name'] = task_name
                                        
                                        # 更新event_data
                                        event_data.clear()
                                        for key, value in parsed_data.items():
                                            event_data[key] = value
                                        
                                        logger.debug(f"Task {task_name} will process message {event_id}")
                                else:
                                    # 没有data字段，跳过消息
                                    should_process = False
                            except Exception as e:
                                logger.error(f"Task {task_name}: Error parsing message data: {e}")
                            
                            if should_process:
                                # 处理消息 - 消息会被放入队列，由执行器处理并ACK
                                result = self._process_message_common(
                                    event_id, event_data, queue, event_queue,
                                    is_async=True, consumer_name=consumer_name
                                )
                                if isinstance(result, tuple) and result[0] == 'async_put':
                                    await self._async_put_task(event_queue, result[1])
                                # 注意：这里不ACK，由执行器在处理完成后ACK
                            else:
                                # 不属于当前task的消息，收集起来批量ACK
                                skip_message_ids.append(event_id)
                            
                    
                    # 批量ACK不需要的消息
                    if skip_message_ids:
                        group_name_bytes = group_name.encode() if isinstance(group_name, str) else group_name
                        await self.async_binary_redis_client.xack(prefixed_queue_bytes, group_name_bytes, *skip_message_ids)
                        logger.debug(f"Task {task_name} batch ACKed {len(skip_message_ids)} skipped messages")
                        
                except Exception as e:
                    error_msg = str(e)
                    # import traceback
                    # traceback.print_exc()
                    logger.error(f"Error in task listener {task_name}: {e}")
                    
                    # 特殊处理：如果是NOGROUP错误，尝试重新创建consumer group
                    if "NOGROUP" in error_msg:
                        logger.info(f"Detected NOGROUP error for {task_name}, attempting to recreate consumer group...")
                        try:
                            await self.async_redis_client.xgroup_create(
                                name=prefixed_queue,
                                groupname=group_name,
                                id="0",
                                mkstream=True
                            )
                            logger.info(f"Successfully recreated consumer group {group_name} for task {task_name}")
                            # 重新创建成功，重置错误计数器
                            consecutive_errors = 0
                            continue
                        except Exception as create_error:
                            logger.error(f"Failed to recreate consumer group for {task_name}: {create_error}")
                    
                    consecutive_errors += 1
                    if consecutive_errors >= max_consecutive_errors:
                        logger.error(f"Too many errors for task {task_name}, restarting...")
                        consecutive_errors = 0
                    await asyncio.sleep(min(consecutive_errors, 5))
        
        logger.info(f"Starting event listeners for queues: {self.queues}")
        tasks = []
        
        if not (self.app and hasattr(self.app, '_tasks_by_queue')):
            raise RuntimeError("No app or tasks registered, cannot start listeners")
        
        # 为每个队列创建独立的延迟任务扫描器
        for queue in self.queues:
            logger.info(f"Starting delayed task scanner for queue: {queue}")
            scanner_task = asyncio.create_task(
                scan_delayed_tasks_for_queue(
                    queue, 
                    delayed_tasks_lists[queue], 
                    delayed_tasks_locks[queue]
                )
            )
            tasks.append(scanner_task)
        
        # 为每个队列启动离线worker处理器（带自动重启）
        for queue in self.queues:
            logger.info(f"Starting offline worker processor for queue: {queue}")
            offline_processor_task = asyncio.create_task(
                self._start_offline_worker_processor_with_restart(queue, event_queue)
            )
            tasks.append(offline_processor_task)
        
        # # 为每个task创建独立的listener
        for queue in self.queues:
            task_names = self.app._tasks_by_queue.get(queue, [])
            if not task_names:
                raise RuntimeError(f"No tasks registered for queue '{queue}'. Cannot start worker without tasks.")
            
            for task_name in task_names:
                logger.info(f"Starting listener for task: {task_name} on queue: {queue}")
                task = asyncio.create_task(listen_event_by_task(queue, task_name))
                tasks.append(task)
        
        # 等待所有任务
        await asyncio.gather(*tasks)
    
    async def _scan_and_load_delayed_tasks_to_list(self, queue: str, task_list: list, task_lock: asyncio.Lock):
        """扫描延迟队列并将到期任务加载到list（更高效）"""
        try:
            current_time = time.time()
            delayed_queue_key = f"{self.redis_prefix}:DELAYED_QUEUE:{queue}"
            prefixed_queue = self.get_prefixed_queue_name(queue)
            
            # 使用Lua脚本原子地获取并移除到期的任务
            lua_script = """
            local delayed_queue_key = KEYS[1]
            local stream_key = KEYS[2]
            local current_time = ARGV[1]
            local limit = ARGV[2]
            
            -- 获取到期的任务ID（这些是Stream消息ID）
            local expired_task_ids = redis.call('ZRANGEBYSCORE', delayed_queue_key, 0, current_time, 'LIMIT', 0, limit)
            
            if #expired_task_ids == 0 then
                return {}
            end
            
            local tasks_with_data = {}
            
            -- 获取每个任务的实际数据
            for i, task_id in ipairs(expired_task_ids) do
                -- 从Stream中读取任务数据
                local messages = redis.call('XRANGE', stream_key, task_id, task_id)
                if #messages > 0 then
                    -- 移除延迟队列中的任务
                    redis.call('ZREM', delayed_queue_key, task_id)
                    -- 添加到结果中
                    table.insert(tasks_with_data, messages[1])
                end
            end
            
            return tasks_with_data
            """
            
            # 注册Lua脚本（使用二进制客户端）
            if not hasattr(self, '_scan_delayed_script'):
                self._scan_delayed_script = self.async_binary_redis_client.register_script(lua_script)
            
            # 执行脚本，每次最多获取100个到期任务（提高批处理效率）
            expired_tasks = await self._scan_delayed_script(
                keys=[delayed_queue_key, prefixed_queue],
                args=[str(current_time), "100"]
            )
            # 移除频繁的debug日志，只在有任务时记录
            if not expired_tasks:
                return
            
            # 批量处理任务并添加到list
            tasks_to_add = []
            for task in expired_tasks:
                try:
                    if isinstance(task, list) and len(task) >= 2:
                        # task格式: [stream_id, fields]
                        stream_id = task[0]
                        fields = task[1]
                        
                        # 将fields转换为字典（保持二进制格式）
                        task_data = {}
                        if isinstance(fields, list):
                            for j in range(0, len(fields), 2):
                                if j + 1 < len(fields):
                                    key = fields[j]
                                    value = fields[j + 1]
                                    # 保持原始格式，不解码
                                    task_data[key] = value
                        
                        # 解析data字段
                        data_field = task_data.get('data') or task_data.get(b'data')
                        if data_field:
                            # 使用loads_str来解析（它能处理二进制和字符串）
                            data = loads_str(data_field)
                            # 添加event_id
                            data['event_id'] = stream_id if isinstance(stream_id, str) else stream_id.decode('utf-8')
                            
                            # 添加到列表
                            tasks_to_add.append({'event_id': data['event_id'], 'data': data})
                    
                except Exception as e:
                    logger.error(f"Error processing delayed task: {e}")
            
            # 批量添加到list（使用锁保证线程安全）
            if tasks_to_add:
                async with task_lock:
                    task_list.extend(tasks_to_add)
                logger.debug(f"Added {len(tasks_to_add)} delayed tasks to list for queue {queue}")
                    
        except Exception as e:
            logger.error(f"Error scanning delayed tasks for queue {queue}: {e}")
    
    async def _scan_and_load_delayed_tasks(self, queue: str, memory_queue: asyncio.Queue):
        """扫描延迟队列并将到期任务加载到内存队列"""
        try:
            current_time = time.time()
            delayed_queue_key = f"{self.redis_prefix}:DELAYED_QUEUE:{queue}"
            prefixed_queue = self.get_prefixed_queue_name(queue)
            
            # 使用Lua脚本原子地获取并移除到期的任务
            lua_script = """
            local delayed_queue_key = KEYS[1]
            local stream_key = KEYS[2]
            local current_time = ARGV[1]
            local limit = ARGV[2]
            
            -- 获取到期的任务ID（这些是Stream消息ID）
            local expired_task_ids = redis.call('ZRANGEBYSCORE', delayed_queue_key, 0, current_time, 'LIMIT', 0, limit)
            
            if #expired_task_ids == 0 then
                return {}
            end
            
            local tasks_with_data = {}
            
            -- 获取每个任务的实际数据
            for i, task_id in ipairs(expired_task_ids) do
                -- 从Stream中读取任务数据
                local messages = redis.call('XRANGE', stream_key, task_id, task_id)
                if #messages > 0 then
                    -- 移除延迟队列中的任务
                    redis.call('ZREM', delayed_queue_key, task_id)
                    -- 添加到结果中
                    table.insert(tasks_with_data, messages[1])
                end
            end
            
            return tasks_with_data
            """
            
            # 注册Lua脚本（使用二进制客户端）
            if not hasattr(self, '_scan_delayed_script'):
                self._scan_delayed_script = self.async_binary_redis_client.register_script(lua_script)
            
            # 执行脚本，每次最多获取100个到期任务（提高批处理效率）
            expired_tasks = await self._scan_delayed_script(
                keys=[delayed_queue_key, prefixed_queue],
                args=[str(current_time), "100"]
            )
            
            if not expired_tasks:
                return
            
            # 处理返回的任务
            for task in expired_tasks:
                try:
                    if isinstance(task, list) and len(task) >= 2:
                        # task格式: [stream_id, fields]
                        stream_id = task[0]
                        fields = task[1]
                        
                        # 将fields转换为字典（保持二进制格式）
                        task_data = {}
                        if isinstance(fields, list):
                            for j in range(0, len(fields), 2):
                                if j + 1 < len(fields):
                                    key = fields[j]
                                    value = fields[j + 1]
                                    # 保持原始格式，不解码
                                    task_data[key] = value
                        
                        # 解析data字段
                        data_field = task_data.get('data') or task_data.get(b'data')
                        if data_field:
                            # 使用loads_str来解析（它能处理二进制和字符串）
                            data = loads_str(data_field)
                            # 添加event_id
                            data['event_id'] = stream_id if isinstance(stream_id, str) else stream_id.decode('utf-8')
                            
                            # 将任务放入内存队列
                            await memory_queue.put({'event_id': data['event_id'], 'data': data})
                            logger.debug(f"Loaded delayed task {data['event_id']} to memory queue for queue {queue}")
                    
                except Exception as e:
                    logger.error(f"Error processing delayed task: {e}")
                    
        except Exception as e:
            logger.error(f"Error scanning delayed tasks for queue {queue}: {e}")
    
    async def _claim_delayed_tasks(self, queue: str, event_queue: asyncio.Queue, prefetch_multiplier: int):
        """处理延迟队列中的到期任务"""
        try:
            # 检查队列大小，如果已满则不处理
            if event_queue.qsize() >= max(prefetch_multiplier // 2, 1):
                return
            
            current_time = time.time()
            delayed_queue_key = f"{self.redis_prefix}:DELAYED_QUEUE:{queue}"
            consumer_name = self.consumer_manager.get_consumer_name(queue)
            prefixed_queue = self.get_prefixed_queue_name(queue)
            
            # 计算需要获取的任务数量
            count_to_claim = max(1, prefetch_multiplier - event_queue.qsize())
            
            # Lua脚本：原子性地获取到期任务、认领、删除成功认领的任务
            lua_script = """
            local delayed_queue_key = KEYS[1]
            local stream_key = KEYS[2]
            local group_name = KEYS[3]
            local consumer_name = ARGV[1]
            local current_time = ARGV[2]
            local limit = ARGV[3]
            
            -- 获取到期的任务ID（这些是Stream消息ID）
            local expired_tasks = redis.call('ZRANGEBYSCORE', delayed_queue_key, 0, current_time, 'LIMIT', 0, limit)
            
            if #expired_tasks == 0 then
                return {}
            end
            
            local successfully_claimed = {}
            local claimed_messages = {}
            
            -- 尝试认领每个任务
            for i, task_id in ipairs(expired_tasks) do
                -- 先检查消息的pending信息
                local pending_info = redis.call('XPENDING', stream_key, group_name, task_id, task_id, 1)
                
                if #pending_info > 0 then
                    -- pending_info[1] 格式: {id, consumer, idle_time, delivery_count}
                    local idle_time = pending_info[1][3]
                    
                    -- 只认领空闲时间超过1秒的消息（避免认领刚被读取的消息）
                    if idle_time > 1000 then
                        -- 使用XCLAIM认领消息
                        local claim_result = redis.call('XCLAIM', stream_key, group_name, consumer_name, 0, task_id)
                        
                        if #claim_result > 0 then
                            -- 认领成功，记录任务ID
                            table.insert(successfully_claimed, task_id)
                            -- 保存认领到的消息内容
                            for j, msg in ipairs(claim_result) do
                                table.insert(claimed_messages, msg)
                            end
                        end
                    end
                else
                    -- 消息不在pending列表中，可能还没被读取，跳过
                    -- 但保留在ZSET中，等待正常读取
                end
            end
            
            -- 只删除成功认领的任务
            if #successfully_claimed > 0 then
                redis.call('ZREM', delayed_queue_key, unpack(successfully_claimed))
            end
            
            -- 返回认领到的消息
            return claimed_messages
            """
            
            # 注册Lua脚本（如果还没有注册）
            if not hasattr(self, '_atomic_claim_script'):
                self._atomic_claim_script = self.async_redis_client.register_script(lua_script)
            
            # 执行Lua脚本
            try:
                claimed_messages = await self._atomic_claim_script(
                    keys=[delayed_queue_key, prefixed_queue, prefixed_queue],
                    args=[consumer_name, str(current_time), str(count_to_claim)]
                )
                
                if not claimed_messages:
                    return
                    
                # claimed_messages 是嵌套列表，每个元素是 [msg_id, msg_data_fields]
                # 其中 msg_data_fields 是扁平的键值对列表
                for claimed_message in claimed_messages:
                    if isinstance(claimed_message, list) and len(claimed_message) >= 2:
                        msg_id = claimed_message[0]
                        msg_data_fields = claimed_message[1]
                        
                        # 解析消息数据
                        msg_data = {}
                        if isinstance(msg_data_fields, list):
                            for j in range(0, len(msg_data_fields), 2):
                                if j + 1 < len(msg_data_fields):
                                    key = msg_data_fields[j]
                                    value = msg_data_fields[j + 1]
                                    # 保持bytes格式以匹配正常消息处理
                                    if isinstance(key, str):
                                        key = key.encode()
                                    if isinstance(value, str):
                                        value = value.encode()
                                    msg_data[key] = value
                        
                        # 清除延迟标记
                        if b'data' in msg_data:
                            data_field = msg_data.get(b'data')
                            if data_field:
                                try:
                                    # 直接解析二进制数据
                                    parsed_data = loads_str(data_field)
                                    # 清除延迟标记，避免再次被延迟
                                    parsed_data['is_delayed'] = 0
                                    # dumps_str 现在直接返回二进制
                                    updated_data = dumps_str(parsed_data)
                                    msg_data[b'data'] = updated_data
                                except:
                                    pass
                        
                        # 处理消息
                        result = self._process_message_common(
                            msg_id, msg_data, queue, event_queue,
                            is_async=True, consumer_name=consumer_name
                        )
                        if isinstance(result, tuple) and result[0] == 'async_put':
                            await self._async_put_task(event_queue, result[1])
                        
                        logger.info(f"Claimed and processed delayed task {msg_id} from queue {queue}")
                
                logger.info(f"Processed {len(claimed_messages)} delayed tasks for queue {queue}")
                
            except Exception as e:
                logger.error(f"Error executing atomic claim script: {e}")
                    
        except Exception as e:
            logger.error(f"Error processing delayed tasks for queue {queue}: {e}")
            # 错误不应该阻塞主流程
    def read_pending(self, groupname: str, queue: str, asyncio: bool = False):
        # 使用二进制客户端进行Stream操作
        client = self.get_redis_client(asyncio, binary=True)
        prefixed_queue = self.get_prefixed_queue_name(queue)
        prefixed_queue_bytes = prefixed_queue.encode() if isinstance(prefixed_queue, str) else prefixed_queue
        groupname_bytes = groupname.encode() if isinstance(groupname, str) else groupname
        return client.xpending(prefixed_queue_bytes, groupname_bytes)

    def ack(self, queue, event_id, asyncio: bool = False):
        # 使用二进制客户端进行Stream操作
        client = self.get_redis_client(asyncio, binary=True)
        prefixed_queue = self.get_prefixed_queue_name(queue)
        prefixed_queue_bytes = prefixed_queue.encode() if isinstance(prefixed_queue, str) else prefixed_queue
        event_id_bytes = event_id if isinstance(event_id, bytes) else event_id.encode() if isinstance(event_id, str) else str(event_id).encode()
        result = client.xack(prefixed_queue_bytes, prefixed_queue_bytes, event_id_bytes)
        # 清理已认领的消息ID
        if event_id in self._claimed_message_ids:
            self._claimed_message_ids.remove(event_id)
        return result
    
    def _recreate_redis_connection(self):
        """重新创建Redis连接"""
        try:
            logger.info("开始重新创建Redis连接...")
            
            # 关闭现有连接
            if hasattr(self.redis_client, 'connection_pool'):
                try:
                    self.redis_client.connection_pool.disconnect()
                except:
                    pass
            
            if hasattr(self.async_redis_client, 'connection_pool'):
                try:
                    self.async_redis_client.connection_pool.disconnect()
                except:
                    pass
            
            # 重新创建连接池和客户端
            from ..core.app import get_redis_pool, get_async_redis_pool, get_binary_redis_pool, get_async_binary_redis_pool
            import redis
            from redis import asyncio as aioredis
            
            redis_url = self._redis_url
            
            # 重新创建同步连接
            pool = get_redis_pool(redis_url)
            new_redis_client = redis.StrictRedis(connection_pool=pool)
            
            # 重新创建异步连接
            async_pool = get_async_redis_pool(redis_url)
            new_async_redis_client = aioredis.StrictRedis(connection_pool=async_pool)
            
            # 重新创建二进制连接
            binary_pool = get_binary_redis_pool(redis_url)
            new_binary_redis_client = redis.StrictRedis(connection_pool=binary_pool)
            
            async_binary_pool = get_async_binary_redis_pool(redis_url)
            new_async_binary_redis_client = aioredis.StrictRedis(connection_pool=async_binary_pool)
            
            # 测试新连接
            new_redis_client.ping()
            
            # 更新连接
            self.redis_client = new_redis_client
            self.async_redis_client = new_async_redis_client
            self.binary_redis_client = new_binary_redis_client
            self.async_binary_redis_client = new_async_binary_redis_client
            
            logger.info("Redis连接已成功重新创建")
            
        except Exception as e:
            logger.error(f"重新创建Redis连接失败: {e}")
            # 如果重新创建失败，尝试重置连接池
            try:
                if hasattr(self.redis_client, 'connection_pool'):
                    self.redis_client.connection_pool.reset()
                if hasattr(self.async_redis_client, 'connection_pool'):
                    self.async_redis_client.connection_pool.reset()
                logger.info("已重置现有连接池")
            except Exception as reset_error:
                logger.error(f"重置连接池失败: {reset_error}")
                
    def _safe_redis_operation(self, operation, *args, max_retries=3, **kwargs):
        """安全的Redis操作，带有重试机制"""
        for attempt in range(max_retries):
            try:
                return operation(*args, **kwargs)
            except (redis.exceptions.TimeoutError, redis.exceptions.ConnectionError) as e:
                if attempt == max_retries - 1:
                    logger.error(f"Redis操作失败，已重试{max_retries}次: {e}")
                    raise
                
                logger.warning(f"Redis操作失败，第{attempt + 1}次重试: {e}")
                if attempt == 0:  # 第一次失败时重新创建连接
                    self._recreate_redis_connection()
                time.sleep(min(2 ** attempt, 5))  # 指数退避，最多5秒
    
    def cleanup(self):
        """清理EventPool资源"""
        # 立即设置停止标志，阻止后台任务继续处理
        self._stop_reading = True
        
        # 只有在有实际资源需要清理时才打印日志
        has_active_resources = False
        
        # 检查是否有活跃的消费者管理器
        if hasattr(self, 'consumer_manager') and self.consumer_manager:
            # 检查消费者管理器是否真的有活动
            if hasattr(self.consumer_manager, '_heartbeat_strategy'):
                strategy = self.consumer_manager._heartbeat_strategy
                if strategy and hasattr(strategy, 'consumer_id') and strategy.consumer_id:
                    has_active_resources = True
        
        if has_active_resources:
            logger.info("Cleaning up EventPool resources...")
            self.consumer_manager.cleanup()
            logger.info("EventPool cleanup completed")
        else:
            # 静默清理
            if hasattr(self, 'consumer_manager') and self.consumer_manager:
                self.consumer_manager.cleanup()
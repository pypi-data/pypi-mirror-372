-- 清理废弃的表和相关对象

-- 1. 删除触发器（如果存在）
DROP TRIGGER IF EXISTS update_queue_stats_trigger ON tasks;

-- 2. 删除触发器函数（如果存在）
DROP FUNCTION IF EXISTS update_queue_stats();

-- 3. 删除废弃的表
DROP TABLE IF EXISTS queue_stats CASCADE;
DROP TABLE IF EXISTS workers CASCADE;

-- 4. 清理说明
-- 这些表已经不再使用：
-- - queue_stats: 队列统计信息现在通过 Redis 或其他方式管理
-- - workers: Worker 信息通过 Redis 的心跳机制管理
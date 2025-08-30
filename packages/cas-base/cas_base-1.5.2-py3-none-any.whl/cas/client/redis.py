import redis.asyncio as redis
from redis.exceptions import RedisError, ConnectionError, TimeoutError
from ..base.logger import logger


class RedisClient:
    def __init__(self, host="localhost", port=6379, db=0, password=None, pool_size=10, timeout=5):
        """初始化 Redis 客户端，使用连接池"""
        try:
            self.pool = redis.ConnectionPool(
                host=host, port=port, db=db, password=password, decode_responses=True, max_connections=pool_size, socket_timeout=timeout
            )
            self.ins = redis.Redis(connection_pool=self.pool)
            logger.debug("成功创建 Redis 连接池")
        except (ConnectionError, RedisError) as e:
            logger.exception(f"初始化 Redis 连接池失败: {e}")

    async def set(self, key: str, value, expire=7 * 24 * 60 * 60):
        """设置键值对，默认过期时间为 7 天"""
        try:
            await self.ins.set(key, value, ex=expire)
            logger.debug(f"成功设置键 {key}，值为: {value}，过期时间: {expire} 秒")
        except (TimeoutError, RedisError) as e:
            logger.exception(f"设置键 {key} 失败: {e}")

    async def get(self, key: str):
        """获取键的值，带异常处理"""
        try:
            value = await self.ins.get(key)
            logger.debug(f"成功获取键 {key}，值为: {value}")
            return value
        except (TimeoutError, RedisError) as e:
            logger.exception(f"获取键 {key} 失败: {e}")
            return None

    async def exists(self, key: str):
        """检查键是否存在"""
        try:
            exists = await self.ins.exists(key)
            logger.debug(f"键 {key} 存在: {bool(exists)}")
            return bool(exists)
        except (TimeoutError, RedisError) as e:
            logger.exception(f"检查键 {key} 是否存在失败: {e}")
            return False

    async def execute_command(self, *args):
        """执行自定义 Redis 命令"""
        try:
            result = await self.ins.execute_command(*args)
            logger.debug(f"执行命令 {' '.join(map(str, args))}，结果: {result}")
            return result
        except (RedisError, TimeoutError) as e:
            logger.exception(f"执行命令 {' '.join(map(str, args))} 失败: {e}")
            return None

    async def queue_len(self, queue_name: str):
        """判断一个队列还有多少数据"""
        try:
            length = await self.execute_command("LLEN", queue_name)
            logger.debug(f"队列 {queue_name} 中的数据量: {length}")
            return length
        except (RedisError, TimeoutError) as e:
            logger.exception(f"获取队列 {queue_name} 数据量失败: {e}")
            return None

    async def rpush(self, queue_name: str, *values):
        """将元素加入队列右端，带异常处理"""
        try:
            result = await self.ins.rpush(queue_name, *values)
            logger.debug(f"成功将元素 {values} 加入队列 {queue_name} 的右端")
            return result
        except (RedisError, TimeoutError) as e:
            logger.exception(f"将元素 {values} 加入队列 {queue_name} 失败: {e}")

    async def lpush(self, queue_name: str, *values):
        """将任务推入队列（左侧），带异常处理"""
        try:
            await self.ins.lpush(queue_name, *values)
            logger.debug(f"成功将元素 {values} 加入队列 {queue_name} 的左端")
        except (TimeoutError, RedisError) as e:
            logger.exception(f"将元素 {values} 加入队列 {queue_name} 失败: {e}")

    async def rpop(self, queue_name: str, count: int = None):
        """从队列右侧弹出任务，带异常处理"""
        try:
            task = await self.ins.rpop(queue_name, count)
            logger.debug(f"成功从队列 {queue_name} 弹出任务: {task}")
            return task
        except (TimeoutError, RedisError) as e:
            logger.exception(f"弹出队列 {queue_name} 失败: {e}")
            return None

    async def lpop(self, queue_name: str, count: int = None):
        """从队列左侧弹出任务，带异常处理"""
        try:
            task = await self.ins.lpop(queue_name, count)
            logger.debug(f"成功从队列 {queue_name} 弹出任务: {task}")
            return task
        except (TimeoutError, RedisError) as e:
            logger.exception(f"弹出队列 {queue_name} 失败: {e}")
            return None

    async def brpop(self, queue_name: str, timeout: int = 0):
        """阻塞式弹出任务"""
        try:
            task = await self.ins.brpop(queue_name, timeout=timeout)
            if task:
                logger.debug(f"成功阻塞式弹出队列 {queue_name} 的任务: {task[1]}")
                return task[1]
            else:
                logger.debug(f"队列 {queue_name} 在 {timeout} 秒内没有任务")
                return None
        except (TimeoutError, RedisError) as e:
            logger.exception(f"阻塞式弹出队列 {queue_name} 失败: {e}")
            return None

    async def blpop(self, queue_name: str, timeout: int = 0):
        """阻塞式弹出任务"""
        try:
            task = await self.ins.blpop(queue_name, timeout=timeout)
            if task:
                logger.debug(f"成功阻塞式弹出队列 {queue_name} 的任务: {task[1]}")
                return task[1]
            else:
                logger.debug(f"队列 {queue_name} 在 {timeout} 秒内没有任务")
                return None
        except (TimeoutError, RedisError) as e:
            logger.exception(f"阻塞式弹出队列 {queue_name} 失败: {e}")
            return None

    async def subscribe(self, channel_name: str, callback):
        """订阅频道，带异常处理"""
        try:
            pubsub = self.ins.pubsub()
            await pubsub.subscribe(channel_name)
            logger.debug(f"成功订阅频道 {channel_name}")

            async for message in pubsub.listen():
                if message["type"] == "message":
                    logger.debug(f"收到频道 {channel_name} 的消息: {message['data']}")
                    await callback(message["data"])
        except (ConnectionError, RedisError) as e:
            logger.exception(f"订阅频道 {channel_name} 失败: {e}")

    async def publish(self, channel_name: str, message):
        """发布消息到频道，带异常处理"""
        try:
            await self.ins.publish(channel_name, message)
            logger.debug(f"成功向频道 {channel_name} 发布消息: {message}")
        except (TimeoutError, RedisError) as e:
            logger.exception(f"发布消息到频道 {channel_name} 失败: {e}")

    async def close(self):
        """关闭连接池"""
        try:
            await self.ins.close()
            logger.debug("Redis 连接已关闭")
        except (ConnectionError, RedisError) as e:
            logger.exception(f"关闭 Redis 连接失败: {e}")

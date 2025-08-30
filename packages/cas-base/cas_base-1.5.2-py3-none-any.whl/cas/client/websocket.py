import json
import asyncio
import websockets
import websockets.client
import websockets.connection
import websockets.exceptions
from ..base.logger import logger


class WebSocketClient:
    def __init__(self, base_url: str, name: str = "WebSocket"):
        self.name: str = name
        self.base_url: str = base_url
        self.path: str | None = None
        self.max_retries = 259200  # 最大重试次数 259200*15秒=3天
        self.retry_delay = 15  # 重试延迟（秒）
        self.retry_count = 0  # 当前重试次数
        self.is_connected = False  # 是否已连接
        self.stop_event = asyncio.Event()  # 用于停止
        self.events = {}  # 事件注册

    def register_event(self, event_name, callback):
        """注册事件"""
        self.events[event_name] = callback

    async def trigger_event(self, event_name, *args, **kwargs):
        """触发事件"""
        if event_name in self.events:
            await self.events[event_name](*args, **kwargs)

    async def send_message(self, message):
        """异步发送消息到服务器"""
        try:
            if self.is_connected:
                if isinstance(message, dict):
                    message = json.dumps(message, ensure_ascii=False)
                if self.ins.state == websockets.connection.State.OPEN:
                    logger.debug(f"[{self.name}]send_message:\n{message}")
                    await self.ins.send(message)
        except Exception as e:
            logger.exception(e)

    async def listen(self):
        """监听服务器消息"""
        try:
            async for message in self.ins:
                try:
                    logger.debug(f"[{self.name}]rev_message:\n{message}")
                    await self.trigger_event("on_message", self, message)
                except Exception as e:
                    logger.exception(e)
        except websockets.exceptions.ConnectionClosedError as e:
            logger.info(f"[{self.name}]连接错误: {e}")
            self.is_connected = False
        except websockets.exceptions.ConnectionClosed as e:
            logger.info(f"[{self.name}]连接关闭: {e}")
            self.is_connected = False

    async def try_connect(self):
        """连接 WebSocket 服务器"""
        try:
            logger.info(f"[{self.name}]连接中... 第 {self.retry_count} 次")
            self.ins = await websockets.client.connect(f"{self.base_url}/?{self.path}")
            self.is_connected = True
            self.retry_count = 0
            logger.info(f"[{self.name}]连接成功")
            await self.trigger_event("on_connect", self)  # 触发连接成功事件
            await self.listen()  # 开始监听服务器消息
        except Exception as e:
            logger.info(f"[{self.name}]连接失败: {e}")
            self.is_connected = False

    async def connect(self):
        """主事件循环，负责处理重连逻辑"""
        while not self.stop_event.is_set():
            if not self.is_connected:
                if self.retry_count < self.max_retries:
                    self.retry_count += 1
                    await self.try_connect()  # 尝试连接
                    if not self.is_connected:
                        await asyncio.sleep(self.retry_delay)  # 如果连接失败，等待一段时间再重试
                else:
                    logger.info(f"[{self.name}]重试次数已达最大值，放弃连接")
                    await self.trigger_event("on_disconnect", self)
                    self.stop()  # 停止事件，终止程序
            await asyncio.sleep(1)  # 等待一秒后继续循环
        logger.info(f"[{self.name}]客户端已停止")

    async def stop(self):
        """停止 WebSocket 客户端"""
        self.stop_event.set()  # 触发停止事件
        if self.is_connected:
            await self.ins.close()  # 关闭连接

    async def start(self, path: str):
        self.path = path
        self.stop_event.clear()
        asyncio.create_task(self.connect())

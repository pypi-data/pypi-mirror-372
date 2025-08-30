from functools import wraps
from typing import Callable
from .logger import logger


class MessageManager:
    _message_handlers = {}

    @classmethod
    def register(cls, handler_name: str):
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(ctx, **kwargs):
                try:
                    await func(ctx, **kwargs)
                except Exception as e:
                    logger.exception(e)

            cls._message_handlers[handler_name] = wrapper
            return wrapper

        return decorator

    @classmethod
    async def handle(cls, ctx, message: dict):
        try:
            cmd = message.get("cmd")
            message_handler = cls._message_handlers.get(cmd)
            if not message_handler:
                logger.warning(f"message_handler {cmd} 不存在")
                return
            args = message.get("args", {})
            await message_handler(ctx, **args)
        except Exception as e:
            logger.exception(e)

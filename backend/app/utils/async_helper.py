"""
异步辅助工具
"""
import asyncio
import logging

logger = logging.getLogger(__name__)


def run_async(coro):
    """
    在同步上下文中运行异步函数

    Args:
        coro: 协程对象

    Returns:
        协程的返回值
    """
    try:
        # 尝试获取现有事件循环
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # 如果循环正在运行，创建新循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except RuntimeError:
        # 没有事件循环，创建新的
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        return loop.run_until_complete(coro)
    finally:
        # 确保循环被正确关闭
        if not loop.is_closed():
            loop.close()

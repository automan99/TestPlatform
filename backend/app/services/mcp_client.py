"""
MCP 客户端连接管理
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any, List, AsyncIterator

try:
    from exceptiongroup import ExceptionGroup
except ImportError:
    ExceptionGroup = BaseException

from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession

logger = logging.getLogger(__name__)


class MCPClientError(Exception):
    """MCP 客户端错误"""
    pass


class MCPConnectionError(MCPClientError):
    """MCP 连接错误"""
    pass


class MCPTimeoutError(MCPClientError):
    """MCP 超时错误"""
    pass


class MCPClientManager:
    """MCP 客户端管理器"""

    def __init__(self, timeout: float = 30.0):
        """
        初始化 MCP 客户端管理器

        Args:
            timeout: 默认超时时间（秒）
        """
        self.timeout = timeout
        self._connections: Dict[int, Any] = {}  # 连接缓存

    @asynccontextmanager
    async def get_session(
        self,
        transport_type: str,
        command: Optional[str] = None,
        args: Optional[List[str]] = None,
        env: Optional[Dict[str, str]] = None,
        url: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> AsyncIterator[ClientSession]:
        """
        获取 MCP 会话（上下文管理器）

        Args:
            transport_type: 传输类型 (stdio, sse)
            command: 执行命令 (stdio 类型)
            args: 命令参数 (stdio 类型)
            env: 环境变量 (stdio 类型)
            url: SSE/HTTP URL (sse 类型)
            headers: HTTP 请求头 (sse 类型)

        Yields:
            ClientSession 实例

        Raises:
            MCPConnectionError: 连接失败
        """
        if transport_type == 'stdio':
            logger.info(f"创建 stdio MCP 会话: command={command}, args={args}")

            server_params = StdioServerParameters(
                command=command,
                args=args or [],
                env=env
            )

            # stdio_client 和 ClientSession 都是异步上下文管理器
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # 初始化会话
                    await session.initialize()
                    logger.info("MCP 会话初始化成功")
                    yield session

        elif transport_type == 'sse':
            logger.info(f"创建 SSE MCP 会话: url={url}, headers={headers}")

            try:
                # sse_client 和 ClientSession 都是异步上下文管理器
                async with sse_client(
                    url=url,
                    headers=headers or {},
                    timeout=self.timeout
                ) as (read, write):
                    async with ClientSession(read, write) as session:
                        # 初始化会话
                        await session.initialize()
                        logger.info("SSE MCP 会话初始化成功")
                        yield session
            except ExceptionGroup as e:
                # SSE 连接可能因为各种原因失败（服务器不可用、URL错误等）
                logger.error(f"SSE 连接失败 (ExceptionGroup): {e}")
                # 提取实际的异常原因
                if e.exceptions:
                    actual_error = e.exceptions[0]
                    error_str = str(actual_error)
                    # 提供更友好的错误信息
                    if '400' in error_str or 'Bad Request' in error_str:
                        raise MCPConnectionError(
                            f"SSE连接失败: 服务器返回400错误。请确认URL是有效的MCP SSE端点。当前URL: {url}"
                        ) from actual_error
                    elif '404' in error_str or 'Not Found' in error_str:
                        raise MCPConnectionError(
                            f"SSE连接失败: 端点不存在 (404)。请检查URL是否正确。当前URL: {url}"
                        ) from actual_error
                    elif 'Connection' in error_str or 'refused' in error_str:
                        raise MCPConnectionError(
                            f"SSE连接失败: 无法连接到服务器。请确认服务器正在运行。当前URL: {url}"
                        ) from actual_error
                    else:
                        raise MCPConnectionError(f"SSE连接失败: {error_str}") from actual_error
                raise MCPConnectionError(f"SSE连接失败: {str(e)}") from e
            except asyncio.TimeoutError:
                logger.error(f"SSE 连接超时 ({self.timeout}秒)")
                raise MCPTimeoutError(
                    f"SSE连接超时 ({self.timeout}秒)。请确认服务器正在运行且URL正确: {url}"
                )
            except Exception as e:
                logger.error(f"SSE 连接错误: {e}", exc_info=True)
                error_str = str(e)
                if '400' in error_str or 'Bad Request' in error_str:
                    raise MCPConnectionError(
                        f"SSE连接失败: 服务器返回400错误。URL可能不是有效的MCP SSE端点。当前URL: {url}"
                    ) from e
                raise MCPConnectionError(f"SSE连接错误: {error_str}") from e

        else:
            raise MCPConnectionError(
                f"不支持的传输类型: {transport_type}"
            )


# 全局单例
_mcp_client_manager = None


def get_mcp_client_manager(timeout: float = 30.0) -> MCPClientManager:
    """
    获取 MCP 客户端管理器单例

    Args:
        timeout: 超时时间

    Returns:
        MCPClientManager 实例
    """
    global _mcp_client_manager
    if _mcp_client_manager is None:
        _mcp_client_manager = MCPClientManager(timeout=timeout)
    return _mcp_client_manager

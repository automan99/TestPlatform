"""
MCP 操作封装
"""
import asyncio
import json
import logging
from typing import Dict, Any, List, Optional

try:
    from exceptiongroup import ExceptionGroup
except ImportError:
    ExceptionGroup = BaseException

from app.services.mcp_client import (
    get_mcp_client_manager,
    MCPConnectionError,
    MCPTimeoutError,
    MCPClientError
)
from app.utils.async_helper import run_async

logger = logging.getLogger(__name__)


class MCPOperations:
    """MCP 操作类"""

    def __init__(self, mcp_server):
        """
        初始化 MCP 操作

        Args:
            mcp_server: MCPServer 模型实例
        """
        self.mcp_server = mcp_server
        self.manager = get_mcp_client_manager(timeout=mcp_server.timeout)

    def _prepare_connection_params(self) -> Dict[str, Any]:
        """准备连接参数"""
        params = {
            'transport_type': self.mcp_server.transport_type
        }

        if self.mcp_server.transport_type == 'stdio':
            params['command'] = self.mcp_server.command
            params['args'] = json.loads(self.mcp_server.arguments) if self.mcp_server.arguments else []
            params['env'] = json.loads(self.mcp_server.env) if self.mcp_server.env else None
        elif self.mcp_server.transport_type == 'sse':
            params['url'] = self.mcp_server.url
            # SSE 需要设置正确的 Accept 头
            params['headers'] = {'Accept': 'text/event-stream'}

        return params

    async def _list_tools_async(self) -> List[Dict[str, Any]]:
        """异步获取工具列表"""
        params = self._prepare_connection_params()

        try:
            async with self.manager.get_session(**params) as session:
                tools_response = await session.list_tools()

                logger.info(f"tools_response 类型: {type(tools_response)}")

                tools = []

                # 处理不同的响应格式
                if hasattr(tools_response, 'tools'):
                    tool_list = tools_response.tools
                elif isinstance(tools_response, list):
                    tool_list = tools_response
                else:
                    logger.warning(f"未知的响应格式: {type(tools_response)}")
                    return []

                logger.info(f"tool_list 长度: {len(tool_list) if hasattr(tool_list, '__len__') else 'N/A'}")

                for tool in tool_list:
                    # 处理 Pydantic 模型
                    if hasattr(tool, 'model_dump'):
                        tool_dict = tool.model_dump()
                    elif hasattr(tool, 'dict'):
                        tool_dict = tool.dict()
                    else:
                        tool_dict = tool

                    tools.append({
                        'name': tool_dict.get('name', ''),
                        'description': tool_dict.get('description', ''),
                        'input_schema': tool_dict.get('inputSchema', tool_dict.get('input_schema', {}))
                    })

                logger.info(f"获取到 {len(tools)} 个工具")
                return tools
        except asyncio.TimeoutError:
            logger.error(f"获取工具列表超时")
            raise MCPTimeoutError("操作超时")
        except Exception as e:
            logger.error(f"获取工具列表失败: {e}", exc_info=True)
            raise MCPClientError(f"获取工具列表失败: {str(e)}")

    def list_tools(self) -> List[Dict[str, Any]]:
        """
        获取 MCP 工具列表

        Returns:
            工具列表

        Raises:
            MCPConnectionError: 连接失败
            MCPTimeoutError: 超时
        """
        return run_async(self._list_tools_async())

    async def _call_tool_async(
        self,
        tool_name: str,
        arguments: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """异步调用工具"""
        params = self._prepare_connection_params()

        async with self.manager.get_session(**params) as session:
            result = await session.call_tool(tool_name, arguments or {})

            # 处理返回结果
            response = {
                'tool_name': tool_name,
                'success': True,
                'result': None,
                'error': None,
                'content': []
            }

            if hasattr(result, 'content'):
                for content in result.content:
                    if hasattr(content, 'text'):
                        response['content'].append({
                            'type': 'text',
                            'text': content.text
                        })
                    elif hasattr(content, 'data'):
                        response['content'].append({
                            'type': 'resource',
                            'data': content.data
                        })

            return response

    def call_tool(
        self,
        tool_name: str,
        arguments: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        调用 MCP 工具

        Args:
            tool_name: 工具名称
            arguments: 工具参数

        Returns:
            执行结果

        Raises:
            MCPConnectionError: 连接失败
            MCPTimeoutError: 超时
        """
        return run_async(
            self._call_tool_async(tool_name, arguments)
        )

    async def _list_resources_async(self) -> List[Dict[str, Any]]:
        """异步获取资源列表"""
        params = self._prepare_connection_params()

        try:
            async with self.manager.get_session(**params) as session:
                resources_response = await session.list_resources()

                logger.info(f"resources_response 类型: {type(resources_response)}")

                resources = []

                # 处理不同的响应格式
                if hasattr(resources_response, 'resources'):
                    resource_list = resources_response.resources
                elif isinstance(resources_response, list):
                    resource_list = resources_response
                else:
                    logger.warning(f"未知的响应格式: {type(resources_response)}")
                    return []

                for resource in resource_list:
                    # 处理 Pydantic 模型
                    if hasattr(resource, 'model_dump'):
                        resource_dict = resource.model_dump()
                    elif hasattr(resource, 'dict'):
                        resource_dict = resource.dict()
                    else:
                        resource_dict = resource

                    resources.append({
                        'uri': resource_dict.get('uri', ''),
                        'name': resource_dict.get('name', ''),
                        'description': resource_dict.get('description', ''),
                        'mime_type': resource_dict.get('mimeType', resource_dict.get('mime_type'))
                    })

                logger.info(f"获取到 {len(resources)} 个资源")
                return resources
        except ExceptionGroup as e:
            # 处理 TaskGroup 错误 - 可能是服务器不支持 resources
            logger.warning(f"MCP Server 可能不支持 resources: {e}")
            return []
        except Exception as e:
            logger.error(f"获取资源列表失败: {e}", exc_info=True)
            raise MCPClientError(f"获取资源列表失败: {str(e)}")

    def list_resources(self) -> List[Dict[str, Any]]:
        """
        获取 MCP 资源列表

        Returns:
            资源列表

        Raises:
            MCPConnectionError: 连接失败
            MCPTimeoutError: 超时
        """
        return run_async(self._list_resources_async())

    async def _read_resource_async(self, resource_uri: str) -> Dict[str, Any]:
        """异步读取资源内容"""
        params = self._prepare_connection_params()

        try:
            async with self.manager.get_session(**params) as session:
                result = await session.read_resource(resource_uri)

                response = {
                    'uri': resource_uri,
                    'success': True,
                    'content': []
                }

                for content in result.contents:
                    if hasattr(content, 'text'):
                        response['content'].append({
                            'type': 'text',
                            'text': content.text,
                            'mime_type': content.mimeType if hasattr(content, 'mimeType') else None
                        })
                    elif hasattr(content, 'blob'):
                        response['content'].append({
                            'type': 'blob',
                            'data': content.blob,
                            'mime_type': content.mimeType if hasattr(content, 'mimeType') else None
                        })

                return response
        except ExceptionGroup as e:
            # 处理 TaskGroup 错误 - 可能是服务器不支持 resources
            logger.warning(f"MCP Server 可能不支持 resources: {e}")
            return {
                'uri': resource_uri,
                'success': False,
                'error': 'Server does not support resources',
                'content': []
            }
        except Exception as e:
            logger.error(f"读取资源失败: {e}", exc_info=True)
            raise MCPClientError(f"读取资源失败: {str(e)}")

    def read_resource(self, resource_uri: str) -> Dict[str, Any]:
        """
        读取 MCP 资源内容

        Args:
            resource_uri: 资源 URI

        Returns:
            资源内容

        Raises:
            MCPConnectionError: 连接失败
            MCPTimeoutError: 超时
        """
        return run_async(self._read_resource_async(resource_uri))

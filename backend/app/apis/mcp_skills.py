"""
MCP/Skills管理API
"""
from flask import request, current_app
from flask_restx import Namespace, Resource, fields
from app import db
from app.models import MCPServer, MCPTool, MCPResource, Skill
from app.utils import success_response, error_response
from app.services.mcp_operations import MCPOperations
from app.services.mcp_client import MCPConnectionError, MCPTimeoutError, MCPClientError
from app.services.mcp_process_manager import get_mcp_process_manager
import json
import subprocess
from datetime import datetime
import traceback

# 命名空间
mcp_server_ns = Namespace('MCPServers', description='MCP Server管理')
skill_ns = Namespace('Skills', description='Skill管理')

# Swagger模型定义
mcp_server_model = mcp_server_ns.model('MCPServer', {
    'name': fields.String(required=True, description='MCP名称'),
    'code': fields.String(description='MCP编码'),
    'transport_type': fields.String(description='传输类型'),
    'command': fields.String(description='执行命令'),
    'arguments': fields.String(description='参数(JSON数组)'),
    'env': fields.String(description='环境变量(JSON对象)'),
    'url': fields.String(description='URL(SSE/HTTP)'),
    'timeout': fields.Integer(description='超时时间'),
    'status': fields.String(description='状态'),
    'is_enabled': fields.Boolean(description='是否启用'),
    'is_builtin': fields.Boolean(description='是否内置'),
    'tags': fields.String(description='标签')
})

skill_model = skill_ns.model('Skill', {
    'name': fields.String(required=True, description='Skill名称'),
    'code': fields.String(description='Skill编码'),
    'description': fields.String(description='描述'),
    'mcp_id': fields.Integer(description='关联MCP ID'),
    'script_content': fields.String(description='脚本内容'),
    'script_type': fields.String(description='脚本类型'),
    'params_schema': fields.String(description='参数结构(JSON)'),
    'params_example': fields.String(description='参数示例(JSON)'),
    'timeout': fields.Integer(description='超时时间'),
    'log_enabled': fields.Boolean(description='是否启用日志'),
    'retry_count': fields.Integer(description='重试次数'),
    'allowed_roles': fields.String(description='允许角色(JSON)'),
    'version': fields.String(description='版本'),
    'tags': fields.String(description='标签'),
    'status': fields.String(description='状态'),
    'is_enabled': fields.Boolean(description='是否启用')
})


# ============== 辅助函数 ==============

def _handle_mcp_status_change(mcp_server, old_is_enabled, new_is_enabled):
    """
    处理 MCP Server 状态变化，启动/停止进程

    Args:
        mcp_server: MCPServer 实例
        old_is_enabled: 旧的启用状态
        new_is_enabled: 新的启用状态
    """
    process_manager = get_mcp_process_manager()

    # 从禁用变为启用：启动进程
    if not old_is_enabled and new_is_enabled:
        if mcp_server.transport_type == 'stdio':
            # stdio 类型需要启动常驻进程
            args = json.loads(mcp_server.arguments) if mcp_server.arguments else []
            env = json.loads(mcp_server.env) if mcp_server.env else None

            success = process_manager.start_process(
                mcp_id=mcp_server.id,
                command=mcp_server.command,
                args=args,
                env=env
            )
            if success:
                current_app.logger.info(f"MCP Server {mcp_server.id} ({mcp_server.name}) 进程已启动")
            else:
                current_app.logger.error(f"MCP Server {mcp_server.id} ({mcp_server.name}) 进程启动失败")
        else:
            # SSE 类型不需要进程管理
            current_app.logger.info(f"MCP Server {mcp_server.id} ({mcp_server.name}) 已启用 (SSE)")

    # 从启用变为禁用：停止进程
    elif old_is_enabled and not new_is_enabled:
        if mcp_server.transport_type == 'stdio':
            # stdio 类型需要停止进程
            success = process_manager.stop_process(mcp_server.id)
            if success:
                current_app.logger.info(f"MCP Server {mcp_server.id} ({mcp_server.name}) 进程已停止")
            else:
                current_app.logger.warning(f"MCP Server {mcp_server.id} ({mcp_server.name}) 进程停止失败")
        else:
            # SSE 类型不需要进程管理
            current_app.logger.info(f"MCP Server {mcp_server.id} ({mcp_server.name}) 已禁用 (SSE)")


# ============== MCP Server API ==============

@mcp_server_ns.route('')
class MCPServerListAPI(Resource):
    """MCP Server列表API"""

    def get(self):
        """获取MCP Server列表"""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            keyword = request.args.get('keyword')
            transport_type = request.args.get('transport_type')
            status = request.args.get('status')
            is_enabled = request.args.get('is_enabled')

            query = MCPServer.query.filter_by(is_deleted=False)

            if keyword:
                query = query.filter(MCPServer.name.contains(keyword))
            if transport_type:
                query = query.filter_by(transport_type=transport_type)
            if status:
                query = query.filter_by(status=status)
            if is_enabled is not None:
                is_enabled_bool = is_enabled.lower() == 'true'
                query = query.filter_by(is_enabled=is_enabled_bool)

            pagination = query.order_by(MCPServer.id.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )

            return success_response(data={
                'items': [item.to_dict() for item in pagination.items],
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page
            })
        except Exception as e:
            current_app.logger.error(f'获取MCP Server列表失败: {str(e)}')
            return error_response(message=f'获取MCP Server列表失败: {str(e)}', code=500)

    @mcp_server_ns.expect(mcp_server_model)
    def post(self):
        """创建MCP Server"""
        try:
            data = request.get_json()

            # 检查编码是否已存在
            if data.get('code') and data['code'].strip():
                existing = MCPServer.query.filter_by(code=data['code'].strip(), is_deleted=False).first()
                if existing:
                    return error_response(message='MCP编码已存在', code=400)

            mcp_server = MCPServer(
                name=data.get('name'),
                code=data.get('code') and data['code'].strip() if data.get('code') else None,
                transport_type=data.get('transport_type', 'stdio'),
                command=data.get('command'),
                arguments=json.dumps(data.get('arguments')) if data.get('arguments') else None,
                env=json.dumps(data.get('env')) if data.get('env') else None,
                url=data.get('url'),
                timeout=data.get('timeout', 30),
                status=data.get('status', 'active'),
                is_enabled=data.get('is_enabled', True),
                is_builtin=data.get('is_builtin', False),
                tags=data.get('tags'),
                created_by=data.get('created_by')
            )

            db.session.add(mcp_server)
            db.session.commit()

            return success_response(data=mcp_server.to_dict(), message='创建成功', code=201)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'创建MCP Server失败: {str(e)}')
            return error_response(message=f'创建MCP Server失败: {str(e)}', code=500)


@mcp_server_ns.route('/<int:mcp_id>')
class MCPServerAPI(Resource):
    """MCP Server详情API"""

    def get(self, mcp_id):
        """获取MCP Server详情"""
        try:
            mcp_server = MCPServer.query.filter_by(id=mcp_id, is_deleted=False).first()
            if not mcp_server:
                return error_response(message='MCP Server不存在', code=404)
            return success_response(data=mcp_server.to_dict())
        except Exception as e:
            return error_response(message=f'获取MCP Server失败: {str(e)}', code=500)

    @mcp_server_ns.expect(mcp_server_model)
    def put(self, mcp_id):
        """更新MCP Server"""
        try:
            mcp_server = MCPServer.query.filter_by(id=mcp_id, is_deleted=False).first()
            if not mcp_server:
                return error_response(message='MCP Server不存在', code=404)

            # 获取请求数据
            data = request.get_json() or {}

            # 检查 is_enabled 是否变化
            old_is_enabled = mcp_server.is_enabled
            new_is_enabled = data.get('is_enabled', old_is_enabled)
            is_enabled_changed = 'is_enabled' in data and old_is_enabled != new_is_enabled

            # 内置MCP Server只允许修改启用状态
            if mcp_server.is_builtin:
                # 只允许更新 is_enabled 字段
                if 'is_enabled' in data:
                    mcp_server.is_enabled = data['is_enabled']
                    db.session.commit()

                    # 处理进程启动/停止
                    if is_enabled_changed:
                        _handle_mcp_status_change(mcp_server, old_is_enabled, new_is_enabled)

                    return success_response(data=mcp_server.to_dict(), message='更新成功')
                else:
                    return error_response(message='内置MCP Server只允许修改启用状态', code=400)

            # 检查编码是否已被其他MCP使用
            code_value = data.get('code') and data['code'].strip() if data.get('code') else None
            if code_value and code_value != mcp_server.code:
                existing = MCPServer.query.filter_by(code=code_value, is_deleted=False).first()
                if existing:
                    return error_response(message='MCP编码已存在', code=400)

            mcp_server.name = data.get('name', mcp_server.name)
            mcp_server.code = code_value if code_value is not None else mcp_server.code
            mcp_server.transport_type = data.get('transport_type', mcp_server.transport_type)
            mcp_server.command = data.get('command', mcp_server.command)
            if data.get('arguments') is not None:
                mcp_server.arguments = json.dumps(data['arguments'])
            if data.get('env') is not None:
                mcp_server.env = json.dumps(data['env'])
            mcp_server.url = data.get('url', mcp_server.url)
            mcp_server.timeout = data.get('timeout', mcp_server.timeout)
            mcp_server.status = data.get('status', mcp_server.status)
            mcp_server.is_enabled = new_is_enabled
            mcp_server.is_builtin = data.get('is_builtin', mcp_server.is_builtin)
            mcp_server.tags = data.get('tags', mcp_server.tags)
            mcp_server.updated_by = data.get('updated_by')

            db.session.commit()

            # 处理进程启动/停止
            if is_enabled_changed:
                _handle_mcp_status_change(mcp_server, old_is_enabled, new_is_enabled)

            return success_response(data=mcp_server.to_dict(), message='更新成功')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'更新MCP Server失败: {str(e)}')
            return error_response(message=f'更新MCP Server失败: {str(e)}', code=500)

    def delete(self, mcp_id):
        """删除MCP Server"""
        try:
            mcp_server = MCPServer.query.filter_by(id=mcp_id, is_deleted=False).first()
            if not mcp_server:
                return error_response(message='MCP Server不存在', code=404)

            # 内置MCP Server不允许删除
            if mcp_server.is_builtin:
                return error_response(message='内置MCP Server不允许删除', code=400)

            # 检查是否有关联的Skill
            if mcp_server.skills.filter_by(is_deleted=False).count() > 0:
                return error_response(message='该MCP下有Skill，无法删除', code=400)

            mcp_server.is_deleted = True
            mcp_server.updated_at = datetime.utcnow()
            db.session.commit()
            return success_response(message='删除成功')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'删除MCP Server失败: {str(e)}')
            return error_response(message=f'删除MCP Server失败: {str(e)}', code=500)


@mcp_server_ns.route('/<int:mcp_id>/test')
class MCPServerTestAPI(Resource):
    """测试MCP Server连接"""

    def post(self, mcp_id):
        """测试MCP Server连接"""
        try:
            mcp_server = MCPServer.query.filter_by(id=mcp_id, is_deleted=False).first()
            if not mcp_server:
                return error_response(message='MCP Server不存在', code=404)

            result = {
                'success': False,
                'message': '',
                'output': ''
            }

            # 对于 stdio 类型，先检查进程是否在运行
            if mcp_server.transport_type == 'stdio':
                process_manager = get_mcp_process_manager()
                if not process_manager.is_running(mcp_id):
                    result['message'] = 'MCP Server 进程未运行，请先启用'
                    result['success'] = False
                    return success_response(data=result, message='测试完成')

            # 使用真实的 MCP 连接测试
            operations = MCPOperations(mcp_server)

            try:
                # 尝试获取工具列表来测试连接
                tools = operations.list_tools()
                result['success'] = True
                result['message'] = f'连接成功，获取到 {len(tools)} 个工具'
                result['output'] = f'工具列表: {", ".join([t["name"] for t in tools[:5]])}'

                # 更新状态和使用次数
                mcp_server.last_used_at = datetime.utcnow()
                mcp_server.usage_count += 1
                mcp_server.status = 'active'
                db.session.commit()

            except (MCPConnectionError, MCPTimeoutError) as e:
                result['message'] = f'连接失败: {str(e)}'
                mcp_server.status = 'error'
                db.session.commit()
            except Exception as e:
                result['message'] = f'测试失败: {str(e)}'
                mcp_server.status = 'error'
                db.session.commit()

            return success_response(data=result, message='测试完成')
        except Exception as e:
            current_app.logger.error(f'测试MCP Server失败: {str(e)}')
            return error_response(message=f'测试MCP Server失败: {str(e)}', code=500)


@mcp_server_ns.route('/<int:mcp_id>/tools')
class MCPServerToolsAPI(Resource):
    """获取MCP Server工具列表（从数据库读取）"""

    def get(self, mcp_id):
        """获取MCP Server提供的工具列表"""
        try:
            mcp_server = MCPServer.query.filter_by(id=mcp_id, is_deleted=False).first()
            if not mcp_server:
                return error_response(message='MCP Server不存在', code=404)

            # 从数据库读取工具列表
            tools = MCPTool.query.filter_by(mcp_id=mcp_id).all()

            return success_response(data={
                'tools': [tool.to_dict() for tool in tools],
                'total': len(tools),
                'last_sync_at': mcp_server.last_sync_at.isoformat() if mcp_server.last_sync_at else None
            })

        except Exception as e:
            current_app.logger.error(f'获取MCP Server工具列表失败: {str(e)}\n{traceback.format_exc()}')
            return error_response(message=f'获取工具列表失败: {str(e)}', code=500)


@mcp_server_ns.route('/<int:mcp_id>/sync')
class MCPServerSyncAPI(Resource):
    """同步MCP Server工具和资源"""

    def post(self, mcp_id):
        """同步工具和资源列表到数据库"""
        try:
            mcp_server = MCPServer.query.filter_by(id=mcp_id, is_deleted=False).first()
            if not mcp_server:
                return error_response(message='MCP Server不存在', code=404)

            if not mcp_server.is_enabled:
                return error_response(message='MCP Server已禁用', code=400)

            # 使用真实的 MCP 连接
            operations = MCPOperations(mcp_server)

            result = {
                'tools_synced': 0,
                'resources_synced': 0,
                'tools': [],
                'resources': []
            }

            try:
                # 同步工具列表
                tools = operations.list_tools()

                # 删除旧的工具记录
                MCPTool.query.filter_by(mcp_id=mcp_id).delete()

                # 添加新的工具记录
                for tool_data in tools:
                    tool = MCPTool(
                        mcp_id=mcp_id,
                        name=tool_data.get('name', ''),
                        description=tool_data.get('description', ''),
                        input_schema=json.dumps(tool_data.get('input_schema', {}))
                    )
                    db.session.add(tool)

                result['tools_synced'] = len(tools)
                result['tools'] = tools
                mcp_server.tools_count = len(tools)

            except MCPConnectionError as e:
                current_app.logger.error(f'MCP连接失败: {str(e)}')
                return error_response(message=f'MCP连接失败: {str(e)}', code=503)

            except MCPTimeoutError as e:
                current_app.logger.error(f'MCP连接超时: {str(e)}')
                return error_response(message=f'MCP连接超时: {str(e)}', code=504)

            except MCPClientError as e:
                current_app.logger.error(f'MCP客户端错误: {str(e)}')
                return error_response(message=f'MCP客户端错误: {str(e)}', code=500)

            try:
                # 同步资源列表
                resources = operations.list_resources()

                # 删除旧的资源记录
                MCPResource.query.filter_by(mcp_id=mcp_id).delete()

                # 添加新的资源记录
                for resource_data in resources:
                    resource = MCPResource(
                        mcp_id=mcp_id,
                        uri=resource_data.get('uri', ''),
                        name=resource_data.get('name', ''),
                        description=resource_data.get('description', ''),
                        mime_type=resource_data.get('mime_type', '')
                    )
                    db.session.add(resource)

                result['resources_synced'] = len(resources)
                result['resources'] = resources
                mcp_server.resources_count = len(resources)

            except Exception as e:
                # 资源同步失败不影响工具同步
                current_app.logger.warning(f'MCP资源同步失败: {str(e)}')

            # 更新同步时间
            mcp_server.last_sync_at = datetime.utcnow()
            mcp_server.status = 'active'
            db.session.commit()

            return success_response(data=result, message=f'同步成功: {result["tools_synced"]}个工具, {result["resources_synced"]}个资源')

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'同步MCP Server失败: {str(e)}\n{traceback.format_exc()}')
            return error_response(message=f'同步失败: {str(e)}', code=500)


@mcp_server_ns.route('/<int:mcp_id>/tools/<tool_name>/invoke')
class MCPServerToolInvokeAPI(Resource):
    """调用MCP Server工具"""

    def post(self, mcp_id, tool_name):
        """调用指定的MCP工具"""
        try:
            mcp_server = MCPServer.query.filter_by(id=mcp_id, is_deleted=False).first()
            if not mcp_server:
                return error_response(message='MCP Server不存在', code=404)

            if not mcp_server.is_enabled:
                return error_response(message='MCP Server已禁用', code=400)

            data = request.get_json()
            params = data.get('params', {})

            # 使用真实的 MCP 连接
            operations = MCPOperations(mcp_server)

            try:
                result = operations.call_tool(tool_name, params)

                # 更新使用统计
                mcp_server.usage_count += 1
                mcp_server.last_used_at = datetime.utcnow()
                mcp_server.status = 'active'
                db.session.commit()

                return success_response(data=result, message='调用成功')

            except MCPConnectionError as e:
                mcp_server.status = 'error'
                db.session.commit()
                current_app.logger.error(f'MCP连接失败: {str(e)}')
                return error_response(message=f'MCP连接失败: {str(e)}', code=503)

            except MCPTimeoutError as e:
                mcp_server.status = 'error'
                db.session.commit()
                current_app.logger.error(f'MCP连接超时: {str(e)}')
                return error_response(message=f'MCP连接超时: {str(e)}', code=504)

            except MCPClientError as e:
                current_app.logger.error(f'MCP客户端错误: {str(e)}')
                return error_response(message=f'MCP客户端错误: {str(e)}', code=500)

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'调用MCP工具失败: {str(e)}\n{traceback.format_exc()}')
            return error_response(message=f'调用工具失败: {str(e)}', code=500)


@mcp_server_ns.route('/<int:mcp_id>/resources')
class MCPServerResourcesAPI(Resource):
    """获取MCP Server资源列表（从数据库读取）"""

    def get(self, mcp_id):
        """获取MCP Server提供的资源列表"""
        try:
            mcp_server = MCPServer.query.filter_by(id=mcp_id, is_deleted=False).first()
            if not mcp_server:
                return error_response(message='MCP Server不存在', code=404)

            # 从数据库读取资源列表
            resources = MCPResource.query.filter_by(mcp_id=mcp_id).all()

            return success_response(data={
                'resources': [resource.to_dict() for resource in resources],
                'total': len(resources),
                'last_sync_at': mcp_server.last_sync_at.isoformat() if mcp_server.last_sync_at else None
            })

        except Exception as e:
            current_app.logger.error(f'获取MCP Server资源列表失败: {str(e)}\n{traceback.format_exc()}')
            return error_response(message=f'获取资源列表失败: {str(e)}', code=500)


@mcp_server_ns.route('/<int:mcp_id>/resources/<path:resource_uri>')
class MCPServerResourceReadAPI(Resource):
    """读取MCP Server资源内容"""

    def get(self, mcp_id, resource_uri):
        """读取指定资源的内容"""
        try:
            mcp_server = MCPServer.query.filter_by(id=mcp_id, is_deleted=False).first()
            if not mcp_server:
                return error_response(message='MCP Server不存在', code=404)

            if not mcp_server.is_enabled:
                return error_response(message='MCP Server已禁用', code=400)

            # 使用真实的 MCP 连接
            operations = MCPOperations(mcp_server)

            try:
                result = operations.read_resource(resource_uri)

                # 更新使用统计
                mcp_server.usage_count += 1
                mcp_server.last_used_at = datetime.utcnow()
                db.session.commit()

                return success_response(data=result)

            except MCPConnectionError as e:
                current_app.logger.error(f'MCP连接失败: {str(e)}')
                return error_response(message=f'MCP连接失败: {str(e)}', code=503)

            except MCPTimeoutError as e:
                current_app.logger.error(f'MCP连接超时: {str(e)}')
                return error_response(message=f'MCP连接超时: {str(e)}', code=504)

            except MCPClientError as e:
                current_app.logger.error(f'MCP客户端错误: {str(e)}')
                return error_response(message=f'MCP客户端错误: {str(e)}', code=500)

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'读取MCP资源失败: {str(e)}\n{traceback.format_exc()}')
            return error_response(message=f'读取资源失败: {str(e)}', code=500)


# ============== Skill API ==============

@skill_ns.route('')
class SkillListAPI(Resource):
    """Skill列表API"""

    def get(self):
        """获取Skill列表"""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            keyword = request.args.get('keyword')
            mcp_id = request.args.get('mcp_id', type=int)
            script_type = request.args.get('script_type')
            status = request.args.get('status')
            is_enabled = request.args.get('is_enabled')

            query = Skill.query.filter_by(is_deleted=False)

            if keyword:
                query = query.filter(
                    Skill.name.contains(keyword) |
                    Skill.code.contains(keyword) |
                    Skill.description.contains(keyword)
                )
            if mcp_id:
                query = query.filter_by(mcp_id=mcp_id)
            if script_type:
                query = query.filter_by(script_type=script_type)
            if status:
                query = query.filter_by(status=status)
            if is_enabled is not None:
                is_enabled_bool = is_enabled.lower() == 'true'
                query = query.filter_by(is_enabled=is_enabled_bool)

            pagination = query.order_by(Skill.id.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )

            return success_response(data={
                'items': [item.to_dict() for item in pagination.items],
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page
            })
        except Exception as e:
            current_app.logger.error(f'获取Skill列表失败: {str(e)}')
            return error_response(message=f'获取Skill列表失败: {str(e)}', code=500)

    @skill_ns.expect(skill_model)
    def post(self):
        """创建Skill"""
        try:
            data = request.get_json()

            # 检查编码是否已存在
            if data.get('code'):
                existing = Skill.query.filter_by(code=data['code'], is_deleted=False).first()
                if existing:
                    return error_response(message='Skill编码已存在', code=400)

            skill = Skill(
                name=data.get('name'),
                code=data.get('code'),
                description=data.get('description'),
                mcp_id=data.get('mcp_id'),
                script_content=data.get('script_content'),
                script_type=data.get('script_type', 'python'),
                params_schema=json.dumps(data.get('params_schema')) if data.get('params_schema') else None,
                params_example=json.dumps(data.get('params_example')) if data.get('params_example') else None,
                timeout=data.get('timeout', 60),
                log_enabled=data.get('log_enabled', True),
                retry_count=data.get('retry_count', 1),
                allowed_roles=json.dumps(data.get('allowed_roles')) if data.get('allowed_roles') else None,
                version=data.get('version', '1.0.0'),
                tags=data.get('tags'),
                status=data.get('status', 'active'),
                is_enabled=data.get('is_enabled', True),
                created_by=data.get('created_by')
            )

            db.session.add(skill)
            db.session.commit()

            return success_response(data=skill.to_dict(), message='创建成功', code=201)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'创建Skill失败: {str(e)}')
            return error_response(message=f'创建Skill失败: {str(e)}', code=500)


@skill_ns.route('/<int:skill_id>')
class SkillAPI(Resource):
    """Skill详情API"""

    def get(self, skill_id):
        """获取Skill详情"""
        try:
            skill = Skill.query.filter_by(id=skill_id, is_deleted=False).first()
            if not skill:
                return error_response(message='Skill不存在', code=404)
            return success_response(data=skill.to_dict())
        except Exception as e:
            return error_response(message=f'获取Skill失败: {str(e)}', code=500)

    @skill_ns.expect(skill_model)
    def put(self, skill_id):
        """更新Skill"""
        try:
            skill = Skill.query.filter_by(id=skill_id, is_deleted=False).first()
            if not skill:
                return error_response(message='Skill不存在', code=404)

            data = request.get_json()

            # 检查编码是否已被其他Skill使用
            if data.get('code') and data['code'] != skill.code:
                existing = Skill.query.filter_by(code=data['code'], is_deleted=False).first()
                if existing:
                    return error_response(message='Skill编码已存在', code=400)

            skill.name = data.get('name', skill.name)
            skill.code = data.get('code', skill.code)
            skill.description = data.get('description', skill.description)
            skill.mcp_id = data.get('mcp_id', skill.mcp_id)
            skill.script_content = data.get('script_content', skill.script_content)
            skill.script_type = data.get('script_type', skill.script_type)
            if data.get('params_schema') is not None:
                skill.params_schema = json.dumps(data['params_schema'])
            if data.get('params_example') is not None:
                skill.params_example = json.dumps(data['params_example'])
            skill.timeout = data.get('timeout', skill.timeout)
            skill.log_enabled = data.get('log_enabled', skill.log_enabled)
            skill.retry_count = data.get('retry_count', skill.retry_count)
            if data.get('allowed_roles') is not None:
                skill.allowed_roles = json.dumps(data['allowed_roles'])
            skill.version = data.get('version', skill.version)
            skill.tags = data.get('tags', skill.tags)
            skill.status = data.get('status', skill.status)
            skill.is_enabled = data.get('is_enabled', skill.is_enabled)
            skill.updated_by = data.get('updated_by')

            db.session.commit()
            return success_response(data=skill.to_dict(), message='更新成功')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'更新Skill失败: {str(e)}')
            return error_response(message=f'更新Skill失败: {str(e)}', code=500)

    def delete(self, skill_id):
        """删除Skill"""
        try:
            skill = Skill.query.filter_by(id=skill_id, is_deleted=False).first()
            if not skill:
                return error_response(message='Skill不存在', code=404)

            skill.is_deleted = True
            skill.updated_at = datetime.utcnow()
            db.session.commit()
            return success_response(message='删除成功')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'删除Skill失败: {str(e)}')
            return error_response(message=f'删除Skill失败: {str(e)}', code=500)


@skill_ns.route('/<int:skill_id>/execute')
class SkillExecuteAPI(Resource):
    """执行Skill"""

    def post(self, skill_id):
        """执行Skill"""
        try:
            skill = Skill.query.filter_by(id=skill_id, is_deleted=False).first()
            if not skill:
                return error_response(message='Skill不存在', code=404)

            if not skill.is_enabled:
                return error_response(message='Skill已禁用', code=400)

            data = request.get_json()
            params = data.get('params', {})

            # 这里实现具体的Skill执行逻辑
            # 根据script_type选择不同的执行方式
            result = {
                'success': True,
                'message': '执行成功',
                'output': f'Skill {skill.name} 执行完成',
                'params': params
            }

            # 更新统计
            skill.usage_count += 1
            skill.last_used_at = datetime.utcnow()
            skill.last_execution_result = json.dumps(result)
            db.session.commit()

            return success_response(data=result, message='执行成功')
        except Exception as e:
            current_app.logger.error(f'执行Skill失败: {str(e)}')
            return error_response(message=f'执行Skill失败: {str(e)}', code=500)


@skill_ns.route('/<int:skill_id>/version-history')
class SkillVersionHistoryAPI(Resource):
    """获取Skill版本历史"""

    def get(self, skill_id):
        """获取Skill版本历史"""
        try:
            skill = Skill.query.filter_by(id=skill_id, is_deleted=False).first()
            if not skill:
                return error_response(message='Skill不存在', code=404)

            versions = []
            if skill.previous_versions:
                try:
                    versions = json.loads(skill.previous_versions)
                except:
                    pass

            # 添加当前版本
            versions.append({
                'version': skill.version,
                'updated_at': skill.updated_at.isoformat() if skill.updated_at else None,
                'updated_by': skill.updated_by
            })

            return success_response(data={'items': versions})
        except Exception as e:
            current_app.logger.error(f'获取Skill版本历史失败: {str(e)}')
            return error_response(message=f'获取Skill版本历史失败: {str(e)}', code=500)

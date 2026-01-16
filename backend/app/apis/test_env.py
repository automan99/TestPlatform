"""
测试环境管理API
"""
from flask import request, current_app
from flask_restx import Namespace, Resource, fields
from app import db
from app.models import TestEnvironment, EnvironmentResource
from app.utils import success_response, error_response
import json

# 命名空间
test_environment_ns = Namespace('TestEnvironments', description='测试环境管理')
environment_resource_ns = Namespace('EnvironmentResources', description='环境资源管理')

# Swagger模型定义
test_environment_model = test_environment_ns.model('TestEnvironment', {
    'name': fields.String(required=True, description='环境名称'),
    'env_code': fields.String(description='环境编码'),
    'env_type': fields.String(description='环境类型'),
    'description': fields.String(description='描述'),
    'base_url': fields.String(description='基础URL'),
    'db_connection': fields.String(description='数据库连接(JSON)'),
    'status': fields.String(description='状态'),
    'project_id': fields.Integer(description='项目ID')
})

environment_resource_model = environment_resource_ns.model('EnvironmentResource', {
    'environment_id': fields.Integer(required=True, description='环境ID'),
    'name': fields.String(required=True, description='资源名称'),
    'resource_type': fields.String(description='资源类型'),
    'host': fields.String(description='主机地址'),
    'port': fields.Integer(description='端口'),
    'username': fields.String(description='用户名'),
    'password': fields.String(description='密码'),
    'os_type': fields.String(description='操作系统类型'),
    'os_version': fields.String(description='操作系统版本'),
    'cpu_cores': fields.Integer(description='CPU核心数'),
    'memory_gb': fields.Integer(description='内存(GB)'),
    'disk_gb': fields.Integer(description='磁盘(GB)'),
    'status': fields.String(description='状态'),
    'description': fields.String(description='描述'),
    'tags': fields.String(description='标签'),
    'capabilities': fields.String(description='能力描述(JSON)')
})


# ============== 测试环境API ==============

@test_environment_ns.route('')
class TestEnvironmentListAPI(Resource):
    """测试环境列表API"""

    def get(self):
        """获取测试环境列表"""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            project_id = request.args.get('project_id', type=int)
            env_type = request.args.get('env_type')
            status = request.args.get('status')
            keyword = request.args.get('keyword')

            query = TestEnvironment.query

            if project_id:
                query = query.filter_by(project_id=project_id)
            if env_type:
                query = query.filter_by(env_type=env_type)
            if status:
                query = query.filter_by(status=status)
            if keyword:
                query = query.filter(TestEnvironment.name.contains(keyword) |
                                     TestEnvironment.env_code.contains(keyword))

            pagination = query.order_by(TestEnvironment.id.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )

            return success_response(data={
                'items': [item.to_dict() for item in pagination.items],
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page
            })
        except Exception as e:
            current_app.logger.error(f'获取测试环境失败: {str(e)}')
            return error_response(message=f'获取测试环境失败: {str(e)}', code=500)

    @test_environment_ns.expect(test_environment_model)
    def post(self):
        """创建测试环境"""
        try:
            data = request.get_json()

            # 检查环境编码是否已存在
            if data.get('env_code'):
                existing = TestEnvironment.query.filter_by(env_code=data['env_code']).first()
                if existing:
                    return error_response(message='环境编码已存在', code=400)

            environment = TestEnvironment(
                name=data.get('name'),
                env_code=data.get('env_code'),
                env_type=data.get('env_type', 'testing'),
                description=data.get('description'),
                base_url=data.get('base_url'),
                db_connection=json.dumps(data.get('db_connection')) if data.get('db_connection') else None,
                status=data.get('status', 'active'),
                is_active=data.get('is_active', True),
                project_id=data.get('project_id'),
                created_by=data.get('created_by')
            )

            db.session.add(environment)
            db.session.commit()

            return success_response(data=environment.to_dict(), message='创建成功', code=201)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'创建测试环境失败: {str(e)}')
            return error_response(message=f'创建测试环境失败: {str(e)}', code=500)


@test_environment_ns.route('/<int:env_id>')
class TestEnvironmentAPI(Resource):
    """测试环境详情API"""

    def get(self, env_id):
        """获取测试环境详情"""
        try:
            environment = TestEnvironment.query.get_or_404(env_id)
            env_dict = environment.to_dict()
            # 获取关联的资源
            resources = EnvironmentResource.query.filter_by(environment_id=env_id).all()
            env_dict['resources'] = [r.to_dict() for r in resources]
            return success_response(data=env_dict)
        except Exception as e:
            return error_response(message=f'获取测试环境失败: {str(e)}', code=500)

    @test_environment_ns.expect(test_environment_model)
    def put(self, env_id):
        """更新测试环境"""
        try:
            environment = TestEnvironment.query.get_or_404(env_id)
            data = request.get_json()

            # 检查环境编码是否已被其他环境使用
            if data.get('env_code') and data['env_code'] != environment.env_code:
                existing = TestEnvironment.query.filter_by(env_code=data['env_code']).first()
                if existing:
                    return error_response(message='环境编码已存在', code=400)

            environment.name = data.get('name', environment.name)
            environment.env_code = data.get('env_code', environment.env_code)
            environment.env_type = data.get('env_type', environment.env_type)
            environment.description = data.get('description', environment.description)
            environment.base_url = data.get('base_url', environment.base_url)

            if data.get('db_connection') is not None:
                environment.db_connection = json.dumps(data.get('db_connection'))

            environment.status = data.get('status', environment.status)
            environment.is_active = data.get('is_active', environment.is_active)
            environment.project_id = data.get('project_id', environment.project_id)
            environment.updated_by = data.get('updated_by')

            db.session.commit()
            return success_response(data=environment.to_dict(), message='更新成功')
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'更新测试环境失败: {str(e)}', code=500)

    def delete(self, env_id):
        """删除测试环境"""
        try:
            environment = TestEnvironment.query.get_or_404(env_id)

            # 检查是否有关联的资源
            if environment.resources.count() > 0:
                return error_response(message='该环境下有资源，无法删除', code=400)

            # 检查是否被测试计划使用
            if environment.test_plans.count() > 0:
                return error_response(message='该环境被测试计划使用，无法删除', code=400)

            db.session.delete(environment)
            db.session.commit()
            return success_response(message='删除成功')
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'删除测试环境失败: {str(e)}', code=500)


# ============== 环境资源API ==============

@environment_resource_ns.route('')
class EnvironmentResourceListAPI(Resource):
    """环境资源列表API"""

    def get(self):
        """获取环境资源列表"""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            environment_id = request.args.get('environment_id', type=int)
            resource_type = request.args.get('resource_type')
            status = request.args.get('status')
            keyword = request.args.get('keyword')

            query = EnvironmentResource.query

            if environment_id:
                query = query.filter_by(environment_id=environment_id)
            if resource_type:
                query = query.filter_by(resource_type=resource_type)
            if status:
                query = query.filter_by(status=status)
            if keyword:
                query = query.filter(EnvironmentResource.name.contains(keyword) |
                                     EnvironmentResource.host.contains(keyword))

            pagination = query.order_by(EnvironmentResource.id.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )

            return success_response(data={
                'items': [item.to_dict() for item in pagination.items],
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page
            })
        except Exception as e:
            current_app.logger.error(f'获取环境资源失败: {str(e)}')
            return error_response(message=f'获取环境资源失败: {str(e)}', code=500)

    @environment_resource_ns.expect(environment_resource_model)
    def post(self):
        """创建环境资源"""
        try:
            data = request.get_json()

            resource = EnvironmentResource(
                environment_id=data.get('environment_id'),
                name=data.get('name'),
                resource_type=data.get('resource_type', 'server'),
                host=data.get('host'),
                port=data.get('port'),
                username=data.get('username'),
                password=data.get('password'),
                os_type=data.get('os_type'),
                os_version=data.get('os_version'),
                cpu_cores=data.get('cpu_cores'),
                memory_gb=data.get('memory_gb'),
                disk_gb=data.get('disk_gb'),
                status=data.get('status', 'online'),
                description=data.get('description'),
                tags=data.get('tags'),
                capabilities=json.dumps(data.get('capabilities')) if data.get('capabilities') else None,
                is_active=data.get('is_active', True),
                created_by=data.get('created_by')
            )

            db.session.add(resource)
            db.session.commit()

            return success_response(data=resource.to_dict(), message='创建成功', code=201)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'创建环境资源失败: {str(e)}')
            return error_response(message=f'创建环境资源失败: {str(e)}', code=500)


@environment_resource_ns.route('/<int:resource_id>')
class EnvironmentResourceAPI(Resource):
    """环境资源详情API"""

    def get(self, resource_id):
        """获取环境资源详情"""
        try:
            resource = EnvironmentResource.query.get_or_404(resource_id)
            return success_response(data=resource.to_dict())
        except Exception as e:
            return error_response(message=f'获取环境资源失败: {str(e)}', code=500)

    @environment_resource_ns.expect(environment_resource_model)
    def put(self, resource_id):
        """更新环境资源"""
        try:
            resource = EnvironmentResource.query.get_or_404(resource_id)
            data = request.get_json()

            resource.name = data.get('name', resource.name)
            resource.resource_type = data.get('resource_type', resource.resource_type)
            resource.host = data.get('host', resource.host)
            resource.port = data.get('port', resource.port)
            resource.username = data.get('username', resource.username)
            resource.password = data.get('password', resource.password)
            resource.os_type = data.get('os_type', resource.os_type)
            resource.os_version = data.get('os_version', resource.os_version)
            resource.cpu_cores = data.get('cpu_cores', resource.cpu_cores)
            resource.memory_gb = data.get('memory_gb', resource.memory_gb)
            resource.disk_gb = data.get('disk_gb', resource.disk_gb)
            resource.status = data.get('status', resource.status)
            resource.description = data.get('description', resource.description)
            resource.tags = data.get('tags', resource.tags)
            resource.is_active = data.get('is_active', resource.is_active)
            resource.updated_by = data.get('updated_by')

            if data.get('capabilities') is not None:
                resource.capabilities = json.dumps(data.get('capabilities'))

            db.session.commit()
            return success_response(data=resource.to_dict(), message='更新成功')
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'更新环境资源失败: {str(e)}', code=500)

    def delete(self, resource_id):
        """删除环境资源"""
        try:
            resource = EnvironmentResource.query.get_or_404(resource_id)
            db.session.delete(resource)
            db.session.commit()
            return success_response(message='删除成功')
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'删除环境资源失败: {str(e)}', code=500)


@environment_resource_ns.route('/<int:resource_id>/status')
class EnvironmentResourceStatusAPI(Resource):
    """更新资源状态API"""

    def put(self, resource_id):
        """更新资源状态（用于Agent定期上报状态）"""
        try:
            data = request.get_json()
            resource = EnvironmentResource.query.get_or_404(resource_id)

            resource.status = data.get('status', resource.status)
            resource.last_check_time = datetime.utcnow()

            # 可以更新资源使用情况
            if data.get('cpu_usage'):
                if not resource.capabilities:
                    resource.capabilities = {}
                capabilities = json.loads(resource.capabilities) if resource.capabilities else {}
                capabilities['cpu_usage'] = data.get('cpu_usage')
                capabilities['memory_usage'] = data.get('memory_usage')
                capabilities['disk_usage'] = data.get('disk_usage')
                resource.capabilities = json.dumps(capabilities)

            db.session.commit()
            return success_response(data=resource.to_dict(), message='状态更新成功')
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'更新资源状态失败: {str(e)}', code=500)

"""
项目管理API
"""
from flask import request
from flask_restx import Namespace, Resource, fields
from app.utils.errors import success_response, error_response
from app.models import Project, Tenant
from app import db
from datetime import datetime
import random
import string

# 创建命名空间
project_ns = Namespace('project', description='项目管理接口')

# 请求参数模型定义
project_model = project_ns.model('Project', {
    'name': fields.String(required=True, description='项目名称'),
    'code': fields.String(required=True, description='项目代码'),
    'description': fields.String(description='项目描述'),
    'project_type': fields.String(description='项目类型'),
    'key': fields.String(description='项目标识符'),
    'url': fields.String(description='项目URL'),
    'repository': fields.String(description='代码仓库地址'),
    'status': fields.String(description='状态'),
    'owner': fields.String(description='项目负责人'),
    'lead': fields.String(description='项目主管'),
    'color': fields.String(description='颜色'),
    'icon': fields.String(description='图标')
})


def generate_project_key():
    """生成项目key"""
    return ''.join(random.choices(string.ascii_uppercase, k=3))


@project_ns.route('/')
class ProjectListAPI(Resource):
    @project_ns.doc('get_projects')
    def get(self):
        """获取项目列表"""
        try:
            # 获取查询参数
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            tenant_id = request.args.get('tenant_id', type=int)
            keyword = request.args.get('keyword', '')
            status = request.args.get('status', '')

            # 构建查询
            query = Project.query.filter_by(is_deleted=False)

            if tenant_id:
                query = query.filter_by(tenant_id=tenant_id)

            if keyword:
                query = query.filter(
                    db.or_(
                        Project.name.like(f'%{keyword}%'),
                        Project.code.like(f'%{keyword}%'),
                        Project.description.like(f'%{keyword}%')
                    )
                )

            if status:
                query = query.filter_by(status=status)

            # 排序
            query = query.order_by(Project.sort_order.asc(), Project.id.desc())

            # 分页
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)

            return success_response(data={
                'items': [p.to_dict() for p in pagination.items],
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page,
                'per_page': per_page
            })
        except Exception as e:
            return error_response(message=f'获取项目列表失败: {str(e)}')

    @project_ns.doc('create_project')
    @project_ns.expect(project_model)
    def post(self):
        """创建项目"""
        try:
            data = request.get_json()

            # 验证必填字段
            if not data.get('name'):
                return error_response(message='项目名称不能为空')

            if not data.get('code'):
                return error_response(message='项目代码不能为空')

            # 检查项目代码是否已存在
            if Project.query.filter_by(code=data['code'], is_deleted=False).first():
                return error_response(message='项目代码已存在')

            # 检查项目key是否已存在
            if data.get('key') and Project.query.filter_by(key=data['key']).first():
                return error_response(message='项目标识符已存在')

            # 创建项目
            project = Project(
                tenant_id=data.get('tenant_id'),
                name=data['name'],
                code=data['code'],
                description=data.get('description'),
                project_type=data.get('project_type', 'web'),
                key=data.get('key') or generate_project_key(),
                url=data.get('url'),
                repository=data.get('repository'),
                status=data.get('status', 'active'),
                owner=data.get('owner'),
                lead=data.get('lead'),
                color=data.get('color', '#409EFF'),
                icon=data.get('icon'),
                sort_order=data.get('sort_order', 0),
                created_by=data.get('created_by'),
                created_at=datetime.utcnow()
            )

            db.session.add(project)
            db.session.commit()

            return success_response(data=project.to_dict(), message='项目创建成功')
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'创建项目失败: {str(e)}')


@project_ns.route('/<int:project_id>')
class ProjectDetailAPI(Resource):
    @project_ns.doc('get_project')
    def get(self, project_id):
        """获取项目详情"""
        try:
            project = Project.query.filter_by(id=project_id, is_deleted=False).first()

            if not project:
                return error_response(message='项目不存在', code=404)

            # 更新统计信息
            project.update_statistics()

            return success_response(data=project.to_dict())
        except Exception as e:
            return error_response(message=f'获取项目详情失败: {str(e)}')

    @project_ns.doc('update_project')
    @project_ns.expect(project_model)
    def put(self, project_id):
        """更新项目"""
        try:
            project = Project.query.filter_by(id=project_id, is_deleted=False).first()

            if not project:
                return error_response(message='项目不存在', code=404)

            data = request.get_json()

            # 更新字段
            if 'name' in data:
                project.name = data['name']
            if 'description' in data:
                project.description = data['description']
            if 'project_type' in data:
                project.project_type = data['project_type']
            if 'status' in data:
                project.status = data['status']
            if 'url' in data:
                project.url = data['url']
            if 'repository' in data:
                project.repository = data['repository']
            if 'owner' in data:
                project.owner = data['owner']
            if 'lead' in data:
                project.lead = data['lead']
            if 'color' in data:
                project.color = data['color']
            if 'icon' in data:
                project.icon = data['icon']
            if 'sort_order' in data:
                project.sort_order = data['sort_order']

            # 检查代码重复
            if 'code' in data and data['code'] != project.code:
                if Project.query.filter_by(code=data['code'], is_deleted=False).first():
                    return error_response(message='项目代码已存在')
                project.code = data['code']

            # 检查key重复
            if 'key' in data and data['key'] != project.key:
                if Project.query.filter_by(key=data['key']).first():
                    return error_response(message='项目标识符已存在')
                project.key = data['key']

            project.updated_by = data.get('updated_by')
            project.updated_at = datetime.utcnow()

            db.session.commit()

            return success_response(data=project.to_dict(), message='项目更新成功')
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'更新项目失败: {str(e)}')

    @project_ns.doc('delete_project')
    def delete(self, project_id):
        """删除项目"""
        try:
            project = Project.query.filter_by(id=project_id, is_deleted=False).first()

            if not project:
                return error_response(message='项目不存在', code=404)

            # 软删除
            project.is_deleted = True
            project.updated_at = datetime.utcnow()

            db.session.commit()

            return success_response(message='项目删除成功')
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'删除项目失败: {str(e)}')


@project_ns.route('/<int:project_id>/statistics')
class ProjectStatisticsAPI(Resource):
    @project_ns.doc('get_project_statistics')
    def get(self, project_id):
        """获取项目统计信息"""
        try:
            project = Project.query.filter_by(id=project_id, is_deleted=False).first()

            if not project:
                return error_response(message='项目不存在', code=404)

            # 更新并获取统计信息
            project.update_statistics()

            from app.models import TestCase, TestSuite, TestPlan, Defect, TestExecution

            # 获取详细统计
            test_suites = TestSuite.query.filter_by(
                project_id=project_id,
                is_deleted=False
            ).count()

            test_cases = TestCase.query.filter(
                TestCase.is_deleted == False
            ).join(TestSuite).filter(TestSuite.project_id == project_id).count()

            test_plans = TestPlan.query.filter_by(project_id=project_id).count()

            defects = Defect.query.filter_by(project_id=project_id).count()

            # 获取最近的执行记录
            recent_executions = TestExecution.query.join(TestCase).join(TestSuite).filter(
                TestSuite.project_id == project_id
            ).order_by(TestExecution.execution_time.desc()).limit(10).all()

            return success_response(data={
                'project': project.to_dict(),
                'test_suites': test_suites,
                'test_cases': test_cases,
                'test_plans': test_plans,
                'defects': defects,
                'recent_executions': [e.to_dict() for e in recent_executions]
            })
        except Exception as e:
            return error_response(message=f'获取项目统计失败: {str(e)}')


@project_ns.route('/switch')
class ProjectSwitchAPI(Resource):
    @project_ns.doc('switch_project')
    def post(self):
        """切换项目"""
        try:
            data = request.get_json()
            project_id = data.get('project_id')

            if not project_id:
                return error_response(message='项目ID不能为空')

            project = Project.query.filter_by(id=project_id, is_deleted=False).first()

            if not project:
                return error_response(message='项目不存在', code=404)

            # 这里可以设置session或返回token信息
            # 简化实现，直接返回项目信息
            return success_response(data={
                'project': project.to_dict(),
                'message': '项目切换成功'
            })
        except Exception as e:
            return error_response(message=f'切换项目失败: {str(e)}')

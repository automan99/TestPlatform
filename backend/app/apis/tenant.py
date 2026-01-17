"""
租户管理API
"""
from flask import request, current_app, g
from flask_restx import Namespace, Resource, fields
from app import db
from app.models import Tenant, TenantUser
from app.utils import success_response, error_response
from datetime import datetime, date

# 命名空间
tenant_ns = Namespace('Tenants', description='租户管理')

# Swagger模型定义
tenant_model = tenant_ns.model('Tenant', {
    'name': fields.String(required=True, description='租户名称'),
    'code': fields.String(required=True, description='租户代码'),
    'description': fields.String(description='描述'),
    'logo': fields.String(description='Logo URL'),
    'status': fields.String(description='状态'),
    'max_users': fields.Integer(description='最大用户数'),
    'max_projects': fields.Integer(description='最大项目数'),
    'max_storage_gb': fields.Integer(description='最大存储空间(GB)'),
    'expire_date': fields.String(description='过期日期(YYYY-MM-DD)'),
    'settings': fields.Raw(description='租户设置(JSON)')
})


# ============== 租户管理API ==============

@tenant_ns.route('')
class TenantListAPI(Resource):
    """租户列表API"""

    def get(self):
        """获取租户列表"""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            status = request.args.get('status')
            keyword = request.args.get('keyword')

            query = Tenant.query.filter_by(is_deleted=False)

            if status:
                query = query.filter_by(status=status)
            if keyword:
                query = query.filter(Tenant.name.contains(keyword) |
                                     Tenant.code.contains(keyword))

            pagination = query.order_by(Tenant.id.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )

            items = [item.to_dict() for item in pagination.items]

            return success_response(data={
                'items': items,
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page
            })
        except Exception as e:
            current_app.logger.error(f'获取租户列表失败: {str(e)}')
            return error_response(message=f'获取租户列表失败: {str(e)}', code=500)

    @tenant_ns.expect(tenant_model)
    def post(self):
        """创建租户"""
        try:
            data = request.get_json()

            # 检查租户代码是否已存在
            if Tenant.query.filter_by(code=data['code']).first():
                return error_response(message='租户代码已存在', code=400)

            # 处理过期日期
            expire_date = None
            if data.get('expire_date'):
                expire_date = datetime.strptime(data.get('expire_date'), '%Y-%m-%d').date()

            tenant = Tenant(
                name=data.get('name'),
                code=data.get('code'),
                description=data.get('description'),
                logo=data.get('logo'),
                status=data.get('status', 'active'),
                max_users=data.get('max_users', 10),
                max_projects=data.get('max_projects', 5),
                max_storage_gb=data.get('max_storage_gb', 10),
                expire_date=expire_date,
                settings=data.get('settings'),
                created_by=g.get('user_id')
            )

            db.session.add(tenant)
            db.session.commit()

            return success_response(data=tenant.to_dict(), message='创建成功', code=201)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'创建租户失败: {str(e)}')
            return error_response(message=f'创建租户失败: {str(e)}', code=500)


@tenant_ns.route('/<int:tenant_id>')
class TenantAPI(Resource):
    """租户详情API"""

    def get(self, tenant_id):
        """获取租户详情"""
        try:
            tenant = Tenant.query.filter_by(id=tenant_id, is_deleted=False).first_or_404()
            return success_response(data=tenant.to_dict())
        except Exception as e:
            return error_response(message=f'获取租户详情失败: {str(e)}', code=500)

    @tenant_ns.expect(tenant_model)
    def put(self, tenant_id):
        """更新租户"""
        try:
            tenant = Tenant.query.filter_by(id=tenant_id, is_deleted=False).first_or_404()
            data = request.get_json()

            # 检查租户代码是否被其他租户使用
            if data.get('code') and data['code'] != tenant.code:
                if Tenant.query.filter_by(code=data['code']).first():
                    return error_response(message='租户代码已存在', code=400)

            tenant.name = data.get('name', tenant.name)
            tenant.code = data.get('code', tenant.code)
            tenant.description = data.get('description', tenant.description)
            tenant.logo = data.get('logo', tenant.logo)
            tenant.status = data.get('status', tenant.status)
            tenant.max_users = data.get('max_users', tenant.max_users)
            tenant.max_projects = data.get('max_projects', tenant.max_projects)
            tenant.max_storage_gb = data.get('max_storage_gb', tenant.max_storage_gb)

            if data.get('expire_date'):
                tenant.expire_date = datetime.strptime(data.get('expire_date'), '%Y-%m-%d').date()

            if data.get('settings') is not None:
                tenant.settings = data.get('settings')

            tenant.updated_by = g.get('user_id')

            db.session.commit()
            return success_response(data=tenant.to_dict(), message='更新成功')
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'更新租户失败: {str(e)}', code=500)

    def delete(self, tenant_id):
        """删除租户（软删除）"""
        try:
            tenant = Tenant.query.filter_by(id=tenant_id, is_deleted=False).first_or_404()

            # 检查是否有关联数据
            if tenant.users.count() > 0:
                return error_response(message='该租户下有用户，无法删除', code=400)
            if tenant.projects.count() > 0:
                return error_response(message='该租户下有项目，无法删除', code=400)

            tenant.is_deleted = True
            tenant.updated_by = g.get('user_id')
            db.session.commit()

            return success_response(message='删除成功')
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'删除租户失败: {str(e)}', code=500)


@tenant_ns.route('/<int:tenant_id>/users')
class TenantUsersAPI(Resource):
    """租户用户列表API"""

    def get(self, tenant_id):
        """获取租户用户列表"""
        try:
            tenant = Tenant.query.filter_by(id=tenant_id, is_deleted=False).first_or_404()

            tenant_users = TenantUser.query.filter_by(tenant_id=tenant_id, is_deleted=False).all()
            users_data = [tu.to_dict() for tu in tenant_users]

            return success_response(data={
                'items': users_data,
                'total': len(users_data)
            })
        except Exception as e:
            current_app.logger.error(f'获取租户用户失败: {str(e)}')
            return error_response(message=f'获取租户用户失败: {str(e)}', code=500)


@tenant_ns.route('/switch')
class TenantSwitchAPI(Resource):
    """切换租户API"""

    def post(self):
        """切换当前用户的租户"""
        try:
            data = request.get_json()
            tenant_id = data.get('tenant_id')
            user_id = g.get('user_id')

            if not tenant_id:
                return error_response(message='请选择租户', code=400)

            # 检查租户是否存在
            tenant = Tenant.query.filter_by(id=tenant_id, is_deleted=False).first_or_404()

            # 检查用户是否属于该租户
            tenant_user = TenantUser.query.filter_by(
                tenant_id=tenant_id,
                user_id=user_id,
                is_deleted=False
            ).first()

            if not tenant_user:
                return error_response(message='您不是该租户的成员', code=403)

            # 检查租户状态
            if tenant.status != 'active' or not tenant.is_active:
                return error_response(message='该租户未激活或已暂停', code=403)

            # 检查租户是否过期
            if tenant.expire_date and tenant.expire_date < date.today():
                return error_response(message='该租户已过期', code=403)

            # TODO: 设置用户当前租户到 session/token
            # 这里可以在 g 对象中设置当前租户，供后续请求使用
            g.current_tenant_id = tenant_id

            return success_response(data=tenant.to_dict(), message='切换成功')
        except Exception as e:
            current_app.logger.error(f'切换租户失败: {str(e)}')
            return error_response(message=f'切换租户失败: {str(e)}', code=500)


@tenant_ns.route('/my')
class MyTenantAPI(Resource):
    """我的租户API"""

    def get(self):
        """获取当前用户的租户列表"""
        try:
            user_id = g.get('user_id')

            if not user_id:
                return error_response(message='未登录', code=401)

            # 获取用户所属的所有租户
            tenant_users = TenantUser.query.filter_by(
                user_id=user_id,
                is_deleted=False
            ).all()

            tenants_data = []
            default_tenant = None

            for tu in tenant_users:
                tenant = Tenant.query.filter_by(
                    id=tu.tenant_id,
                    is_deleted=False
                ).first()

                if tenant:
                    tenant_dict = tenant.to_dict()
                    tenant_dict['role'] = tu.role
                    tenant_dict['is_default'] = tu.is_default
                    tenants_data.append(tenant_dict)

                    if tu.is_default:
                        default_tenant = tenant_dict

            return success_response(data={
                'tenants': tenants_data,
                'default_tenant': default_tenant,
                'total': len(tenants_data)
            })
        except Exception as e:
            current_app.logger.error(f'获取用户租户失败: {str(e)}')
            return error_response(message=f'获取用户租户失败: {str(e)}', code=500)


# ============== 租户成员管理API ==============

@tenant_ns.route('/<int:tenant_id>/members')
class TenantMembersAPI(Resource):
    """租户成员管理API"""

    def get(self, tenant_id):
        """获取租户成员列表"""
        try:
            tenant = Tenant.query.filter_by(id=tenant_id, is_deleted=False).first_or_404()

            tenant_users = TenantUser.query.filter_by(
                tenant_id=tenant_id,
                is_deleted=False
            ).all()

            # 获取用户信息
            from app.models import User
            members_data = []
            for tu in tenant_users:
                user = User.query.get(tu.user_id)
                if user:
                    member_dict = {
                        'id': tu.id,
                        'user_id': tu.user_id,
                        'username': user.username,
                        'real_name': user.real_name,
                        'email': user.email,
                        'role': tu.role,
                        'is_default': tu.is_default,
                        'created_at': tu.created_at.isoformat() if tu.created_at else None
                    }
                    members_data.append(member_dict)

            return success_response(data=members_data)
        except Exception as e:
            current_app.logger.error(f'获取租户成员失败: {str(e)}')
            return error_response(message=f'获取租户成员失败: {str(e)}', code=500)

    def post(self, tenant_id):
        """添加成员到租户"""
        try:
            data = request.get_json()
            user_id = data.get('user_id')
            role = data.get('role', 'member')

            if not user_id:
                return error_response(message='用户ID不能为空', code=400)

            # 检查租户是否存在
            tenant = Tenant.query.filter_by(id=tenant_id, is_deleted=False).first_or_404()

            # 检查用户是否已在该租户中
            existing = TenantUser.query.filter_by(
                tenant_id=tenant_id,
                user_id=user_id,
                is_deleted=False
            ).first()
            if existing:
                return error_response(message='用户已在该租户中', code=400)

            # 检查用户是否存在
            from app.models import User
            user = User.query.get(user_id)
            if not user:
                return error_response(message='用户不存在', code=404)

            # 添加成员
            tenant_user = TenantUser(
                tenant_id=tenant_id,
                user_id=user_id,
                role=role,
                is_default=False,
                created_by=g.get('user_id')
            )

            db.session.add(tenant_user)
            db.session.commit()

            return success_response(message='添加成员成功', code=201)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'添加租户成员失败: {str(e)}')
            return error_response(message=f'添加租户成员失败: {str(e)}', code=500)


@tenant_ns.route('/<int:tenant_id>/members/<int:user_id>')
class TenantMemberAPI(Resource):
    """租户成员详情API"""

    def delete(self, tenant_id, user_id):
        """从租户移除成员"""
        try:
            # 检查租户是否存在
            tenant = Tenant.query.filter_by(id=tenant_id, is_deleted=False).first_or_404()

            # 获取租户用户关联
            tenant_user = TenantUser.query.filter_by(
                tenant_id=tenant_id,
                user_id=user_id,
                is_deleted=False
            ).first_or_404()

            # 软删除
            tenant_user.is_deleted = True
            db.session.commit()

            return success_response(message='移除成员成功')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'移除租户成员失败: {str(e)}')
            return error_response(message=f'移除租户成员失败: {str(e)}', code=500)

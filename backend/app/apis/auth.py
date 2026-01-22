"""
认证相关API
"""
from flask import request, g, current_app
from flask_restx import Namespace, Resource, fields
from app.models import Tenant, User, TenantUser
from app.utils.errors import success_response, error_response
from app.utils.permissions import get_user_accessible_tenants
from app.utils.jwt_utils import generate_token
from datetime import datetime

# 创建命名空间
auth_ns = Namespace('auth', description='认证相关接口')

# 定义数据模型
login_model = auth_ns.model('Login', {
    'username': fields.String(required=True, description='用户名'),
    'password': fields.String(required=True, description='密码')
})

tenant_select_model = auth_ns.model('TenantSelect', {
    'tenant_id': fields.Integer(required=True, description='租户ID')
})


@auth_ns.route('/login')
class AuthLoginAPI(Resource):
    @auth_ns.doc('login')
    @auth_ns.expect(login_model)
    def post(self):
        """用户登录"""
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        # 验证用户名密码
        user = User.query.filter_by(
            username=username,
            is_deleted=False,
            status='active'
        ).first()

        if not user or not user.check_password(password):
            return error_response(message='用户名或密码错误', code=401)

        # 更新最后登录时间
        user.last_login_at = datetime.utcnow()
        from app import db
        db.session.commit()

        # 生成 JWT token
        token = generate_token(user.id, user.username)

        # 获取用户可访问的租户列表
        tenants = get_user_accessible_tenants(user)

        # 构建租户列表（包含角色信息）
        tenant_list = []
        for tenant in tenants:
            tenant_dict = tenant.to_dict()
            # 添加用户在该租户中的角色
            if user.is_super_admin():
                tenant_dict['user_role'] = 'super_admin'
                tenant_dict['user_role_name'] = '超级管理员'
            else:
                tenant_user = TenantUser.query.filter_by(
                    tenant_id=tenant.id,
                    user_id=user.id,
                    is_deleted=False
                ).first()
                if tenant_user:
                    tenant_dict['user_role'] = tenant_user.role
                    tenant_dict['user_role_name'] = self._get_role_name(tenant_user.role)
            tenant_list.append(tenant_dict)

        # 构建用户信息
        user_info = user.to_dict()
        user_info['tenants'] = tenant_list

        return success_response(data={
            'token': token,
            'user': user_info
        }, message='登录成功')

    @staticmethod
    def _get_role_name(role):
        """获取角色名称"""
        role_names = {
            'super_admin': '超级管理员',
            'owner': '所有者',
            'admin': '管理员',
            'member': '成员'
        }
        return role_names.get(role, role)


@auth_ns.route('/tenants')
class AuthTenantsAPI(Resource):
    @auth_ns.doc('get_user_tenants')
    def get(self):
        """获取当前用户可访问的租户列表"""
        from app.utils.permissions import get_current_user

        user = get_current_user()
        if not user:
            return error_response(message='未登录或登录已过期', code=401)

        tenants = get_user_accessible_tenants(user)

        # 构建租户列表（包含角色信息）
        tenant_list = []
        for tenant in tenants:
            tenant_dict = tenant.to_dict()
            if user.is_super_admin():
                tenant_dict['user_role'] = 'super_admin'
                tenant_dict['user_role_name'] = '超级管理员'
            else:
                tenant_user = TenantUser.query.filter_by(
                    tenant_id=tenant.id,
                    user_id=user.id,
                    is_deleted=False
                ).first()
                if tenant_user:
                    tenant_dict['user_role'] = tenant_user.role
                    role_names = {'owner': '所有者', 'admin': '管理员', 'member': '成员'}
                    tenant_dict['user_role_name'] = role_names.get(tenant_user.role, tenant_user.role)
            tenant_list.append(tenant_dict)

        return success_response(data={
            'tenants': tenant_list
        })


@auth_ns.route('/select-tenant')
class AuthSelectTenantAPI(Resource):
    @auth_ns.doc('select_tenant')
    @auth_ns.expect(tenant_select_model)
    def post(self):
        """选择租户"""
        from app.utils.permissions import get_current_user

        data = request.get_json()
        tenant_id = data.get('tenant_id')

        user = get_current_user()
        if not user:
            return error_response(message='未登录或登录已过期', code=401)

        # 验证租户是否存在
        tenant = Tenant.query.filter_by(
            id=tenant_id,
            is_deleted=False,
            is_active=True
        ).first()

        if not tenant:
            return error_response(message='租户不存在或已停用', code=404)

        # 验证用户是否有权访问该租户
        if not user.is_super_admin():
            tenant_user = TenantUser.query.filter_by(
                tenant_id=tenant_id,
                user_id=user.id,
                is_deleted=False
            ).first()
            if not tenant_user:
                return error_response(message='您无权访问该租户', code=403)

        # 设置当前租户
        g.tenant_id = tenant_id
        g.tenant = tenant

        return success_response(data=tenant.to_dict(), message='租户选择成功')


@auth_ns.route('/current-user')
class AuthCurrentUserAPI(Resource):
    @auth_ns.doc('get_current_user')
    def get(self):
        """获取当前登录用户信息"""
        from app.utils.permissions import get_current_user

        user = get_current_user()
        if not user:
            return error_response(message='未登录或登录已过期', code=401)

        # 获取用户可访问的租户列表
        tenants = get_user_accessible_tenants(user)

        # 构建租户列表
        tenant_list = []
        for tenant in tenants:
            tenant_dict = tenant.to_dict()
            if user.is_super_admin():
                tenant_dict['user_role'] = 'super_admin'
                tenant_dict['user_role_name'] = '超级管理员'
            else:
                tenant_user = TenantUser.query.filter_by(
                    tenant_id=tenant.id,
                    user_id=user.id,
                    is_deleted=False
                ).first()
                if tenant_user:
                    tenant_dict['user_role'] = tenant_user.role
                    role_names = {'owner': '所有者', 'admin': '管理员', 'member': '成员'}
                    tenant_dict['user_role_name'] = role_names.get(tenant_user.role, tenant_user.role)
            tenant_list.append(tenant_dict)

        # 构建用户信息
        user_info = user.to_dict()
        user_info['tenants'] = tenant_list
        user_info['is_super_admin'] = user.is_super_admin()

        return success_response(data=user_info)

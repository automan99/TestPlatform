"""
认证相关API
"""
from flask import request, g
from flask_restx import Namespace, Resource, fields
from app.models import Tenant, User
from app.utils.errors import success_response, error_response
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

        # 查询用户可访问的租户列表
        # TODO: 从 tenant_users 表查询用户关联的租户
        # 这里简化处理，返回所有激活的租户
        tenants = Tenant.query.filter_by(
            is_deleted=False,
            is_active=True,
            status='active'
        ).all()

        # 生成token（简化处理，实际应使用JWT）
        token = f"token_{user.id}_{username}"

        return success_response(data={
            'token': token,
            'user': user.to_dict(),
            'tenants': [tenant.to_dict() for tenant in tenants]
        }, message='登录成功')


@auth_ns.route('/tenants')
class AuthTenantsAPI(Resource):
    @auth_ns.doc('get_user_tenants')
    def get(self):
        """获取当前用户可访问的租户列表"""
        # TODO: 从token或session中获取用户ID
        # 这里简化处理
        user_id = 1

        # 查询用户可访问的租户列表
        tenants = Tenant.query.filter_by(
            is_deleted=False,
            is_active=True
        ).all()

        return success_response(data={
            'tenants': [tenant.to_dict() for tenant in tenants]
        })


@auth_ns.route('/select-tenant')
class AuthSelectTenantAPI(Resource):
    @auth_ns.doc('select_tenant')
    @auth_ns.expect(tenant_select_model)
    def post(self):
        """选择租户"""
        data = request.get_json()
        tenant_id = data.get('tenant_id')

        # 验证租户是否存在
        tenant = Tenant.query.filter_by(
            id=tenant_id,
            is_deleted=False,
            is_active=True
        ).first()

        if not tenant:
            return error_response(message='租户不存在或已停用', code=404)

        # TODO: 验证用户是否有权访问该租户

        # 设置当前租户
        g.tenant_id = tenant_id
        g.tenant = tenant

        return success_response(data=tenant.to_dict(), message='租户选择成功')

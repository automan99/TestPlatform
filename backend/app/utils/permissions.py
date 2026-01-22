"""
权限装饰器和工具函数
实现基于角色的访问控制 (RBAC)
"""
from functools import wraps
from flask import request, g, jsonify
from app.models.user import User
from app.models.tenant import Tenant, TenantUser


def get_current_user():
    """获取当前登录用户"""
    from app.utils.jwt_utils import verify_token

    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None

    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return None

    user_id = payload.get('user_id')
    return User.query.get(user_id)


def get_current_tenant_id():
    """获取当前租户ID（从请求头）"""
    return request.headers.get('X-Tenant-ID', type=int)


def require_super_admin(f):
    """要求超级管理员权限"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({'success': False, 'message': '未登录或登录已过期'}), 401

        if not user.is_super_admin():
            return jsonify({'success': False, 'message': '需要超级管理员权限'}), 403

        g.current_user = user
        return f(*args, **kwargs)
    return decorated_function


def require_tenant_admin(f):
    """要求租户管理员权限（owner或admin角色）"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({'success': False, 'message': '未登录或登录已过期'}), 401

        # 超级管理员拥有所有权限
        if user.is_super_admin():
            g.current_user = user
            g.is_super_admin = True
            return f(*args, **kwargs)

        tenant_id = get_current_tenant_id()
        if not tenant_id:
            return jsonify({'success': False, 'message': '缺少租户信息'}), 400

        # 检查是否是租户管理员
        if not user.is_tenant_admin(tenant_id):
            return jsonify({'success': False, 'message': '需要租户管理员权限'}), 403

        g.current_user = user
        g.current_tenant_id = tenant_id
        g.is_super_admin = False
        return f(*args, **kwargs)
    return decorated_function


def require_tenant_member(f):
    """要求租户成员权限（任何角色）"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({'success': False, 'message': '未登录或登录已过期'}), 401

        # 超级管理员拥有所有权限
        if user.is_super_admin():
            g.current_user = user
            g.is_super_admin = True
            return f(*args, **kwargs)

        tenant_id = get_current_tenant_id()
        if not tenant_id:
            return jsonify({'success': False, 'message': '缺少租户信息'}), 400

        # 检查是否是租户成员
        tenant_role = user.get_tenant_role(tenant_id)
        if not tenant_role:
            return jsonify({'success': False, 'message': '您不是该租户的成员'}), 403

        g.current_user = user
        g.current_tenant_id = tenant_id
        g.current_tenant_role = tenant_role
        g.is_super_admin = False
        return f(*args, **kwargs)
    return decorated_function


def can_manage_tenant(user, tenant_id):
    """检查用户是否可以管理指定租户"""
    # 超级管理员可以管理所有租户
    if user.is_super_admin():
        return True

    # 检查是否是租户的管理员
    return user.is_tenant_admin(tenant_id)


def can_manage_user(user, target_user_id, tenant_id):
    """检查用户是否可以管理目标用户"""
    # 超级管理员可以管理所有用户
    if user.is_super_admin():
        return True

    # 租户管理员只能管理本租户的普通用户
    if user.is_tenant_admin(tenant_id):
        # 获取目标用户在租户中的角色
        target_user = User.query.get(target_user_id)
        if not target_user:
            return False

        target_role = target_user.get_tenant_role(tenant_id)
        # 只能管理 member 角色的用户，不能管理 owner/admin
        return target_role == 'member'

    return False


def get_user_accessible_tenants(user):
    """获取用户可访问的租户列表"""
    # 超级管理员可以访问所有租户
    if user.is_super_admin():
        return Tenant.query.filter_by(is_deleted=False).all()

    # 普通用户只能访问自己所属的租户
    tenant_users = TenantUser.query.filter_by(
        user_id=user.id,
        is_deleted=False
    ).all()

    tenants = []
    for tu in tenant_users:
        tenant = Tenant.query.get(tu.tenant_id)
        if tenant and not tenant.is_deleted:
            tenants.append(tenant)

    return tenants


def check_tenant_user_limit(tenant_id):
    """检查租户用户数量是否已达到上限"""
    tenant = Tenant.query.get(tenant_id)
    if not tenant:
        return True, '租户不存在'

    current_count = TenantUser.query.filter_by(
        tenant_id=tenant_id,
        is_deleted=False
    ).count()

    if current_count >= tenant.max_users:
        return False, f'租户用户数量已达上限（{tenant.max_users}）'

    return True, None


def get_tenant_users_query(tenant_id, include_deleted=False):
    """获取租户用户查询"""
    query = TenantUser.query.filter_by(tenant_id=tenant_id)

    if not include_deleted:
        query = query.filter_by(is_deleted=False)

    return query

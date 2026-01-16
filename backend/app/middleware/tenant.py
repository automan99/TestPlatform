"""
租户中间件
用于处理多租户请求过滤
"""
from flask import g, request
from app.models import Tenant


def set_tenant_context(f):
    """
    设置租户上下文装饰器
    从请求头或参数中获取租户ID，并设置到 g 对象中
    """
    def wrapper(*args, **kwargs):
        # 尝试从请求头获取租户ID
        tenant_id = request.headers.get('X-Tenant-ID')

        # 如果请求头没有，尝试从查询参数获取
        if not tenant_id:
            tenant_id = request.args.get('tenant_id')

        # 如果都没有，从认证信息中获取用户的默认租户
        if not tenant_id:
            # TODO: 从认证 token 中获取用户ID和默认租户
            # 这里暂时跳过，等认证系统完善后再处理
            pass

        # 设置租户ID到 g 对象
        if tenant_id:
            try:
                tenant_id = int(tenant_id)
                # 验证租户是否存在且激活
                tenant = Tenant.query.filter_by(
                    id=tenant_id,
                    is_deleted=False,
                    is_active=True,
                    status='active'
                ).first()

                if tenant:
                    g.tenant_id = tenant_id
                    g.tenant = tenant
                else:
                    g.tenant_id = None
                    g.tenant = None
            except (ValueError, TypeError):
                g.tenant_id = None
                g.tenant = None
        else:
            g.tenant_id = None
            g.tenant = None

        return f(*args, **kwargs)

    # 保留原始函数的名称和文档
    wrapper.__name__ = f.__name__
    wrapper.__doc__ = f.__doc__
    return wrapper


def require_tenant(f):
    """
    要求租户上下文装饰器
    如果请求没有租户上下文，则返回错误
    """
    def wrapper(*args, **kwargs):
        if not hasattr(g, 'tenant_id') or g.tenant_id is None:
            from app.utils import error_response
            return error_response(message='缺少租户上下文', code=400)

        return f(*args, **kwargs)

    wrapper.__name__ = f.__name__
    wrapper.__doc__ = f.__doc__
    return wrapper


def filter_by_tenant(query):
    """
    根据租户过滤查询

    使用示例:
        query = TestCase.query
        query = filter_by_tenant(query)
        results = query.all()
    """
    if hasattr(g, 'tenant_id') and g.tenant_id is not None:
        return query.filter_by(tenant_id=g.tenant_id)
    return query


def get_current_tenant():
    """
    获取当前租户

    返回: Tenant 对象或 None
    """
    return getattr(g, 'tenant', None)


def get_current_tenant_id():
    """
    获取当前租户ID

    返回: 租户ID或 None
    """
    return getattr(g, 'tenant_id', None)

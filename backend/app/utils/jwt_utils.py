"""
JWT 工具函数
用于生成和验证 JWT token
"""
import jwt
from datetime import datetime, timedelta
from flask import current_app


def generate_token(user_id, username, expires_in=None):
    """
    生成 JWT token

    Args:
        user_id: 用户ID
        username: 用户名
        expires_in: 过期时间（秒），默认7天
    """
    if expires_in is None:
        expires_in = 7 * 24 * 60 * 60  # 7天

    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.utcnow() + timedelta(seconds=expires_in),
        'iat': datetime.utcnow()
    }

    # 从配置中获取密钥，如果没有配置则使用默认值
    secret_key = current_app.config.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production')

    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token


def verify_token(token):
    """
    验证 JWT token

    Args:
        token: JWT token

    Returns:
        解码后的 payload，验证失败返回 None
    """
    try:
        secret_key = current_app.config.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        # Token 已过期
        return None
    except jwt.InvalidTokenError:
        # Token 无效
        return None


def refresh_token(old_token):
    """
    刷新 token

    Args:
        old_token: 旧的 token

    Returns:
        新的 token
    """
    payload = verify_token(old_token)
    if not payload:
        return None

    # 生成新 token
    return generate_token(
        user_id=payload['user_id'],
        username=payload['username']
    )

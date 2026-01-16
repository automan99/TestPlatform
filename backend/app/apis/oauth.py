"""
OAuth2 认证集成
"""
from flask import request
from flask_restx import Namespace, Resource
from app.utils.errors import success_response, error_response
from app.models import User, Tenant
from app import db
from datetime import datetime
from urllib.parse import urlencode
import urllib.request
import json

# 创建命名空间
oauth_ns = Namespace('oauth', description='OAuth2认证接口')

# OAuth2配置（从数据库或配置文件读取）
OAUTH_PROVIDERS = {
    'github': {
        'name': 'GitHub',
        'auth_url': 'https://github.com/login/oauth/authorize',
        'token_url': 'https://github.com/login/oauth/access_token',
        'user_url': 'https://api.github.com/user',
        'client_id': '',  # 需要配置
        'client_secret': '',  # 需要配置
        'scope': 'user:email'
    },
    'gitee': {
        'name': 'Gitee',
        'auth_url': 'https://gitee.com/oauth/authorize',
        'token_url': 'https://gitee.com/oauth/token',
        'user_url': 'https://gitee.com/api/v5/user',
        'client_id': '',  # 需要配置
        'client_secret': '',  # 需要配置
        'scope': 'user_info'
    },
    'gitlab': {
        'name': 'GitLab',
        'auth_url': 'https://gitlab.com/oauth/authorize',
        'token_url': 'https://gitlab.com/oauth/token',
        'user_url': 'https://gitlab.com/api/v4/user',
        'client_id': '',  # 需要配置
        'client_secret': '',  # 需要配置
        'scope': 'read_user'
    },
    'dingtalk': {
        'name': '钉钉',
        'auth_url': 'https://login.dingtalk.com/oauth2/auth',
        'token_url': 'https://api.dingtalk.com/v1.0/oauth2/userAccessToken',
        'user_url': 'https://api.dingtalk.com/v1.0/contact/users/me',
        'client_id': '',  # 需要配置
        'client_secret': '',  # 需要配置
        'scope': 'openid corpid'
    }
}


def get_oauth_config(provider):
    """获取OAuth配置（实际应该从数据库读取）"""
    # TODO: 从数据库或环境变量读取配置
    from app.config import Config
    config_key = f'OAUTH_{provider.upper()}'
    if hasattr(Config, config_key):
        return getattr(Config, config_key)
    return OAUTH_PROVIDERS.get(provider, {})


def http_post(url, data=None, headers=None):
    """发送HTTP POST请求"""
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8') if data else None,
        headers=headers or {},
        method='POST'
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode('utf-8')), response.status
    except urllib.error.HTTPError as e:
        return json.loads(e.read().decode('utf-8')), e.code
    except Exception as e:
        return {'error': str(e)}, 500


def http_get(url, headers=None):
    """发送HTTP GET请求"""
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode('utf-8')), response.status
    except urllib.error.HTTPError as e:
        return json.loads(e.read().decode('utf-8')), e.code
    except Exception as e:
        return {'error': str(e)}, 500


@oauth_ns.route('/<provider>/authorize')
class OAuthAuthorizeAPI(Resource):
    @oauth_ns.doc('oauth_authorize')
    def get(self, provider):
        """获取OAuth授权URL"""
        config = get_oauth_config(provider)
        if not config or not config.get('client_id'):
            return error_response(message=f'{provider} 未配置')

        # 构建授权URL
        params = {
            'client_id': config['client_id'],
            'redirect_uri': f"{request.host_url.rstrip('/')}/api/oauth/{provider}/callback",
            'response_type': 'code',
            'scope': config.get('scope', ''),
            'state': 'random_state_string'  # 实际应该生成随机state并验证
        }

        auth_url = f"{config['auth_url']}?{urlencode(params)}"

        return success_response(data={'auth_url': auth_url})


@oauth_ns.route('/<provider>/callback')
class OAuthCallbackAPI(Resource):
    @oauth_ns.doc('oauth_callback')
    def get(self, provider):
        """OAuth回调处理"""
        code = request.args.get('code')
        state = request.args.get('state')

        if not code:
            return error_response(message='授权失败', code=400)

        try:
            config = get_oauth_config(provider)
            if not config:
                return error_response(message=f'{provider} 未配置')

            if provider == 'github':
                return self._handle_github_callback(config, code)
            elif provider == 'gitee':
                return self._handle_gitee_callback(config, code)
            elif provider == 'gitlab':
                return self._handle_gitlab_callback(config, code)
            elif provider == 'dingtalk':
                return error_response(message='钉钉OAuth暂不支持网页授权')
            else:
                return error_response(message='不支持的OAuth平台')

        except Exception as e:
            return error_response(message=f'OAuth登录失败: {str(e)}')

    def _handle_github_callback(self, config, code):
        """处理GitHub回调"""
        # 1. 获取access_token
        token_data, status = http_post(
            config['token_url'],
            data={
                'client_id': config['client_id'],
                'client_secret': config['client_secret'],
                'code': code
            },
            headers={'Accept': 'application/json'}
        )

        if status != 200 or 'access_token' not in token_data:
            return error_response(message='获取token失败')

        access_token = token_data['access_token']

        # 2. 获取用户信息
        user_data, status = http_get(
            config['user_url'],
            headers={'Authorization': f'token {access_token}', 'User-Agent': 'TestPlatform'}
        )

        if status != 200:
            return error_response(message='获取用户信息失败')

        # 3. 创建或获取用户
        user = self._get_or_create_oauth_user('github', str(user_data['id']), user_data)

        # 4. 生成token并返回
        token = f"oauth_{user.id}_github"

        return success_response(data={
            'token': token,
            'user': user.to_dict(),
            'oauth_provider': 'github'
        }, message='登录成功')

    def _handle_gitee_callback(self, config, code):
        """处理Gitee回调"""
        # 1. 获取access_token
        token_data, status = http_post(
            config['token_url'],
            data={
                'client_id': config['client_id'],
                'client_secret': config['client_secret'],
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': f"{request.host_url.rstrip('/')}/api/oauth/gitee/callback"
            },
            headers={'Accept': 'application/json'}
        )

        if status != 200 or 'access_token' not in token_data:
            return error_response(message='获取token失败')

        access_token = token_data['access_token']

        # 2. 获取用户信息
        user_data, status = http_get(
            config['user_url'],
            headers={'Authorization': f'token {access_token}', 'User-Agent': 'TestPlatform'}
        )

        if status != 200:
            return error_response(message='获取用户信息失败')

        # 3. 创建或获取用户
        user = self._get_or_create_oauth_user('gitee', str(user_data['id']), user_data)

        # 4. 生成token并返回
        token = f"oauth_{user.id}_gitee"

        return success_response(data={
            'token': token,
            'user': user.to_dict(),
            'oauth_provider': 'gitee'
        }, message='登录成功')

    def _handle_gitlab_callback(self, config, code):
        """处理GitLab回调"""
        # 1. 获取access_token
        token_data, status = http_post(
            config['token_url'],
            data={
                'client_id': config['client_id'],
                'client_secret': config['client_secret'],
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': f"{request.host_url.rstrip('/')}/api/oauth/gitlab/callback"
            },
            headers={'Accept': 'application/json'}
        )

        if status != 200 or 'access_token' not in token_data:
            return error_response(message='获取token失败')

        access_token = token_data['access_token']

        # 2. 获取用户信息
        user_data, status = http_get(
            config['user_url'],
            headers={'Authorization': f'Bearer {access_token}', 'User-Agent': 'TestPlatform'}
        )

        if status != 200:
            return error_response(message='获取用户信息失败')

        # 3. 创建或获取用户
        user = self._get_or_create_oauth_user('gitlab', str(user_data['id']), user_data)

        # 4. 生成token并返回
        token = f"oauth_{user.id}_gitlab"

        return success_response(data={
            'token': token,
            'user': user.to_dict(),
            'oauth_provider': 'gitlab'
        }, message='登录成功')

    def _get_or_create_oauth_user(self, provider, oauth_user_id, user_data):
        """获取或创建OAuth用户"""
        # 查找已存在的用户
        user = User.query.filter_by(
            oauth_provider=provider,
            oauth_user_id=oauth_user_id
        ).first()

        if not user:
            # 创建新用户
            if provider == 'github':
                username = user_data.get('login') or f"{provider}_{oauth_user_id}"
                real_name = user_data.get('name') or username
                email = user_data.get('email') or ''
                avatar = user_data.get('avatar_url')
            elif provider == 'gitee':
                username = user_data.get('login') or f"{provider}_{oauth_user_id}"
                real_name = user_data.get('name') or username
                email = user_data.get('email') or ''
                avatar = user_data.get('avatar_url')
            elif provider == 'gitlab':
                # GitLab用户信息字段
                username = user_data.get('username') or f"{provider}_{oauth_user_id}"
                real_name = user_data.get('name') or username
                email = user_data.get('email') or ''
                avatar = user_data.get('avatar_url')
            else:
                username = f"{provider}_{oauth_user_id}"
                real_name = username
                email = ''
                avatar = None

            # 确保用户名唯一
            counter = 1
            original_username = username
            while User.query.filter_by(username=username).first():
                username = f"{original_username}_{counter}"
                counter += 1

            user = User(
                username=username,
                real_name=real_name,
                email=email,
                avatar=avatar,
                oauth_provider=provider,
                oauth_user_id=oauth_user_id,
                status='active'
            )
            user.set_password('oauth_user_123')  # OAuth用户设置默认密码
            db.session.add(user)
            db.session.commit()

        return user


@oauth_ns.route('/config')
class OAuthConfigAPI(Resource):
    @oauth_ns.doc('get_oauth_config')
    def get(self):
        """获取OAuth配置（前端需要知道哪些平台可用）"""
        # TODO: 从数据库读取实际配置
        providers = []
        for key, config in OAUTH_PROVIDERS.items():
            if config.get('client_id'):  # 只显示已配置的平台
                providers.append({
                    'key': key,
                    'name': config['name']
                })
        return success_response(data={'providers': providers})

    @oauth_ns.doc('update_oauth_config')
    def post(self):
        """更新OAuth配置"""
        try:
            data = request.get_json()
            provider = data.get('provider')
            client_id = data.get('client_id')
            client_secret = data.get('client_secret')

            if not provider or not client_id or not client_secret:
                return error_response(message='参数不完整')

            # TODO: 保存到数据库
            # 这里简化处理，实际应该保存到数据库或配置文件

            # 更新内存中的配置
            if provider in OAUTH_PROVIDERS:
                OAUTH_PROVIDERS[provider]['client_id'] = client_id
                OAUTH_PROVIDERS[provider]['client_secret'] = client_secret

            return success_response(message='配置已更新')
        except Exception as e:
            return error_response(message=f'配置更新失败: {str(e)}')

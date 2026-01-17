"""
测试管理平台 - 应用工厂模式
"""
from flask import Flask, g, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_restx import Api
import os

# 初始化扩展
db = SQLAlchemy()
migrate = Migrate()
cors = CORS()


def create_app(config_name=None):
    """
    应用工厂函数

    Args:
        config_name: 配置名称 ('development', 'production', 'testing')

    Returns:
        Flask应用实例
    """
    app = Flask(__name__)

    # 加载配置
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    from app.config import config
    app.config.from_object(config[config_name])

    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, origins=app.config['CORS_ORIGINS'])

    # 创建上传文件夹
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # 注册API
    from app.apis import api_blueprint
    app.register_blueprint(api_blueprint)

    # 注册错误处理器
    from app.utils.errors import register_error_handlers
    register_error_handlers(app)

    # 注册认证中间件
    @app.before_request
    def auth_middleware():
        """认证中间件 - 验证token并设置g.user_id"""
        # 跳过不需要认证的路径
        skip_paths = ['/api/auth/login', '/api/oauth', '/api/doc', '/api/favicon.ico']
        if any(request.path.startswith(path) for path in skip_paths):
            return

        # 从Authorization header获取token
        auth_header = request.headers.get('Authorization', '')
        if not auth_header or not auth_header.startswith('Bearer '):
            return  # 没有token，继续处理（某些接口可能不需要认证）

        token = auth_header.replace('Bearer ', '')

        # 验证token格式：token_{user_id}_{username}
        if token.startswith('token_'):
            try:
                parts = token.split('_')
                if len(parts) >= 3:
                    user_id = int(parts[1])
                    g.user_id = user_id
            except (ValueError, IndexError):
                pass  # token格式错误，忽略

    return app

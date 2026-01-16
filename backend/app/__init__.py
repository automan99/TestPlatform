"""
测试管理平台 - 应用工厂模式
"""
from flask import Flask
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

    return app

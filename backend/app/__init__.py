"""
测试管理平台 - 应用工厂模式
"""
from flask import Flask, g, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_restx import Api
import os
import logging

# 初始化扩展
db = SQLAlchemy()
migrate = Migrate()
cors = CORS()

# 配置日志
logger = logging.getLogger(__name__)


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

    # 自动运行数据库迁移
    with app.app_context():
        auto_upgrade_database()

    return app


def auto_upgrade_database():
    """自动升级数据库到最新版本"""
    try:
        from alembic.config import Config
        from alembic import command
        import traceback

        # 获取迁移目录的绝对路径
        migrations_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'migrations')

        # 检查迁移目录是否存在
        if not os.path.exists(migrations_dir):
            logger.info("Migrations directory not found, skipping auto-upgrade")
            return

        # 配置alembic
        alembic_cfg = Config()
        alembic_cfg.set_main_option('sqlalchemy.url', db.engine.url.render_as_string(hide_password=False))
        alembic_cfg.set_main_option('script_location', migrations_dir)

        logger.info(f"Migrations directory: {migrations_dir}")

        # 获取当前版本
        try:
            current = command.current(alembic_cfg)
            logger.info(f"Current database version: {current}")
        except Exception as e:
            current = None
            logger.info(f"No database version found (may be new database): {e}")

        # 尝试升级数据库
        try:
            logger.info("Attempting database upgrade...")
            command.upgrade(alembic_cfg, 'head')
            logger.info("Database auto-upgrade completed successfully")
        except Exception as upgrade_error:
            error_msg = str(upgrade_error)
            logger.error(f"Database upgrade error type: {type(upgrade_error).__name__}")
            logger.error(f"Database upgrade error: {error_msg}")
            logger.error(f"Traceback: {traceback.format_exc()}")

            # 多头错误是预期的，记录为INFO
            if "Multiple head revisions" in error_msg:
                logger.info("Multiple migration heads detected, skipping auto-upgrade")
            elif "Table" in error_msg and "already exists" in error_msg:
                logger.info("Tables already exist, database may have been initialized manually")

    except Exception as e:
        logger.error(f"Database auto-upgrade error: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error args: {e.args}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")


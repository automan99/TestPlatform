"""
测试管理平台 - 配置文件
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    """基础配置"""
    # 密钥
    SECRET_KEY = os.getenv('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # JWT配置
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)

    # 数据库配置
    DB_TYPE = os.getenv('DB_TYPE', 'mysql')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '3306')
    DB_NAME = os.getenv('DB_NAME', 'testp')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'liyang123')

    # 构建数据库URI
    if DB_TYPE == 'mysql':
        SQLALCHEMY_DATABASE_URI = (
            f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@'
            f'{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4'
        )
    elif DB_TYPE == 'postgresql':
        SQLALCHEMY_DATABASE_URI = (
            f'postgresql://{DB_USER}:{DB_PASSWORD}@'
            f'{DB_HOST}:{DB_PORT}/{DB_NAME}'
        )
    else:
        # 默认使用SQLite
        SQLALCHEMY_DATABASE_URI = 'sqlite:///test_management.db'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # API配置
    API_TITLE = os.getenv('API_TITLE', '测试管理平台API')
    API_VERSION = os.getenv('API_VERSION', 'v1')
    API_PREFIX = os.getenv('API_PREFIX', '/api')

    # CORS配置
    CORS_ORIGINS = ['http://localhost:5173', 'http://localhost:5174', 'http://localhost:3000']

    # 分页配置
    ITEMS_PER_PAGE = 20

    # 文件上传配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')

    # Git技能仓库配置
    # Git 仓库存储目录，可通过 .env 配置 GIT_REPOS_DIR
    GIT_REPOS_DIR = os.getenv('GIT_REPOS_DIR', os.path.join(os.path.dirname(__file__), 'git_repos'))
    # 加密密钥，用于加密 Git 凭证
    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
    # 加密密钥种子（用于派生密钥）
    ENCRYPTION_KEY_SEED = os.getenv('ENCRYPTION_KEY_SEED', 'default-seed-change-in-production')

    # Session配置
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

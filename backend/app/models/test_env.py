"""
测试环境模型
"""
from datetime import datetime
from app import db


class TestEnvironment(db.Model):
    """测试环境模型"""
    __tablename__ = 'test_environments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    env_code = db.Column(db.String(50), unique=True)  # 环境编码
    env_type = db.Column(db.String(50), default='testing')  # dev, testing, staging, production
    description = db.Column(db.Text)
    base_url = db.Column(db.String(500))  # 基础URL
    db_connection = db.Column(db.Text)  # 数据库连接信息 (JSON格式)
    status = db.Column(db.String(20), default='active')  # active, inactive, maintenance
    is_active = db.Column(db.Boolean, default=True)
    project_id = db.Column(db.Integer, nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(100))
    updated_by = db.Column(db.String(100))

    # 关系
    resources = db.relationship('EnvironmentResource', backref='environment', lazy='dynamic',
                               cascade='all, delete-orphan')

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'env_code': self.env_code,
            'env_type': self.env_type,
            'description': self.description,
            'base_url': self.base_url,
            'db_connection': self.db_connection,
            'status': self.status,
            'is_active': self.is_active,
            'project_id': self.project_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'resources_count': self.resources.count()
        }


class EnvironmentResource(db.Model):
    """环境资源模型 - 测试执行主机/资源"""
    __tablename__ = 'environment_resources'

    id = db.Column(db.Integer, primary_key=True)
    environment_id = db.Column(db.Integer, db.ForeignKey('test_environments.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    resource_type = db.Column(db.String(50), default='server')  # server, database, cache, message_queue
    host = db.Column(db.String(200))  # 主机地址
    port = db.Column(db.Integer)
    username = db.Column(db.String(100))
    password = db.Column(db.String(200))  # 加密存储
    os_type = db.Column(db.String(50))  # 操作系统类型
    os_version = db.Column(db.String(100))  # 操作系统版本
    cpu_cores = db.Column(db.Integer)
    memory_gb = db.Column(db.Integer)
    disk_gb = db.Column(db.Integer)
    status = db.Column(db.String(20), default='online')  # online, offline, busy, error
    last_check_time = db.Column(db.DateTime)  # 最后一次状态检查时间
    description = db.Column(db.Text)
    tags = db.Column(db.String(500))
    capabilities = db.Column(db.Text)  # 能力描述 (JSON格式)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(100))
    updated_by = db.Column(db.String(100))

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'environment_id': self.environment_id,
            'name': self.name,
            'resource_type': self.resource_type,
            'host': self.host,
            'port': self.port,
            'username': self.username,
            'os_type': self.os_type,
            'os_version': self.os_version,
            'cpu_cores': self.cpu_cores,
            'memory_gb': self.memory_gb,
            'disk_gb': self.disk_gb,
            'status': self.status,
            'last_check_time': self.last_check_time.isoformat() if self.last_check_time else None,
            'description': self.description,
            'tags': self.tags,
            'capabilities': self.capabilities,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'updated_by': self.updated_by
        }

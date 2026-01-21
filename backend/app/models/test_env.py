"""
测试环境模型
"""
from datetime import datetime
from app import db


class TestEnvironment(db.Model):
    """测试环境模型"""
    __tablename__ = 'test_environments'

    id = db.Column(db.Integer, primary_key=True, comment='主键ID')
    name = db.Column(db.String(200), nullable=False, comment='环境名称')
    env_code = db.Column(db.String(50), unique=True, comment='环境编码')
    env_type = db.Column(db.String(50), default='testing', comment='环境类型: dev, testing, staging, production')
    description = db.Column(db.Text, comment='描述')
    base_url = db.Column(db.String(500), comment='基础URL')
    db_connection = db.Column(db.Text, comment='数据库连接信息(JSON格式)')
    status = db.Column(db.String(20), default='active', comment='状态: active, inactive, maintenance')
    is_active = db.Column(db.Boolean, default=True, comment='是否激活')
    project_id = db.Column(db.Integer, nullable=True, index=True, comment='所属项目ID')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    created_by = db.Column(db.String(100), comment='创建人')
    updated_by = db.Column(db.String(100), comment='更新人')

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

    id = db.Column(db.Integer, primary_key=True, comment='主键ID')
    environment_id = db.Column(db.Integer, db.ForeignKey('test_environments.id'), nullable=False, comment='环境ID')
    name = db.Column(db.String(200), nullable=False, comment='资源名称')
    resource_type = db.Column(db.String(50), default='server', comment='资源类型: server, database, cache, message_queue')
    host = db.Column(db.String(200), comment='主机地址')
    port = db.Column(db.Integer, comment='端口号')
    username = db.Column(db.String(100), comment='用户名')
    password = db.Column(db.String(200), comment='密码(加密存储)')
    os_type = db.Column(db.String(50), comment='操作系统类型')
    os_version = db.Column(db.String(100), comment='操作系统版本')
    cpu_cores = db.Column(db.Integer, comment='CPU核心数')
    memory_gb = db.Column(db.Integer, comment='内存(GB)')
    disk_gb = db.Column(db.Integer, comment='磁盘(GB)')
    status = db.Column(db.String(20), default='online', comment='状态: online, offline, busy, error')
    last_check_time = db.Column(db.DateTime, comment='最后一次状态检查时间')
    description = db.Column(db.Text, comment='描述')
    tags = db.Column(db.String(500), comment='标签')
    capabilities = db.Column(db.Text, comment='能力描述(JSON格式)')
    is_active = db.Column(db.Boolean, default=True, comment='是否激活')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    created_by = db.Column(db.String(100), comment='创建人')
    updated_by = db.Column(db.String(100), comment='更新人')

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

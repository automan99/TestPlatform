"""
Skill 模型 - AI技能/指令集
"""
from datetime import datetime
from app import db


class Skill(db.Model):
    """Skill模型"""
    __tablename__ = 'skills'

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=True, index=True)

    # 基础信息
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(50), unique=True, index=True)
    description = db.Column(db.Text)
    mcp_id = db.Column(db.Integer, db.ForeignKey('mcp_servers.id'), nullable=True, index=True)

    # 执行配置
    script_content = db.Column(db.Text)
    script_type = db.Column(db.String(50), default='python')  # python, javascript, yaml, json

    # 参数定义
    params_schema = db.Column(db.Text)  # JSON格式的参数结构定义
    params_example = db.Column(db.Text)  # JSON格式的参数示例

    # 配置选项
    timeout = db.Column(db.Integer, default=60)
    log_enabled = db.Column(db.Boolean, default=True)
    retry_count = db.Column(db.Integer, default=1)

    # 权限控制
    allowed_roles = db.Column(db.Text)  # JSON格式的允许角色列表

    # 版本管理
    version = db.Column(db.String(20), default='1.0.0')
    previous_versions = db.Column(db.Text)  # JSON格式的历史版本

    # 统计数据
    usage_count = db.Column(db.Integer, default=0)
    last_used_at = db.Column(db.DateTime)
    last_execution_result = db.Column(db.Text)  # JSON格式的最后一次执行结果

    # 状态管理
    status = db.Column(db.String(20), default='active')  # active, inactive, error
    is_enabled = db.Column(db.Boolean, default=True)

    # 元数据
    tags = db.Column(db.String(500))

    # 软删除
    is_deleted = db.Column(db.Boolean, default=False)

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(100))
    updated_by = db.Column(db.String(100))

    # 关系
    tenant = db.relationship('Tenant', backref='skills')

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'mcp_id': self.mcp_id,
            'mcp_name': self.mcp_server.name if self.mcp_server else None,
            'script_content': self.script_content,
            'script_type': self.script_type,
            'params_schema': self.params_schema,
            'params_example': self.params_example,
            'timeout': self.timeout,
            'log_enabled': self.log_enabled,
            'retry_count': self.retry_count,
            'allowed_roles': self.allowed_roles,
            'version': self.version,
            'previous_versions': self.previous_versions,
            'usage_count': self.usage_count,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
            'last_execution_result': self.last_execution_result,
            'status': self.status,
            'is_enabled': self.is_enabled,
            'tags': self.tags,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'updated_by': self.updated_by
        }

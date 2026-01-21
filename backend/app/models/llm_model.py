"""
LLM模型配置
支持常见大语言模型配置管理
"""
from datetime import datetime
from app import db


class LLMModel(db.Model):
    """LLM模型配置"""
    __tablename__ = 'llm_models'

    id = db.Column(db.Integer, primary_key=True)
    # 基本信息
    name = db.Column(db.String(100), nullable=False, comment='模型名称')
    provider = db.Column(db.String(50), nullable=False, comment='提供商: openai, anthropic, azure, etc.')
    model_id = db.Column(db.String(100), nullable=False, comment='模型ID: gpt-4, claude-3-opus-20240229, etc.')

    # API配置
    api_key = db.Column(db.Text, comment='API密钥(加密存储)')
    api_base = db.Column(db.String(500), comment='API基础URL')
    api_version = db.Column(db.String(50), comment='API版本(用于Azure等)')

    # 模型参数
    temperature = db.Column(db.Float, default=0.7, comment='温度参数')
    max_tokens = db.Column(db.Integer, default=4096, comment='最大token数')
    top_p = db.Column(db.Float, default=1.0, comment='top_p参数')
    frequency_penalty = db.Column(db.Float, default=0.0, comment='频率惩罚')
    presence_penalty = db.Column(db.Float, default=0.0, comment='存在惩罚')

    # 其他配置
    is_default = db.Column(db.Boolean, default=False, comment='是否为默认模型')
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    description = db.Column(db.Text, comment='描述')

    # 元数据
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), comment='创建人')

    # 关系
    creator = db.relationship('User', backref='llm_models')

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'provider': self.provider,
            'model_id': self.model_id,
            'api_key': self.api_key,  # 注意：返回时可能需要脱敏
            'api_base': self.api_base,
            'api_version': self.api_version,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'top_p': self.top_p,
            'frequency_penalty': self.frequency_penalty,
            'presence_penalty': self.presence_penalty,
            'is_default': self.is_default,
            'is_enabled': self.is_enabled,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by
        }

    def __repr__(self):
        return f'<LLMModel {self.name} ({self.provider}/{self.model_id})>'

"""
Git 技能仓库模型
"""
from datetime import datetime
from app import db


class GitCredential(db.Model):
    """Git凭证模型 - 用于存储Git仓库认证信息"""
    __tablename__ = 'git_credentials'

    id = db.Column(db.Integer, primary_key=True)

    # 基本信息
    name = db.Column(db.String(100), nullable=False, comment='凭证名称')
    description = db.Column(db.String(500), comment='凭证描述')

    # 认证类型
    auth_type = db.Column(db.String(20), nullable=False, comment='认证类型: token, ssh_key')

    # Token 认证
    github_token = db.Column(db.Text, comment='GitHub Personal Access Token (加密存储)')

    # SSH 密钥认证
    ssh_key_content = db.Column(db.Text, comment='SSH私钥内容 (加密存储)')
    ssh_key_passphrase = db.Column(db.String(255), comment='SSH密钥密码 (可选,加密存储)')

    # GitHub 特定信息
    github_login = db.Column(db.String(100), comment='GitHub用户名')
    github_user_id = db.Column(db.String(50), comment='GitHub用户ID')

    # 状态
    is_valid = db.Column(db.Boolean, default=True, comment='凭证是否有效')
    last_verified_at = db.Column(db.DateTime, comment='最后验证时间')

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    created_by = db.Column(db.String(100), comment='创建人')

    # 关系
    repositories = db.relationship('SkillRepository', backref='credential', lazy='dynamic')

    def to_dict(self):
        """转换为字典（不包含敏感信息）"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'auth_type': self.auth_type,
            'github_login': self.github_login,
            'github_user_id': self.github_user_id,
            'is_valid': self.is_valid,
            'last_verified_at': self.last_verified_at.isoformat() if self.last_verified_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by
        }


class SkillRepository(db.Model):
    """技能仓库模型"""
    __tablename__ = 'skill_repositories'

    id = db.Column(db.Integer, primary_key=True)

    # 基本信息
    name = db.Column(db.String(100), nullable=False, comment='仓库名称')
    description = db.Column(db.String(500), comment='仓库描述')

    # Git 仓库配置
    git_url = db.Column(db.String(500), nullable=False, comment='Git仓库URL')
    branch = db.Column(db.String(100), default='main', comment='分支名称')
    skills_path = db.Column(db.String(500), default='/', comment='技能文件在仓库中的路径')

    # 认证配置
    auth_type = db.Column(db.String(20), default='public', comment='认证类型: public, token, ssh_key')
    git_credential_id = db.Column(db.Integer, db.ForeignKey('git_credentials.id'), comment='Git凭证ID')

    # 同步配置
    sync_mode = db.Column(db.String(20), default='manual', comment='同步模式: manual, scheduled, webhook')
    sync_interval = db.Column(db.Integer, default=60, comment='定时同步间隔(分钟)')
    webhook_secret = db.Column(db.String(100), comment='Webhook密钥')

    # 状态管理
    status = db.Column(db.String(20), default='idle', comment='状态: idle, syncing, success, error')
    last_sync_at = db.Column(db.DateTime, comment='最后同步时间')
    last_sync_status = db.Column(db.String(20), comment='最后同步状态: success, error')
    last_sync_message = db.Column(db.Text, comment='最后同步消息')
    skills_count = db.Column(db.Integer, default=0, comment='技能数量')

    # 配置选项
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    auto_sync = db.Column(db.Boolean, default=False, comment='是否自动同步')

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    created_by = db.Column(db.String(100), comment='创建人')

    # 关系
    skills = db.relationship('GitSkill', backref='repository', lazy='dynamic', cascade='all, delete-orphan')
    sync_logs = db.relationship('SkillSyncLog', backref='repository', lazy='dynamic', order_by='desc(SkillSyncLog.started_at)')

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'git_url': self.git_url,
            'branch': self.branch,
            'skills_path': self.skills_path,
            'auth_type': self.auth_type,
            'git_credential_id': self.git_credential_id,
            'sync_mode': self.sync_mode,
            'sync_interval': self.sync_interval,
            'status': self.status,
            'last_sync_at': self.last_sync_at.isoformat() if self.last_sync_at else None,
            'last_sync_status': self.last_sync_status,
            'last_sync_message': self.last_sync_message,
            'skills_count': self.skills_count,
            'is_enabled': self.is_enabled,
            'auto_sync': self.auto_sync,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by
        }


class GitSkill(db.Model):
    """Git技能模型"""
    __tablename__ = 'git_skills'

    id = db.Column(db.Integer, primary_key=True)

    # 关联
    repository_id = db.Column(db.Integer, db.ForeignKey('skill_repositories.id'), nullable=False, index=True)

    # 基本信息
    name = db.Column(db.String(200), nullable=False, comment='技能名称')
    code = db.Column(db.String(100), nullable=False, index=True, comment='技能代码')
    description = db.Column(db.Text, comment='技能描述')

    # 技能内容
    script_content = db.Column(db.Text, comment='技能内容')
    script_type = db.Column(db.String(50), comment='脚本类型: python, javascript, yaml, json')

    # 参数定义
    params_schema = db.Column(db.Text, comment='参数定义(JSON格式)')

    # Git 信息
    git_commit_hash = db.Column(db.String(50), comment='Git commit hash')
    git_commit_message = db.Column(db.Text, comment='Git commit message')
    git_commit_author = db.Column(db.String(100), comment='Git commit author')
    git_commit_date = db.Column(db.DateTime, comment='Git commit date')

    # 文件信息
    file_path = db.Column(db.String(500), comment='文件在仓库中的路径')

    # 统计数据
    usage_count = db.Column(db.Integer, default=0, comment='使用次数')
    last_used_at = db.Column(db.DateTime, comment='最后使用时间')

    # 状态
    status = db.Column(db.String(20), default='active', comment='状态: active, inactive, error')
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'repository_id': self.repository_id,
            'repository_name': self.repository.name if self.repository else None,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'script_content': self.script_content,
            'script_type': self.script_type,
            'params_schema': self.params_schema,
            'git_commit_hash': self.git_commit_hash,
            'git_commit_message': self.git_commit_message,
            'git_commit_author': self.git_commit_author,
            'git_commit_date': self.git_commit_date.isoformat() if self.git_commit_date else None,
            'file_path': self.file_path,
            'usage_count': self.usage_count,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
            'status': self.status,
            'is_enabled': self.is_enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class SkillSyncLog(db.Model):
    """技能同步日志模型"""
    __tablename__ = 'skill_sync_logs'

    id = db.Column(db.Integer, primary_key=True)

    # 关联
    repository_id = db.Column(db.Integer, db.ForeignKey('skill_repositories.id'), nullable=False, index=True)

    # 同步类型
    sync_type = db.Column(db.String(20), nullable=False, comment='同步类型: manual, scheduled, webhook')

    # 统计信息
    skills_added = db.Column(db.Integer, default=0, comment='新增技能数')
    skills_updated = db.Column(db.Integer, default=0, comment='更新技能数')
    skills_deleted = db.Column(db.Integer, default=0, comment='删除技能数')
    skills_error = db.Column(db.Integer, default=0, comment='错误技能数')

    # 执行信息
    status = db.Column(db.String(20), default='running', comment='状态: running, success, error, partial')
    error_message = db.Column(db.Text, comment='错误消息')
    started_at = db.Column(db.DateTime, default=datetime.utcnow, comment='开始时间')
    completed_at = db.Column(db.DateTime, comment='完成时间')
    duration = db.Column(db.Float, comment='执行时长(秒)')
    triggered_by = db.Column(db.String(100), comment='触发人/触发源')

    # Git 信息
    git_commit_hash = db.Column(db.String(50), comment='同步的commit hash')
    git_commit_message = db.Column(db.Text, comment='同步的commit message')

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'repository_id': self.repository_id,
            'sync_type': self.sync_type,
            'skills_added': self.skills_added,
            'skills_updated': self.skills_updated,
            'skills_deleted': self.skills_deleted,
            'skills_error': self.skills_error,
            'status': self.status,
            'error_message': self.error_message,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration': self.duration,
            'triggered_by': self.triggered_by,
            'git_commit_hash': self.git_commit_hash,
            'git_commit_message': self.git_commit_message
        }

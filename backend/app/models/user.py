"""
用户模型
"""
from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    """用户表"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True, comment='用户名')
    password_hash = db.Column(db.String(255), comment='密码哈希（OAuth用户可为空）')
    real_name = db.Column(db.String(100), comment='真实姓名')
    email = db.Column(db.String(100), comment='邮箱')
    phone = db.Column(db.String(20), comment='手机号')
    avatar = db.Column(db.String(255), comment='头像URL')
    status = db.Column(db.String(20), default='active', comment='状态: active-激活, disabled-禁用')
    is_admin = db.Column(db.Boolean, default=False, comment='是否管理员')
    # OAuth相关字段
    oauth_provider = db.Column(db.String(50), comment='OAuth提供商: github, gitee, dingtalk等')
    oauth_user_id = db.Column(db.String(100), comment='OAuth用户ID')
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    last_login_at = db.Column(db.DateTime, comment='最后登录时间')
    is_deleted = db.Column(db.Boolean, default=False, comment='是否删除')

    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'real_name': self.real_name,
            'email': self.email,
            'phone': self.phone,
            'avatar': self.avatar,
            'status': self.status,
            'is_admin': self.is_admin,
            'oauth_provider': self.oauth_provider,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'last_login_at': self.last_login_at.strftime('%Y-%m-%d %H:%M:%S') if self.last_login_at else None
        }

    def __repr__(self):
        return f'<User {self.username}>'

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

    # 全局角色 - 用于超级管理员
    role = db.Column(db.String(20), default='user', comment='全局角色: super_admin-超级管理员, user-普通用户')

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
            'role': self.role,
            'oauth_provider': self.oauth_provider,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'last_login_at': self.last_login_at.strftime('%Y-%m-%d %H:%M:%S') if self.last_login_at else None
        }

    def is_super_admin(self):
        """是否是超级管理员"""
        return self.role == 'super_admin'

    def get_tenant_role(self, tenant_id):
        """获取用户在指定租户中的角色"""
        tenant_user = self.tenant_users.filter_by(
            tenant_id=tenant_id,
            is_deleted=False
        ).first()
        return tenant_user.role if tenant_user else None

    def is_tenant_admin(self, tenant_id):
        """是否是租户管理员"""
        role = self.get_tenant_role(tenant_id)
        return role in ['owner', 'admin']

    def __repr__(self):
        return f'<User {self.username}>'

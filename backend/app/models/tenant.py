"""
租户模型
"""
from datetime import datetime
from app import db


class Tenant(db.Model):
    """租户表"""
    __tablename__ = 'tenants'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True, comment='租户名称')
    code = db.Column(db.String(50), nullable=False, unique=True, comment='租户代码')
    description = db.Column(db.Text, comment='描述')
    logo = db.Column(db.String(255), comment='Logo URL')
    status = db.Column(db.String(20), default='active', comment='状态: active-激活, suspended-暂停, expired-过期')
    is_active = db.Column(db.Boolean, default=True, comment='是否激活')
    max_users = db.Column(db.Integer, default=10, comment='最大用户数')
    max_projects = db.Column(db.Integer, default=5, comment='最大项目数')
    max_storage_gb = db.Column(db.Integer, default=10, comment='最大存储空间(GB)')
    expire_date = db.Column(db.Date, comment='过期日期')
    settings = db.Column(db.JSON, comment='租户设置(JSON)')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    created_by = db.Column(db.Integer, comment='创建人ID')
    updated_by = db.Column(db.Integer, comment='更新人ID')
    is_deleted = db.Column(db.Boolean, default=False, comment='是否删除')

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'logo': self.logo,
            'status': self.status,
            'is_active': self.is_active,
            'max_users': self.max_users,
            'max_projects': self.max_projects,
            'max_storage_gb': self.max_storage_gb,
            'expire_date': self.expire_date.strftime('%Y-%m-%d') if self.expire_date else None,
            'settings': self.settings,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
            'users_count': 0,  # TODO: 从 tenant_users 表统计
            'projects_count': 0  # TODO: 从 projects 表统计
        }

    def __repr__(self):
        return f'<Tenant {self.name}>'


class TenantUser(db.Model):
    """租户用户关联表"""
    __tablename__ = 'tenant_users'

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    user_id = db.Column(db.Integer, nullable=False, comment='用户ID')
    role = db.Column(db.String(20), default='member', comment='角色: owner-所有者, admin-管理员, member-成员')
    is_default = db.Column(db.Boolean, default=False, comment='是否默认租户')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)

    # 关联
    tenant = db.relationship('Tenant', backref='tenant_users')

    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'user_id': self.user_id,
            'role': self.role,
            'is_default': self.is_default,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

    def __repr__(self):
        return f'<TenantUser tenant_id={self.tenant_id} user_id={self.user_id}>'

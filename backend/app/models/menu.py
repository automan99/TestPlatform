"""
菜单和权限模型
实现基于角色的动态菜单系统
"""
from datetime import datetime
from app import db


class Menu(db.Model):
    """菜单表"""
    __tablename__ = 'menus'

    id = db.Column(db.Integer, primary_key=True, comment='主键ID')
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=True, index=True, comment='租户ID，null表示系统菜单')

    # 基本信息
    name = db.Column(db.String(100), nullable=False, comment='菜单名称')
    code = db.Column(db.String(100), unique=True, nullable=False, index=True, comment='菜单代码')
    title = db.Column(db.String(100), comment='菜单标题')
    parent_id = db.Column(db.Integer, db.ForeignKey('menus.id'), nullable=True, comment='父菜单ID')

    # 路由信息
    path = db.Column(db.String(200), comment='路由路径')
    component = db.Column(db.String(200), comment='组件路径')
    redirect = db.Column(db.String(200), comment='重定向路径')

    # 菜单属性
    icon = db.Column(db.String(100), comment='图标')
    type = db.Column(db.String(20), default='menu', comment='类型: menu-菜单, button-按钮, link-外链')
    sort_order = db.Column(db.Integer, default=0, comment='排序号')
    is_visible = db.Column(db.Boolean, default=True, comment='是否可见')
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    is_cached = db.Column(db.Boolean, default=False, comment='是否缓存')

    # 权限标识
    permission = db.Column(db.String(100), comment='权限标识')

    # 扩展配置
    meta_config = db.Column(db.Text, comment='元数据配置(JSON)')

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    created_by = db.Column(db.String(100), comment='创建人')
    updated_by = db.Column(db.String(100), comment='更新人')

    # 软删除
    is_deleted = db.Column(db.Boolean, default=False, comment='是否删除')

    # 关系
    children = db.relationship('Menu', backref=db.backref('parent', remote_side=[id]),
                               lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self, include_children=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'name': self.name,
            'code': self.code,
            'title': self.title,
            'parent_id': self.parent_id,
            'path': self.path,
            'component': self.component,
            'redirect': self.redirect,
            'icon': self.icon,
            'type': self.type,
            'sort_order': self.sort_order,
            'is_visible': self.is_visible,
            'is_enabled': self.is_enabled,
            'is_cached': self.is_cached,
            'permission': self.permission,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        if include_children and self.children:
            data['children'] = [child.to_dict() for child in self.children.filter_by(is_deleted=False).order_by('sort_order')]

        return data

    def __repr__(self):
        return f'<Menu {self.name}>'


class Role(db.Model):
    """角色表"""
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True, comment='主键ID')
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=True, index=True, comment='租户ID，null表示系统角色')

    # 基本信息
    name = db.Column(db.String(100), nullable=False, comment='角色名称')
    code = db.Column(db.String(100), nullable=False, comment='角色代码')
    description = db.Column(db.Text, comment='角色描述')

    # 角色类型
    role_type = db.Column(db.String(20), default='custom', comment='角色类型: system-系统角色, custom-自定义角色')

    # 权限级别
    level = db.Column(db.Integer, default=0, comment='权限级别，数字越大权限越高')

    # 状态
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    is_system = db.Column(db.Boolean, default=False, comment='是否系统角色（不可删除）')

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    created_by = db.Column(db.String(100), comment='创建人')
    updated_by = db.Column(db.String(100), comment='更新人')

    # 软删除
    is_deleted = db.Column(db.Boolean, default=False, comment='是否删除')

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'role_type': self.role_type,
            'level': self.level,
            'is_enabled': self.is_enabled,
            'is_system': self.is_system,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Role {self.name}>'


class RoleMenu(db.Model):
    """角色菜单关联表"""
    __tablename__ = 'role_menus'

    id = db.Column(db.Integer, primary_key=True, comment='主键ID')
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False, index=True, comment='角色ID')
    menu_id = db.Column(db.Integer, db.ForeignKey('menus.id'), nullable=False, index=True, comment='菜单ID')

    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')

    # 关系
    role = db.relationship('Role', backref=db.backref('role_menus', cascade='all, delete-orphan'))
    menu = db.relationship('Menu', backref=db.backref('menu_roles', cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<RoleMenu role_id={self.role_id} menu_id={self.menu_id}>'


class UserRole(db.Model):
    """用户角色关联表（扩展用户角色系统）"""
    __tablename__ = 'user_roles'

    id = db.Column(db.Integer, primary_key=True, comment='主键ID')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True, comment='用户ID')
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False, index=True, comment='角色ID')
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=True, index=True, comment='租户ID')

    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')

    # 关系
    user = db.relationship('User', backref=db.backref('user_roles', cascade='all, delete-orphan'))
    role = db.relationship('Role', backref=db.backref('role_users', cascade='all, delete-orphan'))
    tenant = db.relationship('Tenant', backref='user_roles')

    def __repr__(self):
        return f'<UserRole user_id={self.user_id} role_id={self.role_id}>'

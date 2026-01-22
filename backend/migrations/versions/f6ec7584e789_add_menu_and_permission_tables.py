"""add_menu_and_permission_tables

Revision ID: f6ec7584e789
Revises: c0014027b581
Create Date: 2026-01-22 11:54:26.291379

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f6ec7584e789'
down_revision = 'c0014027b581'
branch_labels = None
depends_on = None


def upgrade():
    """创建菜单和权限相关表"""
    # 创建菜单表
    op.create_table(
        'menus',
        sa.Column('id', sa.Integer(), nullable=False, comment='主键ID'),
        sa.Column('tenant_id', sa.Integer(), nullable=True, comment='租户ID，null表示系统菜单'),
        sa.Column('name', sa.String(length=100), nullable=False, comment='菜单名称'),
        sa.Column('code', sa.String(length=100), nullable=False, comment='菜单代码'),
        sa.Column('title', sa.String(length=100), comment='菜单标题'),
        sa.Column('parent_id', sa.Integer(), nullable=True, comment='父菜单ID'),
        sa.Column('path', sa.String(length=200), comment='路由路径'),
        sa.Column('component', sa.String(length=200), comment='组件路径'),
        sa.Column('redirect', sa.String(length=200), comment='重定向路径'),
        sa.Column('icon', sa.String(length=100), comment='图标'),
        sa.Column('type', sa.String(length=20), server_default='menu', comment='类型: menu-菜单, button-按钮, link-外链'),
        sa.Column('sort_order', sa.Integer(), server_default='0', comment='排序号'),
        sa.Column('is_visible', sa.Boolean(), server_default='1', comment='是否可见'),
        sa.Column('is_enabled', sa.Boolean(), server_default='1', comment='是否启用'),
        sa.Column('is_cached', sa.Boolean(), server_default='0', comment='是否缓存'),
        sa.Column('permission', sa.String(length=100), comment='权限标识'),
        sa.Column('meta_config', sa.Text(), comment='元数据配置(JSON)'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间'),
        sa.Column('created_by', sa.String(length=100), comment='创建人'),
        sa.Column('updated_by', sa.String(length=100), comment='更新人'),
        sa.Column('is_deleted', sa.Boolean(), server_default='0', comment='是否删除'),
        sa.ForeignKeyConstraint(['parent_id'], ['menus.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id'),
        comment='菜单表'
    )
    op.create_index('ix_menus_code', 'menus', ['code'])
    op.create_index('ix_menus_parent_id', 'menus', ['parent_id'])
    op.create_index('ix_menus_tenant_id', 'menus', ['tenant_id'])

    # 创建角色表
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), nullable=False, comment='主键ID'),
        sa.Column('tenant_id', sa.Integer(), nullable=True, comment='租户ID，null表示系统角色'),
        sa.Column('name', sa.String(length=100), nullable=False, comment='角色名称'),
        sa.Column('code', sa.String(length=100), nullable=False, comment='角色代码'),
        sa.Column('description', sa.Text(), comment='角色描述'),
        sa.Column('role_type', sa.String(length=20), server_default='custom', comment='角色类型: system-系统角色, custom-自定义角色'),
        sa.Column('level', sa.Integer(), server_default='0', comment='权限级别，数字越大权限越高'),
        sa.Column('is_enabled', sa.Boolean(), server_default='1', comment='是否启用'),
        sa.Column('is_system', sa.Boolean(), server_default='0', comment='是否系统角色（不可删除）'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间'),
        sa.Column('created_by', sa.String(length=100), comment='创建人'),
        sa.Column('updated_by', sa.String(length=100), comment='更新人'),
        sa.Column('is_deleted', sa.Boolean(), server_default='0', comment='是否删除'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id'),
        comment='角色表'
    )
    op.create_index('ix_roles_code', 'roles', ['code'])
    op.create_index('ix_roles_tenant_id', 'roles', ['tenant_id'])

    # 创建角色菜单关联表
    op.create_table(
        'role_menus',
        sa.Column('id', sa.Integer(), nullable=False, comment='主键ID'),
        sa.Column('role_id', sa.Integer(), nullable=False, comment='角色ID'),
        sa.Column('menu_id', sa.Integer(), nullable=False, comment='菜单ID'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
        sa.ForeignKeyConstraint(['menu_id'], ['menus.id'], ),
        sa.PrimaryKeyConstraint('id'),
        comment='角色菜单关联表'
    )
    op.create_index('ix_role_menus_menu_id', 'role_menus', ['menu_id'])
    op.create_index('ix_role_menus_role_id', 'role_menus', ['role_id'])

    # 创建用户角色关联表
    op.create_table(
        'user_roles',
        sa.Column('id', sa.Integer(), nullable=False, comment='主键ID'),
        sa.Column('user_id', sa.Integer(), nullable=False, comment='用户ID'),
        sa.Column('role_id', sa.Integer(), nullable=False, comment='角色ID'),
        sa.Column('tenant_id', sa.Integer(), nullable=True, comment='租户ID'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        comment='用户角色关联表'
    )
    op.create_index('ix_user_roles_role_id', 'user_roles', ['role_id'])
    op.create_index('ix_user_roles_tenant_id', 'user_roles', ['tenant_id'])
    op.create_index('ix_user_roles_user_id', 'user_roles', ['user_id'])

    # 插入默认菜单数据
    op.execute("""
        INSERT INTO menus (name, code, title, path, icon, type, sort_order, is_visible, permission, created_by) VALUES
        ('首页', 'dashboard', '首页', '/dashboard', 'House', 'menu', 1, 1, 'dashboard:view', 'system'),
        ('测试用例', 'test-cases', '测试用例', '/test-cases', 'Document', 'menu', 2, 1, 'testcase:view', 'system'),
        ('测试计划', 'test-plans', '测试计划', '/test-plans', 'Calendar', 'menu', 3, 1, 'testplan:view', 'system'),
        ('测试环境', 'environments', '测试环境', '/environments', 'Monitor', 'menu', 4, 1, 'environment:view', 'system'),
        ('缺陷管理', 'defects', '缺陷管理', '/defects', 'CircleClose', 'menu', 5, 1, 'defect:view', 'system'),
        ('测试报告', 'reports', '测试报告', '/reports', 'DataAnalysis', 'menu', 6, 1, 'report:view', 'system'),
        ('项目管理', 'projects', '项目管理', '/projects', 'FolderOpened', 'menu', 7, 1, 'project:view', 'system'),
        ('MCP Server', 'mcp-server', 'MCP Server', '/mcp-server', 'Connection', 'menu', 8, 1, 'mcp:view', 'system'),
        ('Skills', 'skills', 'Skills', '/skills', 'Files', 'menu', 9, 1, 'skill:view', 'system'),
        ('系统设置', 'settings', '系统设置', '/settings', 'Setting', 'menu', 10, 1, 'settings:view', 'system'),
        ('租户管理', 'tenants', '租户管理', '/tenants', 'OfficeBuilding', 'menu', 11, 0, 'tenant:view', 'system'),
        ('菜单管理', 'menu-management', '菜单管理', '/menu-management', 'Menu', 'menu', 12, 0, 'menu:view', 'system')
    """)

    # 插入默认角色
    op.execute("""
        INSERT INTO roles (name, code, description, role_type, level, is_system, created_by) VALUES
        ('超级管理员', 'super_admin', '系统超级管理员，拥有所有权限', 'system', 100, 1, 'system'),
        ('管理员', 'admin', '租户管理员', 'custom', 50, 1, 'system'),
        ('普通用户', 'user', '普通用户', 'custom', 10, 1, 'system')
    """)


def downgrade():
    """回滚：删除菜单和权限相关表"""
    op.drop_table('user_roles')
    op.drop_table('role_menus')
    op.drop_table('roles')
    op.drop_table('menus')

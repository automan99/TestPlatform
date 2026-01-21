"""Create tenant tables

Revision ID: 001_create_tenant_tables
Revises: a278268de740
Create Date: 2026-01-20 11:42:00.000000

"""
from alembic import op
import sqlalchemy as sa
from alembic import context


# revision identifiers, used by Alembic.
revision = '001_create_tenant_tables'
down_revision = 'a278268de740'
branch_labels = None
depends_on = None


def upgrade():
    # 创建租户表
    op.create_table('tenants',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('name', sa.String(length=100), nullable=False, comment='租户名称'),
        sa.Column('code', sa.String(length=50), nullable=False, comment='租户代码'),
        sa.Column('description', sa.Text(), nullable=True, comment='描述'),
        sa.Column('logo', sa.String(length=255), nullable=True, comment='Logo URL'),
        sa.Column('status', sa.String(length=20), nullable=True, server_default='active', comment='状态: active-激活, suspended-暂停, expired-过期'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='1', comment='是否激活'),
        sa.Column('max_users', sa.Integer(), nullable=True, server_default='10', comment='最大用户数'),
        sa.Column('max_projects', sa.Integer(), nullable=True, server_default='5', comment='最大项目数'),
        sa.Column('max_storage_gb', sa.Integer(), nullable=True, server_default='10', comment='最大存储空间(GB)'),
        sa.Column('expire_date', sa.Date(), nullable=True, comment='过期日期'),
        sa.Column('settings', sa.JSON(), nullable=True, comment='租户设置'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间'),
        sa.Column('created_by', sa.Integer(), nullable=True, comment='创建人ID'),
        sa.Column('updated_by', sa.Integer(), nullable=True, comment='更新人ID'),
        sa.Column('is_deleted', sa.Boolean(), nullable=True, server_default='0', comment='是否删除'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', name='uk_name'),
        sa.UniqueConstraint('code', name='uk_code'),
        comment='租户表'
    )
    
    # 创建索引
    op.create_index('idx_status', 'tenants', ['status'], unique=False)
    op.create_index('idx_is_active', 'tenants', ['is_active'], unique=False)
    op.create_index('idx_is_deleted', 'tenants', ['is_deleted'], unique=False)

    # 创建租户用户关联表
    op.create_table('tenant_users',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('tenant_id', sa.Integer(), nullable=False, comment='租户ID'),
        sa.Column('user_id', sa.Integer(), nullable=False, comment='用户ID'),
        sa.Column('role', sa.String(length=20), nullable=True, server_default='member', comment='角色: owner-所有者, admin-管理员, member-成员'),
        sa.Column('is_default', sa.Boolean(), nullable=True, server_default='0', comment='是否默认租户'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('is_deleted', sa.Boolean(), nullable=True, server_default='0', comment='是否删除'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'user_id', name='uk_tenant_user'),
        comment='租户用户关联表'
    )
    
    # 创建索引
    op.create_index('idx_tenant_id', 'tenant_users', ['tenant_id'], unique=False)
    op.create_index('idx_user_id', 'tenant_users', ['user_id'], unique=False)
    op.create_index('idx_role', 'tenant_users', ['role'], unique=False)

    # 插入测试租户数据（仅在初始迁移时执行）
    if context.is_offline_mode() or not context.get_context().as_sql:
        # 使用原始SQL插入测试数据
        op.execute("""
            INSERT INTO tenants (name, code, description, status, is_active, max_users, max_projects, max_storage_gb, expire_date, settings)
            VALUES ('测试租户', 'test', '用于测试的默认租户', 'active', 1, 100, 50, 100, DATE_ADD(CURDATE(), INTERVAL 10 YEAR), '{"allow_register": true, "default_locale": "zh-CN"}')
            ON DUPLICATE KEY UPDATE name = name
        """)


def downgrade():
    # 删除索引
    op.drop_index('idx_role', table_name='tenant_users')
    op.drop_index('idx_user_id', table_name='tenant_users')
    op.drop_index('idx_tenant_id', table_name='tenant_users')
    
    # 删除租户用户关联表
    op.drop_table('tenant_users')
    
    # 删除索引
    op.drop_index('idx_is_deleted', table_name='tenants')
    op.drop_index('idx_is_active', table_name='tenants')
    op.drop_index('idx_status', table_name='tenants')
    
    # 删除租户表
    op.drop_table('tenants')
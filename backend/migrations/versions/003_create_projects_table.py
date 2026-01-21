"""Create projects table

Revision ID: 003_create_projects
Revises: 002_add_tenant_id
Create Date: 2026-01-20 11:42:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003_create_projects'
down_revision = '002_add_tenant_id'
branch_labels = None
depends_on = None


def upgrade():
    """创建 projects 表"""
    
    op.create_table('projects',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True, comment='项目ID'),
        sa.Column('tenant_id', sa.Integer(), nullable=True, comment='租户ID'),
        sa.Column('name', sa.String(length=200), nullable=False, comment='项目名称'),
        sa.Column('code', sa.String(length=50), nullable=False, comment='项目代码'),
        sa.Column('description', sa.Text(), nullable=True, comment='项目描述'),
        sa.Column('project_type', sa.String(length=50), nullable=True, server_default='web', comment='项目类型: web, mobile, api, desktop'),
        sa.Column('status', sa.String(length=20), nullable=True, server_default='active', comment='状态: active, archived, completed'),
        sa.Column('key', sa.String(length=10), nullable=True, comment='项目标识符（用于缺陷编号前缀）'),
        sa.Column('url', sa.String(length=500), nullable=True, comment='项目URL'),
        sa.Column('repository', sa.String(length=500), nullable=True, comment='代码仓库地址'),
        sa.Column('max_test_suites', sa.Integer(), nullable=True, server_default='100', comment='最大测试套件数'),
        sa.Column('max_test_cases', sa.Integer(), nullable=True, server_default='1000', comment='最大测试用例数'),
        sa.Column('max_test_plans', sa.Integer(), nullable=True, server_default='50', comment='最大测试计划数'),
        sa.Column('test_suite_count', sa.Integer(), nullable=True, server_default='0', comment='测试套件数'),
        sa.Column('test_case_count', sa.Integer(), nullable=True, server_default='0', comment='测试用例数'),
        sa.Column('test_plan_count', sa.Integer(), nullable=True, server_default='0', comment='测试计划数'),
        sa.Column('defect_count', sa.Integer(), nullable=True, server_default='0', comment='缺陷数'),
        sa.Column('sort_order', sa.Integer(), nullable=True, server_default='0', comment='排序'),
        sa.Column('icon', sa.String(length=100), nullable=True, comment='图标'),
        sa.Column('color', sa.String(length=20), nullable=True, server_default='#409EFF', comment='颜色'),
        sa.Column('owner', sa.String(length=100), nullable=True, comment='项目负责人'),
        sa.Column('lead', sa.String(length=100), nullable=True, comment='项目主管'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间'),
        sa.Column('created_by', sa.String(length=100), nullable=True, comment='创建人'),
        sa.Column('updated_by', sa.String(length=100), nullable=True, comment='更新人'),
        sa.Column('is_deleted', sa.Boolean(), nullable=True, server_default='0', comment='是否删除'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key'),
        sa.UniqueConstraint('code'),
        comment='项目表'
    )
    
    # 创建索引
    op.create_index('idx_tenant_id', 'projects', ['tenant_id'], unique=False)
    op.create_index('idx_code', 'projects', ['code'], unique=False)
    op.create_index('idx_key', 'projects', ['key'], unique=False)
    op.create_index('idx_status', 'projects', ['status'], unique=False)
    
    # 添加外键约束
    op.create_foreign_key('fk_projects_tenant', 'projects', 'tenants', ['tenant_id'], ['id'], ondelete='SET NULL')


def downgrade():
    """删除 projects 表"""
    
    # 删除外键约束
    op.drop_constraint('fk_projects_tenant', 'projects', type_='foreignkey')
    
    # 删除索引
    op.drop_index('idx_status', table_name='projects')
    op.drop_index('idx_key', table_name='projects')
    op.drop_index('idx_code', table_name='projects')
    op.drop_index('idx_tenant_id', table_name='projects')
    
    # 删除表
    op.drop_table('projects')
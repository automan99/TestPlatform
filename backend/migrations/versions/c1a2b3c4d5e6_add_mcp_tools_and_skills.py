"""Add MCP Tools and Skills tables

Revision ID: c1a2b3c4d5e6
Revises: 5b0g4f3c1d0h
Create Date: 2026-01-20 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c1a2b3c4d5e6'
down_revision = '5b0g4f3c1d0h'
branch_labels = None
depends_on = None


def upgrade():
    """创建 MCP Tools 和 Skills 表"""

    # 创建 mcp_tools 表
    op.create_table('mcp_tools',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('mcp_type', sa.String(length=50), nullable=True),
        sa.Column('endpoint_url', sa.String(length=500), nullable=True),
        sa.Column('auth_type', sa.String(length=50), nullable=True),
        sa.Column('auth_config', sa.Text(), nullable=True),
        sa.Column('timeout', sa.Integer(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=True),
        sa.Column('headers', sa.Text(), nullable=True),
        sa.Column('params_template', sa.Text(), nullable=True),
        sa.Column('response_mapping', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('is_enabled', sa.Boolean(), nullable=True),
        sa.Column('version', sa.String(length=20), nullable=True),
        sa.Column('tags', sa.String(length=500), nullable=True),
        sa.Column('usage_count', sa.Integer(), nullable=True),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('updated_by', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    with op.batch_alter_table('mcp_tools', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_mcp_tools_tenant_id'), ['tenant_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_mcp_tools_code'), ['code'], unique=False)

    # 创建 skills 表
    op.create_table('skills',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('mcp_id', sa.Integer(), nullable=True),
        sa.Column('script_content', sa.Text(), nullable=True),
        sa.Column('script_type', sa.String(length=50), nullable=True),
        sa.Column('params_schema', sa.Text(), nullable=True),
        sa.Column('params_example', sa.Text(), nullable=True),
        sa.Column('timeout', sa.Integer(), nullable=True),
        sa.Column('log_enabled', sa.Boolean(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=True),
        sa.Column('allowed_roles', sa.Text(), nullable=True),
        sa.Column('version', sa.String(length=20), nullable=True),
        sa.Column('previous_versions', sa.Text(), nullable=True),
        sa.Column('usage_count', sa.Integer(), nullable=True),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('last_execution_result', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('is_enabled', sa.Boolean(), nullable=True),
        sa.Column('tags', sa.String(length=500), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('updated_by', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    with op.batch_alter_table('skills', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_skills_tenant_id'), ['tenant_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_skills_code'), ['code'], unique=False)
        batch_op.create_index(batch_op.f('ix_skills_mcp_id'), ['mcp_id'], unique=False)

    # 添加外键约束
    op.create_foreign_key('mcp_tools_tenant_id_fkey', 'mcp_tools', 'tenants', ['tenant_id'], ['id'])
    op.create_foreign_key('skills_mcp_id_fkey', 'skills', 'mcp_tools', ['mcp_id'], ['id'])
    op.create_foreign_key('skills_tenant_id_fkey', 'skills', 'tenants', ['tenant_id'], ['id'])


def downgrade():
    """回滚迁移"""
    # 删除外键约束
    op.drop_constraint('skills_tenant_id_fkey', 'skills', type_='foreignkey')
    op.drop_constraint('skills_mcp_id_fkey', 'skills', type_='foreignkey')
    op.drop_constraint('mcp_tools_tenant_id_fkey', 'mcp_tools', type_='foreignkey')

    # 删除 skills 表
    with op.batch_alter_table('skills', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_skills_mcp_id'))
        batch_op.drop_index(batch_op.f('ix_skills_code'))
        batch_op.drop_index(batch_op.f('ix_skills_tenant_id'))
    op.drop_table('skills')

    # 删除 mcp_tools 表
    with op.batch_alter_table('mcp_tools', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_mcp_tools_code'))
        batch_op.drop_index(batch_op.f('ix_mcp_tools_tenant_id'))
    op.drop_table('mcp_tools')

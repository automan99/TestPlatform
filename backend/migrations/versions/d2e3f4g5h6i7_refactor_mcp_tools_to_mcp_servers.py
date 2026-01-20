"""Refactor MCP Tools to MCP Servers

Revision ID: d2e3f4g5h6i7
Revises: c1a2b3c4d5e6
Create Date: 2026-01-20 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = 'd2e3f4g5h6i7'
down_revision = 'c1a2b3c4d5e6'
branch_labels = None
depends_on = None


def _drop_foreign_key_if_exists(table_name, fk_name):
    """删除外键约束（如果存在）"""
    try:
        # 检查外键是否存在
        conn = op.get_bind()
        result = conn.execute(text(f"""
            SELECT CONSTRAINT_NAME
            FROM information_schema.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = '{table_name}'
            AND CONSTRAINT_NAME = '{fk_name}'
            AND CONSTRAINT_TYPE = 'FOREIGN KEY'
        """))
        if result.fetchone():
            op.drop_constraint(fk_name, table_name, type_='foreignkey')
    except Exception:
        # 如果外键不存在，忽略错误
        pass


def upgrade():
    """将 mcp_tools 重构为 mcp_servers"""

    # 1. 删除 skills 表的外键约束（如果存在）
    _drop_foreign_key_if_exists('skills', 'skills_mcp_id_fkey')

    # 2. 删除 mcp_tools 的外键约束（如果存在）
    _drop_foreign_key_if_exists('mcp_tools', 'mcp_tools_tenant_id_fkey')

    # 3. 重命名表
    op.rename_table('mcp_tools', 'mcp_servers')

    # 4. 修改列结构
    with op.batch_alter_table('mcp_servers', schema=None) as batch_op:
        # 重命名 mcp_type 为 transport_type
        batch_op.alter_column('mcp_type', new_column_name='transport_type',
                             existing_type=sa.String(length=50))

        # 添加新列
        batch_op.add_column(sa.Column('command', sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column('arguments', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('env', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('url', sa.String(length=500), nullable=True))

        # 删除旧列
        batch_op.drop_column('endpoint_url')
        batch_op.drop_column('auth_type')
        batch_op.drop_column('auth_config')
        batch_op.drop_column('retry_count')
        batch_op.drop_column('headers')
        batch_op.drop_column('params_template')
        batch_op.drop_column('response_mapping')
        batch_op.drop_column('version')

    # 5. 创建外键约束
    op.create_foreign_key('mcp_servers_tenant_id_fkey', 'mcp_servers', 'tenants', ['tenant_id'], ['id'])
    # skills_tenant_id_fkey 已存在，跳过
    op.create_foreign_key('skills_mcp_id_fkey', 'skills', 'mcp_servers', ['mcp_id'], ['id'])


def downgrade():
    """回滚迁移"""

    # 删除外键约束
    _drop_foreign_key_if_exists('skills', 'skills_mcp_id_fkey')
    _drop_foreign_key_if_exists('skills', 'skills_tenant_id_fkey')
    _drop_foreign_key_if_exists('mcp_servers', 'mcp_servers_tenant_id_fkey')

    # 恢复列结构
    with op.batch_alter_table('mcp_servers', schema=None) as batch_op:
        # 恢复旧列
        batch_op.add_column(sa.Column('version', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('response_mapping', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('params_template', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('headers', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('retry_count', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('auth_config', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('auth_type', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('endpoint_url', sa.String(length=500), nullable=True))

        # 删除新列
        batch_op.drop_column('url')
        batch_op.drop_column('env')
        batch_op.drop_column('arguments')
        batch_op.drop_column('command')

        # 重命名 transport_type 回 mcp_type
        batch_op.alter_column('transport_type', new_column_name='mcp_type',
                             existing_type=sa.String(length=50))

    # 重命名表回 mcp_tools
    op.rename_table('mcp_servers', 'mcp_tools')

    # 重新创建外键约束
    op.create_foreign_key('mcp_tools_tenant_id_fkey', 'mcp_tools', 'tenants', ['tenant_id'], ['id'])
    # skills_tenant_id_fkey 已存在，保持不变
    _drop_foreign_key_if_exists('skills', 'skills_mcp_id_fkey')
    op.create_foreign_key('skills_mcp_id_fkey', 'skills', 'mcp_tools', ['mcp_id'], ['id'])

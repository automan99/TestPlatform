"""Add tools_count column to mcp_servers

Revision ID: 006_add_tools_count
Revises: 005_add_mcp_tools_resources
Create Date: 2026-01-20 11:42:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '006_add_tools_count'
down_revision = '005_add_mcp_tools_resources'
branch_labels = None
depends_on = None


def upgrade():
    """添加 tools_count 列到 mcp_servers 表"""
    try:
        op.add_column('mcp_servers', 
            sa.Column('tools_count', sa.Integer(), nullable=True, server_default='0', comment='MCP提供的工具数量')
        )
    except Exception as e:
        # 如果列已存在，忽略错误
        if 'duplicate column' not in str(e).lower():
            raise


def downgrade():
    """删除 tools_count 列"""
    op.drop_column('mcp_servers', 'tools_count')
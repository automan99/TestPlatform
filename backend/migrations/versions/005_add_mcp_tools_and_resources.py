"""Add MCP tools and resources tables

Revision ID: 005_add_mcp_tools_resources
Revises: e3f4g5h6i7j8
Create Date: 2026-01-20 11:42:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = '005_add_mcp_tools_resources'
down_revision = 'e3f4g5h6i7j8'
branch_labels = None
depends_on = None


def upgrade():
    """添加 MCP 工具和资源表"""
    
    # 1. 添加 resources_count 列到 mcp_servers 表
    try:
        op.add_column('mcp_servers', 
            sa.Column('resources_count', sa.Integer(), nullable=True, server_default='0', comment='MCP提供的资源数量')
        )
    except Exception as e:
        # 如果列已存在，忽略错误
        if 'duplicate column' not in str(e).lower():
            raise
    
    # 2. 添加 last_sync_at 列到 mcp_servers 表
    try:
        op.add_column('mcp_servers', 
            sa.Column('last_sync_at', sa.DateTime(), nullable=True, comment='最后同步时间')
        )
    except Exception as e:
        # 如果列已存在，忽略错误
        if 'duplicate column' not in str(e).lower():
            raise

    # 3. 创建 mcp_tools 表
    op.create_table('mcp_tools',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('mcp_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('input_schema', sa.Text(), nullable=True),
        sa.Column('usage_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        comment='MCP工具表'
    )
    
    # 创建索引
    op.create_index('idx_mcp_id', 'mcp_tools', ['mcp_id'], unique=False)
    
    # 添加外键约束
    op.create_foreign_key('fk_mcp_tools_mcp_id', 'mcp_tools', 'mcp_servers', ['mcp_id'], ['id'], ondelete='CASCADE')

    # 4. 创建 mcp_resources 表
    op.create_table('mcp_resources',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('mcp_id', sa.Integer(), nullable=False),
        sa.Column('uri', sa.String(length=500), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('mime_type', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        comment='MCP资源表'
    )
    
    # 创建索引
    op.create_index('idx_mcp_id', 'mcp_resources', ['mcp_id'], unique=False)
    
    # 添加外键约束
    op.create_foreign_key('fk_mcp_resources_mcp_id', 'mcp_resources', 'mcp_servers', ['mcp_id'], ['id'], ondelete='CASCADE')

    # 5. 创建 mcp_tool_executions 表
    op.create_table('mcp_tool_executions',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('tool_id', sa.Integer(), nullable=False),
        sa.Column('parameters', sa.Text(), nullable=True),
        sa.Column('result', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True, server_default='success'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('execution_time', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        comment='MCP工具执行记录表'
    )
    
    # 创建索引
    op.create_index('idx_tool_id', 'mcp_tool_executions', ['tool_id'], unique=False)
    
    # 添加外键约束
    op.create_foreign_key('fk_mcp_tool_executions_tool_id', 'mcp_tool_executions', 'mcp_tools', ['tool_id'], ['id'], ondelete='CASCADE')


def downgrade():
    """回滚迁移"""
    
    # 删除 mcp_tool_executions 表
    op.drop_constraint('fk_mcp_tool_executions_tool_id', 'mcp_tool_executions', type_='foreignkey')
    op.drop_index('idx_tool_id', table_name='mcp_tool_executions')
    op.drop_table('mcp_tool_executions')
    
    # 删除 mcp_resources 表
    op.drop_constraint('fk_mcp_resources_mcp_id', 'mcp_resources', type_='foreignkey')
    op.drop_index('idx_mcp_id', table_name='mcp_resources')
    op.drop_table('mcp_resources')
    
    # 删除 mcp_tools 表
    op.drop_constraint('fk_mcp_tools_mcp_id', 'mcp_tools', type_='foreignkey')
    op.drop_index('idx_mcp_id', table_name='mcp_tools')
    op.drop_table('mcp_tools')
    
    # 删除列
    op.drop_column('mcp_servers', 'last_sync_at')
    op.drop_column('mcp_servers', 'resources_count')
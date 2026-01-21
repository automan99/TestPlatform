"""Create LLM models table

Revision ID: 009_create_llm_models
Revises: 008_migrate_data
Create Date: 2026-01-20 22:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = '009_create_llm_models'
down_revision = '008_migrate_data'
branch_labels = None
depends_on = None


def upgrade():
    """创建LLM模型配置表"""

    op.create_table('llm_models',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('name', sa.String(length=100), nullable=False, comment='模型名称'),
        sa.Column('provider', sa.String(length=50), nullable=False, comment='提供商: openai, anthropic, azure, etc.'),
        sa.Column('model_id', sa.String(length=100), nullable=False, comment='模型ID: gpt-4, claude-3-opus-20240229, etc.'),
        sa.Column('api_key', sa.Text(), nullable=True, comment='API密钥(加密存储)'),
        sa.Column('api_base', sa.String(length=500), nullable=True, comment='API基础URL'),
        sa.Column('api_version', sa.String(length=50), nullable=True, comment='API版本(用于Azure等)'),
        sa.Column('temperature', sa.Float(), nullable=True, server_default='0.7', comment='温度参数'),
        sa.Column('max_tokens', sa.Integer(), nullable=True, server_default='4096', comment='最大token数'),
        sa.Column('top_p', sa.Float(), nullable=True, server_default='1.0', comment='top_p参数'),
        sa.Column('frequency_penalty', sa.Float(), nullable=True, server_default='0.0', comment='频率惩罚'),
        sa.Column('presence_penalty', sa.Float(), nullable=True, server_default='0.0', comment='存在惩罚'),
        sa.Column('is_default', sa.Boolean(), nullable=True, server_default='0', comment='是否为默认模型'),
        sa.Column('is_enabled', sa.Boolean(), nullable=True, server_default='1', comment='是否启用'),
        sa.Column('description', sa.Text(), nullable=True, comment='描述'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间'),
        sa.Column('created_by', sa.Integer(), nullable=True, comment='创建人'),
        sa.PrimaryKeyConstraint('id'),
        comment='LLM模型配置表'
    )

    # 创建索引
    op.create_index('idx_llm_provider', 'llm_models', ['provider'], unique=False)
    op.create_index('idx_llm_is_default', 'llm_models', ['is_default'], unique=False)
    op.create_index('idx_llm_is_enabled', 'llm_models', ['is_enabled'], unique=False)

    # 添加外键约束
    op.create_foreign_key('fk_llm_models_created_by', 'llm_models', 'users', ['created_by'], ['id'], ondelete='SET NULL')


def downgrade():
    """删除LLM模型配置表"""

    # 删除外键约束
    op.drop_constraint('fk_llm_models_created_by', 'llm_models', type_='foreignkey')

    # 删除索引
    op.drop_index('idx_llm_is_enabled', 'llm_models')
    op.drop_index('idx_llm_is_default', 'llm_models')
    op.drop_index('idx_llm_provider', 'llm_models')

    # 删除表
    op.drop_table('llm_models')

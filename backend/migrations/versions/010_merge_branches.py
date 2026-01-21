"""Merge branches

This is a merge migration to combine two independent branches.

Revision ID: 010_merge_branches
Revises: 004_add_user_columns, 009_create_llm_models
Create Date: 2026-01-21 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '010_merge_branches'
down_revision = ('004_add_user_columns', '009_create_llm_models')
branch_labels = None
depends_on = None


def upgrade():
    """合并两个分支"""
    # 这是一个合并迁移，不需要任何数据库操作
    # 它只是告诉 Alembic 这两个分支现在已经合并了
    pass


def downgrade():
    """回滚合并"""
    # 无法回滚合并迁移
    pass
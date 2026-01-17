"""Add module_id to defects

Revision ID: 5b0g4f3c1d0h
Revises: 4a9f3e2b8c0g
Create Date: 2026-01-17 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5b0g4f3c1d0h'
down_revision = '4a9f3e2b8c0g'
branch_labels = None
depends_on = None


def upgrade():
    """添加 module_id 字段到 defects 表"""
    op.add_column('defects', sa.Column('module_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_defects_module_id'), 'defects', ['module_id'], unique=False)
    op.create_foreign_key('defects_module_id_fkey', 'defects', 'defect_modules', ['module_id'], ['id'])


def downgrade():
    """回滚迁移"""
    op.drop_constraint('defects_module_id_fkey', 'defects', type_='foreignkey')
    op.drop_index(op.f('ix_defects_module_id'), table_name='defects')
    op.drop_column('defects', 'module_id')

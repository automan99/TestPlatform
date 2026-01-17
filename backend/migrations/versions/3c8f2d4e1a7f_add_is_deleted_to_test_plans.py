"""Add is_deleted field to test_plans

Revision ID: 3c8f2d4e1a7f
Revises: 201587a8592b
Create Date: 2026-01-17 15:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3c8f2d4e1a7f'
down_revision = '201587a8592b'
branch_labels = None
depends_on = None


def upgrade():
    """添加 is_deleted 字段到 test_plans 表"""
    with op.batch_alter_table('test_plans', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_deleted', sa.Boolean(), nullable=True, default=False))


def downgrade():
    """回滚迁移"""
    with op.batch_alter_table('test_plans', schema=None) as batch_op:
        batch_op.drop_column('is_deleted')

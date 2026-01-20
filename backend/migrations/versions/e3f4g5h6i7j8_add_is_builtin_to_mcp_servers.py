"""添加 is_builtin 字段到 mcp_servers 表

Revision ID: e3f4g5h6i7j8
Revises: d2e3f4g5h6i7
Create Date: 2026-01-20 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e3f4g5h6i7j8'
down_revision = 'd2e3f4g5h6i7'
branch_labels = None
depends_on = None


def upgrade():
    """添加 is_builtin 字段"""
    with op.batch_alter_table('mcp_servers', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_builtin', sa.Boolean(), nullable=False, server_default='0'))


def downgrade():
    """回滚迁移"""
    with op.batch_alter_table('mcp_servers', schema=None) as batch_op:
        batch_op.drop_column('is_builtin')

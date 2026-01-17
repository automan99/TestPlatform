"""Create defect_modules table

Revision ID: 4a9f3e2b8c0g
Revises: 3c8f2d4e1a7f
Create Date: 2026-01-17 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4a9f3e2b8c0g'
down_revision = '3c8f2d4e1a7f'
branch_labels = None
depends_on = None


def upgrade():
    """创建 defect_modules 表"""
    op.create_table(
        'defect_modules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['parent_id'], ['defect_modules.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_defect_modules_project_id'), 'defect_modules', ['project_id'], unique=False)


def downgrade():
    """回滚迁移"""
    op.drop_index(op.f('ix_defect_modules_project_id'), table_name='defect_modules')
    op.drop_table('defect_modules')

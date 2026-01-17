"""Add test plan folders and assigned_to field

Revision ID: 201587a8592b
Revises: a278268de740
Create Date: 2026-01-17 10:08:36.275770

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '201587a8592b'
down_revision = 'a278268de740'
branch_labels = None
depends_on = None


def upgrade():
    """添加测试计划目录和指派人字段"""

    # 1. 创建 test_plan_folders 表
    op.create_table('test_plan_folders',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['parent_id'], ['test_plan_folders.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # 2. 为 test_plan_folders 表创建索引
    with op.batch_alter_table('test_plan_folders', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_test_plan_folders_project_id'), ['project_id'], unique=False)

    # 3. 为 test_plans 表添加 folder_id 和 assigned_to 字段
    with op.batch_alter_table('test_plans', schema=None) as batch_op:
        batch_op.add_column(sa.Column('folder_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('assigned_to', sa.String(length=100), nullable=True))

        # 添加外键约束
        batch_op.create_foreign_key('fk_test_plans_folder_id', 'test_plan_folders', ['folder_id'], ['id'])

        # 删除不需要的字段
        batch_op.drop_column('agent_config')
        batch_op.drop_column('automation_enabled')


def downgrade():
    """回滚迁移"""

    # 1. 恢复 test_plans 表的字段
    with op.batch_alter_table('test_plans', schema=None) as batch_op:
        batch_op.drop_constraint('fk_test_plans_folder_id', type_='foreignkey')
        batch_op.drop_column('folder_id')
        batch_op.drop_column('assigned_to')
        batch_op.add_column(sa.Column('automation_enabled', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('agent_config', mysql.TEXT(), nullable=True))

    # 2. 删除 test_plan_folders 表的索引
    with op.batch_alter_table('test_plan_folders', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_test_plan_folders_project_id'))

    # 3. 删除 test_plan_folders 表
    op.drop_table('test_plan_folders')

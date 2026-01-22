"""add_user_role_column

Revision ID: c0014027b581
Revises: 010_merge_branches
Create Date: 2026-01-22 11:32:05.077705

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine import reflection


# revision identifiers, used by Alembic.
revision = 'c0014027b581'
down_revision = '010_merge_branches'
branch_labels = None
depends_on = None


def column_exists(table_name, column_name, connection):
    """检查列是否存在"""
    inspector = reflection.Inspector.from_engine(connection)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def upgrade():
    """添加用户角色字段"""
    # 获取数据库连接
    connection = op.get_bind()

    # 检查 role 列是否已存在
    if not column_exists('users', 'role', connection):
        # 添加 role 列
        with op.batch_alter_table('users', schema=None) as batch_op:
            batch_op.add_column(sa.Column('role', sa.String(length=20), nullable=True, comment='全局角色: super_admin-超级管理员, user-普通用户'))

        # 更新现有数据：将 is_admin=True 的用户设为 super_admin
        connection.execute(sa.text("""
            UPDATE users
            SET role = 'super_admin'
            WHERE is_admin = 1
        """))

        # 将其他用户设为 user
        connection.execute(sa.text("""
            UPDATE users
            SET role = 'user'
            WHERE role IS NULL
        """))

        # 将 role 列设为非空
        with op.batch_alter_table('users', schema=None) as batch_op:
            batch_op.alter_column('role', nullable=False, server_default='user')
    else:
        # 列已存在，更新数据
        # 确保所有用户都有 role 值
        connection.execute(sa.text("""
            UPDATE users
            SET role = 'super_admin'
            WHERE is_admin = 1 AND (role IS NULL OR role != 'super_admin')
        """))

        connection.execute(sa.text("""
            UPDATE users
            SET role = 'user'
            WHERE role IS NULL
        """))


def downgrade():
    """回滚：移除用户角色字段"""
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('role')

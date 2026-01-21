"""Add user columns

Revision ID: 004_add_user_columns
Revises: 003_create_projects
Create Date: 2026-01-20 11:42:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004_add_user_columns'
down_revision = '003_create_projects'
branch_labels = None
depends_on = None


def upgrade():
    """添加 users 表的新字段"""
    
    # 添加头像字段
    op.add_column('users', 
        sa.Column('avatar', sa.String(length=255), nullable=True, comment='头像URL')
    )
    
    # 添加OAuth相关字段
    op.add_column('users', 
        sa.Column('oauth_provider', sa.String(length=50), nullable=True, comment='OAuth提供商')
    )
    op.add_column('users', 
        sa.Column('oauth_user_id', sa.String(length=100), nullable=True, comment='OAuth用户ID')
    )
    
    # 修改password_hash字段为可空（OAuth用户不需要密码）
    # 注意：在MySQL中，ALTER COLUMN修改为可空需要指定新的NOT NULL状态
    op.alter_column('users', 'password_hash',
        existing_type=sa.String(length=255),
        nullable=True,
        comment='密码哈希（OAuth用户可为空）'
    )


def downgrade():
    """删除 users 表的新字段"""
    
    # 恢复password_hash字段为非空
    op.alter_column('users', 'password_hash',
        existing_type=sa.String(length=255),
        nullable=False
    )
    
    # 删除OAuth相关字段
    op.drop_column('users', 'oauth_user_id')
    op.drop_column('users', 'oauth_provider')
    
    # 删除头像字段
    op.drop_column('users', 'avatar')
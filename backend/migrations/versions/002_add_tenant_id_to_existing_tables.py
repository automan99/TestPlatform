"""Add tenant_id to existing tables

Revision ID: 002_add_tenant_id
Revises: 001_create_tenant_tables
Create Date: 2026-01-20 11:42:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_add_tenant_id'
down_revision = '001_create_tenant_tables'
branch_labels = None
depends_on = None


def upgrade():
    """为现有表添加 tenant_id 字段"""
    
    # 测试套件表添加 tenant_id
    op.add_column('test_suites', 
        sa.Column('tenant_id', sa.Integer(), nullable=True, comment='租户ID')
    )
    op.create_index('idx_tenant_id', 'test_suites', ['tenant_id'], unique=False)
    
    # 测试用例表添加 tenant_id
    op.add_column('test_cases', 
        sa.Column('tenant_id', sa.Integer(), nullable=True, comment='租户ID')
    )
    op.create_index('idx_tenant_id', 'test_cases', ['tenant_id'], unique=False)
    
    # 测试计划表添加 tenant_id
    op.add_column('test_plans', 
        sa.Column('tenant_id', sa.Integer(), nullable=True, comment='租户ID')
    )
    op.create_index('idx_tenant_id', 'test_plans', ['tenant_id'], unique=False)
    
    # 测试环境表添加 tenant_id
    op.add_column('test_environments', 
        sa.Column('tenant_id', sa.Integer(), nullable=True, comment='租户ID')
    )
    op.create_index('idx_tenant_id', 'test_environments', ['tenant_id'], unique=False)
    
    # 缺陷表添加 tenant_id
    op.add_column('defects', 
        sa.Column('tenant_id', sa.Integer(), nullable=True, comment='租户ID')
    )
    op.create_index('idx_tenant_id', 'defects', ['tenant_id'], unique=False)
    
    # 添加外键约束（可选，根据实际情况决定是否添加）
    # op.create_foreign_key('fk_test_suites_tenant', 'test_suites', 'tenants', ['tenant_id'], ['id'], ondelete='SET NULL')
    # op.create_foreign_key('fk_test_cases_tenant', 'test_cases', 'tenants', ['tenant_id'], ['id'], ondelete='SET NULL')
    # op.create_foreign_key('fk_test_plans_tenant', 'test_plans', 'tenants', ['tenant_id'], ['id'], ondelete='SET NULL')
    # op.create_foreign_key('fk_test_environments_tenant', 'test_environments', 'tenants', ['tenant_id'], ['id'], ondelete='SET NULL')
    # op.create_foreign_key('fk_defects_tenant', 'defects', 'tenants', ['tenant_id'], ['id'], ondelete='SET NULL')


def downgrade():
    """删除 tenant_id 字段"""
    
    # 删除索引
    op.drop_index('idx_tenant_id', table_name='defects')
    op.drop_index('idx_tenant_id', table_name='test_environments')
    op.drop_index('idx_tenant_id', table_name='test_plans')
    op.drop_index('idx_tenant_id', table_name='test_cases')
    op.drop_index('idx_tenant_id', table_name='test_suites')
    
    # 删除外键约束（如果之前添加了）
    # try:
    #     op.drop_constraint('fk_defects_tenant', 'defects', type_='foreignkey')
    #     op.drop_constraint('fk_test_environments_tenant', 'test_environments', type_='foreignkey')
    #     op.drop_constraint('fk_test_plans_tenant', 'test_plans', type_='foreignkey')
    #     op.drop_constraint('fk_test_cases_tenant', 'test_cases', type_='foreignkey')
    #     op.drop_constraint('fk_test_suites_tenant', 'test_suites', type_='foreignkey')
    # except Exception:
    #     pass  # 忽略不存在的约束
    
    # 删除列
    op.drop_column('defects', 'tenant_id')
    op.drop_column('test_environments', 'tenant_id')
    op.drop_column('test_plans', 'tenant_id')
    op.drop_column('test_cases', 'tenant_id')
    op.drop_column('test_suites', 'tenant_id')
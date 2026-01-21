"""Create Git skill repository tables

Revision ID: 007_create_git_skill_repos
Revises: 006_add_tools_count
Create Date: 2026-01-20 11:42:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = '007_create_git_skill_repos'
down_revision = '006_add_tools_count'
branch_labels = None
depends_on = None


def upgrade():
    """创建 Git 技能仓库相关表"""
    
    # 1. 创建 git_credentials 表
    op.create_table('git_credentials',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('name', sa.String(length=100), nullable=False, comment='凭证名称'),
        sa.Column('description', sa.String(length=500), nullable=True, comment='凭证描述'),
        sa.Column('auth_type', sa.String(length=20), nullable=False, comment='认证类型: token, ssh_key'),
        sa.Column('github_token', sa.Text(), nullable=True, comment='GitHub Personal Access Token (加密存储)'),
        sa.Column('ssh_key_content', sa.Text(), nullable=True, comment='SSH私钥内容 (加密存储)'),
        sa.Column('ssh_key_passphrase', sa.String(length=255), nullable=True, comment='SSH密钥密码 (可选,加密存储)'),
        sa.Column('github_login', sa.String(length=100), nullable=True, comment='GitHub用户名'),
        sa.Column('github_user_id', sa.String(length=50), nullable=True, comment='GitHub用户ID'),
        sa.Column('is_valid', sa.Boolean(), nullable=True, server_default='1', comment='凭证是否有效'),
        sa.Column('last_verified_at', sa.DateTime(), nullable=True, comment='最后验证时间'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间'),
        sa.Column('created_by', sa.String(length=100), nullable=True, comment='创建人'),
        sa.PrimaryKeyConstraint('id'),
        comment='Git凭证表'
    )
    
    # 创建索引
    op.create_index('idx_auth_type', 'git_credentials', ['auth_type'], unique=False)

    # 2. 创建 skill_repositories 表
    op.create_table('skill_repositories',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('name', sa.String(length=100), nullable=False, comment='仓库名称'),
        sa.Column('description', sa.String(length=500), nullable=True, comment='仓库描述'),
        sa.Column('git_url', sa.String(length=500), nullable=False, comment='Git仓库URL'),
        sa.Column('branch', sa.String(length=100), nullable=True, server_default='main', comment='分支名称'),
        sa.Column('skills_path', sa.String(length=500), nullable=True, server_default='/', comment='技能文件在仓库中的路径'),
        sa.Column('auth_type', sa.String(length=20), nullable=True, server_default='public', comment='认证类型: public, token, ssh_key'),
        sa.Column('git_credential_id', sa.Integer(), nullable=True, comment='Git凭证ID'),
        sa.Column('sync_mode', sa.String(length=20), nullable=True, server_default='manual', comment='同步模式: manual, scheduled, webhook'),
        sa.Column('sync_interval', sa.Integer(), nullable=True, server_default='60', comment='定时同步间隔(分钟)'),
        sa.Column('webhook_secret', sa.String(length=100), nullable=True, comment='Webhook密钥'),
        sa.Column('status', sa.String(length=20), nullable=True, server_default='idle', comment='状态: idle, syncing, success, error'),
        sa.Column('last_sync_at', sa.DateTime(), nullable=True, comment='最后同步时间'),
        sa.Column('last_sync_status', sa.String(length=20), nullable=True, comment='最后同步状态: success, error'),
        sa.Column('last_sync_message', sa.Text(), nullable=True, comment='最后同步消息'),
        sa.Column('skills_count', sa.Integer(), nullable=True, server_default='0', comment='技能数量'),
        sa.Column('is_enabled', sa.Boolean(), nullable=True, server_default='1', comment='是否启用'),
        sa.Column('auto_sync', sa.Boolean(), nullable=True, server_default='0', comment='是否自动同步'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间'),
        sa.Column('created_by', sa.String(length=100), nullable=True, comment='创建人'),
        sa.PrimaryKeyConstraint('id'),
        comment='技能仓库表'
    )
    
    # 创建索引
    op.create_index('idx_auth_type', 'skill_repositories', ['auth_type'], unique=False)
    op.create_index('idx_sync_mode', 'skill_repositories', ['sync_mode'], unique=False)
    op.create_index('idx_status', 'skill_repositories', ['status'], unique=False)
    op.create_index('idx_is_enabled', 'skill_repositories', ['is_enabled'], unique=False)
    
    # 添加外键约束
    op.create_foreign_key('fk_skill_repositories_git_credential', 'skill_repositories', 'git_credentials', ['git_credential_id'], ['id'], ondelete='SET NULL')

    # 3. 创建 git_skills 表
    op.create_table('git_skills',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('repository_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False, comment='技能名称'),
        sa.Column('code', sa.String(length=100), nullable=False, comment='技能代码'),
        sa.Column('description', sa.Text(), nullable=True, comment='技能描述'),
        sa.Column('script_content', sa.Text(), nullable=True, comment='技能内容'),
        sa.Column('script_type', sa.String(length=50), nullable=True, comment='脚本类型: python, javascript, yaml, json'),
        sa.Column('params_schema', sa.Text(), nullable=True, comment='参数定义(JSON格式)'),
        sa.Column('git_commit_hash', sa.String(length=50), nullable=True, comment='Git commit hash'),
        sa.Column('git_commit_message', sa.Text(), nullable=True, comment='Git commit message'),
        sa.Column('git_commit_author', sa.String(length=100), nullable=True, comment='Git commit author'),
        sa.Column('git_commit_date', sa.DateTime(), nullable=True, comment='Git commit date'),
        sa.Column('file_path', sa.String(length=500), nullable=True, comment='文件在仓库中的路径'),
        sa.Column('usage_count', sa.Integer(), nullable=True, server_default='0', comment='使用次数'),
        sa.Column('last_used_at', sa.DateTime(), nullable=True, comment='最后使用时间'),
        sa.Column('status', sa.String(length=20), nullable=True, server_default='active', comment='状态: active, inactive, error'),
        sa.Column('is_enabled', sa.Boolean(), nullable=True, server_default='1', comment='是否启用'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        comment='Git技能表'
    )
    
    # 创建索引
    op.create_index('idx_repository_id', 'git_skills', ['repository_id'], unique=False)
    op.create_index('idx_code', 'git_skills', ['code'], unique=False)
    op.create_index('idx_script_type', 'git_skills', ['script_type'], unique=False)
    op.create_index('idx_status', 'git_skills', ['status'], unique=False)
    
    # 添加外键约束
    op.create_foreign_key('fk_git_skills_repository', 'git_skills', 'skill_repositories', ['repository_id'], ['id'], ondelete='CASCADE')

    # 4. 创建 skill_sync_logs 表
    op.create_table('skill_sync_logs',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('repository_id', sa.Integer(), nullable=False),
        sa.Column('sync_type', sa.String(length=20), nullable=False, comment='同步类型: manual, scheduled, webhook'),
        sa.Column('skills_added', sa.Integer(), nullable=True, server_default='0', comment='新增技能数'),
        sa.Column('skills_updated', sa.Integer(), nullable=True, server_default='0', comment='更新技能数'),
        sa.Column('skills_deleted', sa.Integer(), nullable=True, server_default='0', comment='删除技能数'),
        sa.Column('skills_error', sa.Integer(), nullable=True, server_default='0', comment='错误技能数'),
        sa.Column('status', sa.String(length=20), nullable=True, server_default='running', comment='状态: running, success, error, partial'),
        sa.Column('error_message', sa.Text(), nullable=True, comment='错误消息'),
        sa.Column('started_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP'), comment='开始时间'),
        sa.Column('completed_at', sa.DateTime(), nullable=True, comment='完成时间'),
        sa.Column('duration', sa.Float(), nullable=True, comment='执行时长(秒)'),
        sa.Column('triggered_by', sa.String(length=100), nullable=True, comment='触发人/触发源'),
        sa.Column('git_commit_hash', sa.String(length=50), nullable=True, comment='同步的commit hash'),
        sa.Column('git_commit_message', sa.Text(), nullable=True, comment='同步的commit message'),
        sa.PrimaryKeyConstraint('id'),
        comment='技能同步日志表'
    )
    
    # 创建索引
    op.create_index('idx_repository_id', 'skill_sync_logs', ['repository_id'], unique=False)
    op.create_index('idx_sync_type', 'skill_sync_logs', ['sync_type'], unique=False)
    op.create_index('idx_status', 'skill_sync_logs', ['status'], unique=False)
    op.create_index('idx_started_at', 'skill_sync_logs', ['started_at'], unique=False)
    
    # 添加外键约束
    op.create_foreign_key('fk_skill_sync_logs_repository', 'skill_sync_logs', 'skill_repositories', ['repository_id'], ['id'], ondelete='CASCADE')


def downgrade():
    """回滚迁移"""
    
    # 删除 skill_sync_logs 表
    op.drop_constraint('fk_skill_sync_logs_repository', 'skill_sync_logs', type_='foreignkey')
    op.drop_index('idx_started_at', table_name='skill_sync_logs')
    op.drop_index('idx_status', table_name='skill_sync_logs')
    op.drop_index('idx_sync_type', table_name='skill_sync_logs')
    op.drop_index('idx_repository_id', table_name='skill_sync_logs')
    op.drop_table('skill_sync_logs')
    
    # 删除 git_skills 表
    op.drop_constraint('fk_git_skills_repository', 'git_skills', type_='foreignkey')
    op.drop_index('idx_status', table_name='git_skills')
    op.drop_index('idx_script_type', table_name='git_skills')
    op.drop_index('idx_code', table_name='git_skills')
    op.drop_index('idx_repository_id', table_name='git_skills')
    op.drop_table('git_skills')
    
    # 删除 skill_repositories 表
    op.drop_constraint('fk_skill_repositories_git_credential', 'skill_repositories', type_='foreignkey')
    op.drop_index('idx_is_enabled', table_name='skill_repositories')
    op.drop_index('idx_status', table_name='skill_repositories')
    op.drop_index('idx_sync_mode', table_name='skill_repositories')
    op.drop_index('idx_auth_type', table_name='skill_repositories')
    op.drop_table('skill_repositories')
    
    # 删除 git_credentials 表
    op.drop_index('idx_auth_type', table_name='git_credentials')
    op.drop_table('git_credentials')
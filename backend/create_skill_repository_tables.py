"""
创建 Git 技能仓库相关数据表
"""
from app import create_app, db
from sqlalchemy import text

def create_skill_repository_tables():
    """创建 Git 技能仓库相关表"""
    app = create_app()

    with app.app_context():
        inspector = db.inspect(db.engine)

        # 创建 git_credentials 表
        if 'git_credentials' not in inspector.get_table_names():
            print("创建 git_credentials 表...")
            with db.engine.connect() as conn:
                conn.execute(text("""
                    CREATE TABLE git_credentials (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(100) NOT NULL COMMENT '凭证名称',
                        description VARCHAR(500) COMMENT '凭证描述',
                        auth_type VARCHAR(20) NOT NULL COMMENT '认证类型: token, ssh_key',
                        github_token TEXT COMMENT 'GitHub Personal Access Token (加密存储)',
                        ssh_key_content TEXT COMMENT 'SSH私钥内容 (加密存储)',
                        ssh_key_passphrase VARCHAR(255) COMMENT 'SSH密钥密码 (可选,加密存储)',
                        github_login VARCHAR(100) COMMENT 'GitHub用户名',
                        github_user_id VARCHAR(50) COMMENT 'GitHub用户ID',
                        is_valid BOOLEAN DEFAULT TRUE COMMENT '凭证是否有效',
                        last_verified_at DATETIME COMMENT '最后验证时间',
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                        created_by VARCHAR(100) COMMENT '创建人',
                        INDEX idx_auth_type (auth_type)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                    COMMENT='Git凭证表'
                """))
                conn.commit()
            print("成功创建 git_credentials 表")
        else:
            print("git_credentials 表已存在")

        # 创建 skill_repositories 表
        if 'skill_repositories' not in inspector.get_table_names():
            print("创建 skill_repositories 表...")
            with db.engine.connect() as conn:
                conn.execute(text("""
                    CREATE TABLE skill_repositories (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(100) NOT NULL COMMENT '仓库名称',
                        description VARCHAR(500) COMMENT '仓库描述',
                        git_url VARCHAR(500) NOT NULL COMMENT 'Git仓库URL',
                        branch VARCHAR(100) DEFAULT 'main' COMMENT '分支名称',
                        skills_path VARCHAR(500) DEFAULT '/' COMMENT '技能文件在仓库中的路径',
                        auth_type VARCHAR(20) DEFAULT 'public' COMMENT '认证类型: public, token, ssh_key',
                        git_credential_id INT COMMENT 'Git凭证ID',
                        sync_mode VARCHAR(20) DEFAULT 'manual' COMMENT '同步模式: manual, scheduled, webhook',
                        sync_interval INT DEFAULT 60 COMMENT '定时同步间隔(分钟)',
                        webhook_secret VARCHAR(100) COMMENT 'Webhook密钥',
                        status VARCHAR(20) DEFAULT 'idle' COMMENT '状态: idle, syncing, success, error',
                        last_sync_at DATETIME COMMENT '最后同步时间',
                        last_sync_status VARCHAR(20) COMMENT '最后同步状态: success, error',
                        last_sync_message TEXT COMMENT '最后同步消息',
                        skills_count INT DEFAULT 0 COMMENT '技能数量',
                        is_enabled BOOLEAN DEFAULT TRUE COMMENT '是否启用',
                        auto_sync BOOLEAN DEFAULT FALSE COMMENT '是否自动同步',
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                        created_by VARCHAR(100) COMMENT '创建人',
                        FOREIGN KEY (git_credential_id) REFERENCES git_credentials(id) ON DELETE SET NULL,
                        INDEX idx_auth_type (auth_type),
                        INDEX idx_sync_mode (sync_mode),
                        INDEX idx_status (status),
                        INDEX idx_is_enabled (is_enabled)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                    COMMENT='技能仓库表'
                """))
                conn.commit()
            print("成功创建 skill_repositories 表")
        else:
            print("skill_repositories 表已存在")

        # 创建 git_skills 表
        if 'git_skills' not in inspector.get_table_names():
            print("创建 git_skills 表...")
            with db.engine.connect() as conn:
                conn.execute(text("""
                    CREATE TABLE git_skills (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        repository_id INT NOT NULL,
                        name VARCHAR(200) NOT NULL COMMENT '技能名称',
                        code VARCHAR(100) NOT NULL COMMENT '技能代码',
                        description TEXT COMMENT '技能描述',
                        script_content TEXT COMMENT '技能内容',
                        script_type VARCHAR(50) COMMENT '脚本类型: python, javascript, yaml, json',
                        params_schema TEXT COMMENT '参数定义(JSON格式)',
                        git_commit_hash VARCHAR(50) COMMENT 'Git commit hash',
                        git_commit_message TEXT COMMENT 'Git commit message',
                        git_commit_author VARCHAR(100) COMMENT 'Git commit author',
                        git_commit_date DATETIME COMMENT 'Git commit date',
                        file_path VARCHAR(500) COMMENT '文件在仓库中的路径',
                        usage_count INT DEFAULT 0 COMMENT '使用次数',
                        last_used_at DATETIME COMMENT '最后使用时间',
                        status VARCHAR(20) DEFAULT 'active' COMMENT '状态: active, inactive, error',
                        is_enabled BOOLEAN DEFAULT TRUE COMMENT '是否启用',
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                        FOREIGN KEY (repository_id) REFERENCES skill_repositories(id) ON DELETE CASCADE,
                        INDEX idx_repository_id (repository_id),
                        INDEX idx_code (code),
                        INDEX idx_script_type (script_type),
                        INDEX idx_status (status)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                    COMMENT='Git技能表'
                """))
                conn.commit()
            print("成功创建 git_skills 表")
        else:
            print("git_skills 表已存在")

        # 创建 skill_sync_logs 表
        if 'skill_sync_logs' not in inspector.get_table_names():
            print("创建 skill_sync_logs 表...")
            with db.engine.connect() as conn:
                conn.execute(text("""
                    CREATE TABLE skill_sync_logs (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        repository_id INT NOT NULL,
                        sync_type VARCHAR(20) NOT NULL COMMENT '同步类型: manual, scheduled, webhook',
                        skills_added INT DEFAULT 0 COMMENT '新增技能数',
                        skills_updated INT DEFAULT 0 COMMENT '更新技能数',
                        skills_deleted INT DEFAULT 0 COMMENT '删除技能数',
                        skills_error INT DEFAULT 0 COMMENT '错误技能数',
                        status VARCHAR(20) DEFAULT 'running' COMMENT '状态: running, success, error, partial',
                        error_message TEXT COMMENT '错误消息',
                        started_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '开始时间',
                        completed_at DATETIME COMMENT '完成时间',
                        duration FLOAT COMMENT '执行时长(秒)',
                        triggered_by VARCHAR(100) COMMENT '触发人/触发源',
                        git_commit_hash VARCHAR(50) COMMENT '同步的commit hash',
                        git_commit_message TEXT COMMENT '同步的commit message',
                        FOREIGN KEY (repository_id) REFERENCES skill_repositories(id) ON DELETE CASCADE,
                        INDEX idx_repository_id (repository_id),
                        INDEX idx_sync_type (sync_type),
                        INDEX idx_status (status),
                        INDEX idx_started_at (started_at)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                    COMMENT='技能同步日志表'
                """))
                conn.commit()
            print("成功创建 skill_sync_logs 表")
        else:
            print("skill_sync_logs 表已存在")

        print("\n所有表创建完成!")

if __name__ == '__main__':
    create_skill_repository_tables()

"""
创建 MCP 工具和资源表
"""
from app import create_app, db
from sqlalchemy import text

def create_mcp_tables():
    """创建 MCP 工具和资源表"""
    app = create_app()

    with app.app_context():
        inspector = db.inspect(db.engine)

        # 检查并添加 resources_count 列
        columns = [col['name'] for col in inspector.get_columns('mcp_servers')]
        if 'resources_count' not in columns:
            print("添加 resources_count 列到 mcp_servers 表...")
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE mcp_servers ADD COLUMN resources_count INT DEFAULT 0 COMMENT 'MCP提供的资源数量'"))
                conn.commit()
            print("成功添加 resources_count 列")
        else:
            print("resources_count 列已存在")

        # 检查并添加 last_sync_at 列
        if 'last_sync_at' not in columns:
            print("添加 last_sync_at 列到 mcp_servers 表...")
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE mcp_servers ADD COLUMN last_sync_at DATETIME COMMENT '最后同步时间'"))
                conn.commit()
            print("成功添加 last_sync_at 列")
        else:
            print("last_sync_at 列已存在")

        # 创建 mcp_tools 表
        if 'mcp_tools' not in inspector.get_table_names():
            print("创建 mcp_tools 表...")
            with db.engine.connect() as conn:
                conn.execute(text("""
                    CREATE TABLE mcp_tools (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        mcp_id INT NOT NULL,
                        name VARCHAR(200) NOT NULL,
                        description TEXT,
                        input_schema TEXT,
                        usage_count INT DEFAULT 0,
                        last_used_at DATETIME,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        FOREIGN KEY (mcp_id) REFERENCES mcp_servers(id) ON DELETE CASCADE,
                        INDEX idx_mcp_id (mcp_id)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                    COMMENT='MCP工具表'
                """))
                conn.commit()
            print("成功创建 mcp_tools 表")
        else:
            print("mcp_tools 表已存在")

        # 创建 mcp_resources 表
        if 'mcp_resources' not in inspector.get_table_names():
            print("创建 mcp_resources 表...")
            with db.engine.connect() as conn:
                conn.execute(text("""
                    CREATE TABLE mcp_resources (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        mcp_id INT NOT NULL,
                        uri VARCHAR(500) NOT NULL,
                        name VARCHAR(200),
                        description TEXT,
                        mime_type VARCHAR(100),
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        FOREIGN KEY (mcp_id) REFERENCES mcp_servers(id) ON DELETE CASCADE,
                        INDEX idx_mcp_id (mcp_id)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                    COMMENT='MCP资源表'
                """))
                conn.commit()
            print("成功创建 mcp_resources 表")
        else:
            print("mcp_resources 表已存在")

        # 创建 mcp_tool_executions 表
        if 'mcp_tool_executions' not in inspector.get_table_names():
            print("创建 mcp_tool_executions 表...")
            with db.engine.connect() as conn:
                conn.execute(text("""
                    CREATE TABLE mcp_tool_executions (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        tool_id INT NOT NULL,
                        parameters TEXT,
                        result TEXT,
                        status VARCHAR(20) DEFAULT 'success',
                        error_message TEXT,
                        execution_time FLOAT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (tool_id) REFERENCES mcp_tools(id) ON DELETE CASCADE,
                        INDEX idx_tool_id (tool_id)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                    COMMENT='MCP工具执行记录表'
                """))
                conn.commit()
            print("成功创建 mcp_tool_executions 表")
        else:
            print("mcp_tool_executions 表已存在")

        print("\n所有表和字段创建完成!")

if __name__ == '__main__':
    create_mcp_tables()

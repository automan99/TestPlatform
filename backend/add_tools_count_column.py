"""
添加 tools_count 字段到 mcp_servers 表
"""
from app import create_app, db

def add_tools_count_column():
    """添加 tools_count 列"""
    app = create_app()

    with app.app_context():
        # 检查列是否已存在
        from sqlalchemy import inspect, text
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('mcp_servers')]

        if 'tools_count' not in columns:
            print("添加 tools_count 列到 mcp_servers 表...")
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE mcp_servers ADD COLUMN tools_count INT DEFAULT 0 COMMENT 'MCP提供的工具数量'"))
                conn.commit()
            print("成功添加 tools_count 列")
        else:
            print("tools_count 列已存在，跳过")

        print("完成!")

if __name__ == '__main__':
    add_tools_count_column()

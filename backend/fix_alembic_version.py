#!/usr/bin/env python3
"""
修复 Alembic 版本表
当数据库表已存在但 alembic_version 记录不正确时使用
"""
from run import app
from app import db
from sqlalchemy import text

def check_and_fix_alembic_version():
    """检查并修复 alembic_version 表"""
    with app.app_context():
        # 获取数据库中所有表
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()

        print("=== 数据库中的表 ===")
        for table in sorted(tables):
            print(f"  - {table}")
        print(f"\n总共 {len(tables)} 个表\n")

        # 检查 alembic_version 表
        result = db.session.execute(text("SELECT version_num FROM alembic_version"))
        current_versions = [row[0] for row in result.fetchall()]

        print(f"=== 当前 alembic_version 记录 ===")
        if current_versions:
            for v in current_versions:
                print(f"  - {v}")
        else:
            print("  (空)")
        print()

        # 根据存在的表判断应该设置的版本
        # 检查关键表
        key_tables = {
            'llm_models': '009_create_llm_models',
            'git_credentials': '007_create_git_skill_repos',
            'skill_repositories': '007_create_git_skill_repos',
            'git_skills': '007_create_git_skill_repos',
            'skill_sync_logs': '007_create_git_skill_repos',
            'mcp_servers': 'e3f4g5h6i7j8',  # MCP相关表
            'projects': '003_create_projects',
        }

        # 找出最新的版本
        latest_version = None
        for table, version in key_tables.items():
            if table in tables:
                latest_version = version
                print(f"检测到表 '{table}' -> 版本 {version}")

        if not latest_version:
            print("\n无法确定版本，请手动检查")
            return

        print(f"\n=== 建议设置版本为: {latest_version} ===")

        # 更新 alembic_version
        db.session.execute(text("DELETE FROM alembic_version"))
        db.session.execute(
            text("INSERT INTO alembic_version (version_num) VALUES (:version)"),
            {"version": latest_version}
        )
        db.session.commit()

        print(f"已更新 alembic_version 表")
        print("\n=== 修复完成！现在可以运行: ===")
        print("flask db upgrade")

if __name__ == '__main__':
    check_and_fix_alembic_version()

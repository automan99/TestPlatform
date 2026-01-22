"""
修复 alembic_version 表的迁移版本
将数据库标记为 '010_merge_branches'（当前最新的合并版本）
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))


def stamp_migration():
    """
    将 alembic_version 更新到 '010_merge_branches'
    """
    from app import create_app, db
    from sqlalchemy import text

    app = create_app()

    with app.app_context():
        # 获取当前数据库中的迁移版本
        result = db.session.execute(text("SELECT version_num FROM alembic_version"))
        current_versions = [row[0] for row in result]
        print(f"当前 alembic_version: {current_versions}")

        # 目标版本 - 010_merge_branches 是合并了两个分支的最新版本
        target_version = '010_merge_branches'

        print(f"将数据库标记为版本: {target_version}")

        # 删除旧的版本记录
        db.session.execute(text("DELETE FROM alembic_version"))

        # 插入新的版本记录
        db.session.execute(
            text("INSERT INTO alembic_version (version_num) VALUES (:version)"),
            {"version": target_version}
        )
        db.session.commit()

        # 验证更新结果
        result = db.session.execute(text("SELECT version_num FROM alembic_version"))
        new_versions = [row[0] for row in result]
        print(f"更新后的 alembic_version: {new_versions}")

        print(f"\n成功！数据库已标记为版本 {target_version}")
        print("现在运行 'python run.py' 或 'flask db upgrade' 将正常工作")


if __name__ == '__main__':
    stamp_migration()

"""
测试数据库连接和创建表
"""
from run import app, db
from app.models import Tenant


def test_db():
    """测试数据库"""
    with app.app_context():
        try:
            # 创建所有表
            db.create_all()
            print("数据库表创建成功")

            # 检查租户表是否存在
            tenants = Tenant.query.all()
            print(f"当前租户数量: {len(tenants)}")

            for tenant in tenants:
                print(f"  - {tenant.name} ({tenant.code})")

            return True
        except Exception as e:
            print(f"错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == '__main__':
    test_db()

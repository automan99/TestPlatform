"""
初始化测试数据
"""
from run import app, db
from app.models import Tenant, User
from datetime import datetime, timedelta


def init_test_data():
    """初始化测试数据"""
    with app.app_context():
        # 首先创建所有表
        try:
            db.create_all()
            print("✓ 数据库表创建成功")
        except Exception as e:
            print(f"创建表时出错: {str(e)}")

        # 检查并创建测试租户
        test_tenant = Tenant.query.filter_by(code='test').first()
        if not test_tenant:
            test_tenant = Tenant(
                name='测试租户',
                code='test',
                description='用于测试的默认租户',
                status='active',
                is_active=True,
                max_users=100,
                max_projects=50,
                max_storage_gb=100,
                expire_date=datetime.now() + timedelta(days=3650),
                settings={
                    'allow_register': True,
                    'default_locale': 'zh-CN'
                }
            )
            db.session.add(test_tenant)
            print("✓ 创建测试租户")
        else:
            print("⊙ 测试租户已存在")

        # 检查并创建测试用户
        test_user = User.query.filter_by(username='admin').first()
        if not test_user:
            test_user = User(
                username='admin',
                real_name='管理员',
                email='admin@test.com',
                status='active',
                is_admin=True
            )
            test_user.set_password('admin123')
            db.session.add(test_user)
            print("✓ 创建测试用户 (用户名: admin, 密码: admin123)")
        else:
            print("⊙ 测试用户已存在")

        db.session.commit()

        print(f"\n初始化完成！")
        print(f"  租户: {test_tenant.name} (代码: {test_tenant.code})")
        print(f"  用户: {test_user.username} (密码: admin123)")


if __name__ == '__main__':
    init_test_data()

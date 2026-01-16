"""
添加 tenant_id 字段到现有表
"""
from run import app, db
from sqlalchemy import text


def add_tenant_columns():
    """添加tenant_id字段"""
    with app.app_context():
        # 定义需要添加tenant_id字段的表
        tables = [
            'test_suites',
            'test_cases',
            'test_plans',
            'test_environments',
            'defects'
        ]

        for table in tables:
            sql = f'ALTER TABLE {table} ADD COLUMN tenant_id INT NULL COMMENT "租户ID"'
            try:
                db.session.execute(text(sql))
                db.session.commit()
                print(f'✓ {table} 表添加 tenant_id 字段成功')
            except Exception as e:
                error_msg = str(e).lower()
                if 'duplicate column' in error_msg:
                    print(f'⊙ {table} 表 tenant_id 字段已存在，跳过')
                else:
                    print(f'✗ {table} 表添加失败: {str(e)}')
                    db.session.rollback()

        print('\n完成！')


if __name__ == '__main__':
    add_tenant_columns()

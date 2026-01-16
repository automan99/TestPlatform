"""
添加 users 表的新字段
"""
from run import app, db
from sqlalchemy import text


def add_user_columns():
    """添加users表的新字段"""
    with app.app_context():
        # 定义需要添加的字段
        statements = [
            # 添加头像字段
            "ALTER TABLE users ADD COLUMN avatar VARCHAR(255) NULL COMMENT '头像URL'",

            # 添加OAuth相关字段
            "ALTER TABLE users ADD COLUMN oauth_provider VARCHAR(50) NULL COMMENT 'OAuth提供商'",
            "ALTER TABLE users ADD COLUMN oauth_user_id VARCHAR(100) NULL COMMENT 'OAuth用户ID'",

            # 修改password_hash字段为可空（OAuth用户不需要密码）
            "ALTER TABLE users MODIFY password_hash VARCHAR(255) NULL COMMENT '密码哈希（OAuth用户可为空）'"
        ]

        for sql in statements:
            try:
                db.session.execute(text(sql))
                db.session.commit()
                print(f'✓ 执行成功: {sql[:50]}...')
            except Exception as e:
                error_msg = str(e).lower()
                if 'duplicate column' in error_msg:
                    print(f'⊙ 字段已存在，跳过')
                else:
                    print(f'✗ 执行失败: {sql[:50]}...')
                    print(f'  错误: {str(e)}')
                    db.session.rollback()

        print('\n完成！')


if __name__ == '__main__':
    add_user_columns()

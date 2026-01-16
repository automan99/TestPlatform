"""
添加 projects 表的数据库迁移脚本
"""
from run import app, db
from sqlalchemy import text


def add_projects_table():
    """创建projects表"""
    with app.app_context():
        # 创建projects表的SQL语句
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS `projects` (
            `id` INT NOT NULL AUTO_INCREMENT COMMENT '项目ID',
            `tenant_id` INT NULL COMMENT '租户ID',
            `name` VARCHAR(200) NOT NULL COMMENT '项目名称',
            `code` VARCHAR(50) NOT NULL COMMENT '项目代码',
            `description` TEXT NULL COMMENT '项目描述',
            `project_type` VARCHAR(50) DEFAULT 'web' COMMENT '项目类型: web, mobile, api, desktop',
            `status` VARCHAR(20) DEFAULT 'active' COMMENT '状态: active, archived, completed',
            `key` VARCHAR(10) NULL UNIQUE COMMENT '项目标识符（用于缺陷编号前缀）',
            `url` VARCHAR(500) NULL COMMENT '项目URL',
            `repository` VARCHAR(500) NULL COMMENT '代码仓库地址',
            `max_test_suites` INT DEFAULT 100 COMMENT '最大测试套件数',
            `max_test_cases` INT DEFAULT 1000 COMMENT '最大测试用例数',
            `max_test_plans` INT DEFAULT 50 COMMENT '最大测试计划数',
            `test_suite_count` INT DEFAULT 0 COMMENT '测试套件数',
            `test_case_count` INT DEFAULT 0 COMMENT '测试用例数',
            `test_plan_count` INT DEFAULT 0 COMMENT '测试计划数',
            `defect_count` INT DEFAULT 0 COMMENT '缺陷数',
            `sort_order` INT DEFAULT 0 COMMENT '排序',
            `icon` VARCHAR(100) NULL COMMENT '图标',
            `color` VARCHAR(20) DEFAULT '#409EFF' COMMENT '颜色',
            `owner` VARCHAR(100) NULL COMMENT '项目负责人',
            `lead` VARCHAR(100) NULL COMMENT '项目主管',
            `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
            `created_by` VARCHAR(100) NULL COMMENT '创建人',
            `updated_by` VARCHAR(100) NULL COMMENT '更新人',
            `is_deleted` BOOLEAN DEFAULT FALSE COMMENT '是否删除',
            PRIMARY KEY (`id`),
            INDEX `idx_tenant_id` (`tenant_id`),
            INDEX `idx_code` (`code`),
            INDEX `idx_key` (`key`),
            INDEX `idx_status` (`status`),
            CONSTRAINT `fk_projects_tenant` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='项目表';
        """

        try:
            db.session.execute(text(create_table_sql))
            db.session.commit()
            print('[OK] projects table created successfully')
        except Exception as e:
            error_msg = str(e).lower()
            if 'already exists' in error_msg:
                print('[INFO] projects table already exists, skipping')
            else:
                print(f'[ERROR] Failed to create projects table: {str(e)}')
                db.session.rollback()


if __name__ == '__main__':
    add_projects_table()
    print('\nDone!')

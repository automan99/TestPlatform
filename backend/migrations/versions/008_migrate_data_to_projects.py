"""Migrate data to projects

Revision ID: 008_migrate_data
Revises: 007_create_git_skill_repos
Create Date: 2026-01-20 11:42:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = '008_migrate_data'
down_revision = '007_create_git_skill_repos'
branch_labels = None
depends_on = None


def upgrade():
    """将现有数据迁移到项目"""
    
    # 1. 创建默认项目
    op.execute("""
        INSERT INTO projects (name, code, key, description, project_type, status, color, sort_order, created_at, updated_at, is_deleted)
        SELECT '默认项目', 'DEFAULT', 'DEF', '系统默认项目，包含所有未分类的测试数据', 'web', 'active', '#409EFF', 0, NOW(), NOW(), 0
        WHERE NOT EXISTS (SELECT 1 FROM projects WHERE code = 'DEFAULT')
    """)
    
    # 2. 创建测试项目
    op.execute("""
        INSERT INTO projects (name, code, key, description, project_type, status, color, sort_order, created_at, updated_at, is_deleted)
        SELECT '测试项目', 'TEST', 'TST', '用于测试的项目', 'web', 'active', '#67C23A', 1, NOW(), NOW(), 0
        WHERE NOT EXISTS (SELECT 1 FROM projects WHERE code = 'TEST')
    """)
    
    # 3. 迁移测试套件（将没有project_id的套件关联到默认项目）
    op.execute("""
        UPDATE test_suites
        SET project_id = (SELECT id FROM projects WHERE code = 'DEFAULT' LIMIT 1)
        WHERE project_id IS NULL
    """)
    
    # 4. 迁移测试计划（将没有project_id的计划关联到默认项目）
    op.execute("""
        UPDATE test_plans
        SET project_id = (SELECT id FROM projects WHERE code = 'DEFAULT' LIMIT 1)
        WHERE project_id IS NULL
    """)
    
    # 5. 迁移缺陷（将没有project_id的缺陷关联到默认项目）
    op.execute("""
        UPDATE defects
        SET project_id = (SELECT id FROM projects WHERE code = 'DEFAULT' LIMIT 1)
        WHERE project_id IS NULL
    """)
    
    # 6. 更新项目统计信息
    op.execute("""
        UPDATE projects p
        SET p.test_suite_count = (SELECT COUNT(*) FROM test_suites WHERE project_id = p.id),
            p.test_case_count = (SELECT COUNT(*) FROM test_cases tc JOIN test_suites ts ON tc.suite_id = ts.id WHERE ts.project_id = p.id),
            p.test_plan_count = (SELECT COUNT(*) FROM test_plans WHERE project_id = p.id),
            p.defect_count = (SELECT COUNT(*) FROM defects WHERE project_id = p.id),
            p.updated_at = NOW()
        WHERE p.is_deleted = 0
    """)


def downgrade():
    """回滚数据迁移"""
    
    # 清空项目统计信息
    op.execute("""
        UPDATE projects
        SET test_suite_count = 0,
            test_case_count = 0,
            test_plan_count = 0,
            defect_count = 0,
            updated_at = NOW()
    """)
    
    # 取消关联的项目ID（可选，回滚时将project_id设置为NULL）
    # 实际应用中可能需要更复杂的逻辑来处理数据回滚
    op.execute("""
        UPDATE test_suites SET project_id = NULL WHERE project_id IN (SELECT id FROM projects WHERE code IN ('DEFAULT', 'TEST'))
    """)
    
    op.execute("""
        UPDATE test_plans SET project_id = NULL WHERE project_id IN (SELECT id FROM projects WHERE code IN ('DEFAULT', 'TEST'))
    """)
    
    op.execute("""
        UPDATE defects SET project_id = NULL WHERE project_id IN (SELECT id FROM projects WHERE code IN ('DEFAULT', 'TEST'))
    """)
    
    # 删除迁移创建的项目
    op.execute("DELETE FROM projects WHERE code IN ('DEFAULT', 'TEST')")
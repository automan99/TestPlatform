"""
数据迁移脚本：将现有数据关联到项目
"""
from run import app, db
from app.models import Project, TestSuite, TestPlan, Defect
from sqlalchemy import text


def migrate_data_to_projects():
    """将现有数据迁移到项目"""
    with app.app_context():
        print('Starting data migration...\n')

        # 1. 创建默认项目
        print('1. Creating default project...')
        default_project = Project.query.filter_by(code='DEFAULT').first()

        if not default_project:
            default_project = Project(
                name='默认项目',
                code='DEFAULT',
                key='DEF',
                description='系统默认项目，包含所有未分类的测试数据',
                project_type='web',
                status='active',
                color='#409EFF',
                sort_order=0
            )
            db.session.add(default_project)
            db.session.commit()
            print(f'[OK] Created default project: {default_project.name} (ID: {default_project.id})')
        else:
            print(f'[INFO] Default project already exists: {default_project.name} (ID: {default_project.id})')

        # 2. 创建测试项目
        print('\n2. Creating test project...')
        test_project = Project.query.filter_by(code='TEST').first()

        if not test_project:
            test_project = Project(
                name='测试项目',
                code='TEST',
                key='TST',
                description='用于测试的项目',
                project_type='web',
                status='active',
                color='#67C23A',
                sort_order=1
            )
            db.session.add(test_project)
            db.session.commit()
            print(f'[OK] Created test project: {test_project.name} (ID: {test_project.id})')
        else:
            print(f'[INFO] Test project already exists: {test_project.name} (ID: {test_project.id})')

        # 3. 迁移测试套件（将没有project_id的套件关联到默认项目）
        print('\n3. Migrating test suites...')
        suites_without_project = TestSuite.query.filter(
            TestSuite.project_id.is_(None)
        ).all()

        suites_count = 0
        for suite in suites_without_project:
            suite.project_id = default_project.id
            suites_count += 1

        if suites_count > 0:
            db.session.commit()
            print(f'[OK] Migrated {suites_count} test suites to default project')
        else:
            print('[INFO] No test suites to migrate')

        # 4. 迁移测试计划（将没有project_id的计划关联到默认项目）
        print('\n4. Migrating test plans...')
        plans_without_project = TestPlan.query.filter(
            TestPlan.project_id.is_(None)
        ).all()

        plans_count = 0
        for plan in plans_without_project:
            plan.project_id = default_project.id
            plans_count += 1

        if plans_count > 0:
            db.session.commit()
            print(f'[OK] Migrated {plans_count} test plans to default project')
        else:
            print('[INFO] No test plans to migrate')

        # 5. 迁移缺陷（将没有project_id的缺陷关联到默认项目）
        print('\n5. Migrating defects...')
        defects_without_project = Defect.query.filter(
            Defect.project_id.is_(None)
        ).all()

        defects_count = 0
        for defect in defects_without_project:
            defect.project_id = default_project.id
            defects_count += 1

        if defects_count > 0:
            db.session.commit()
            print(f'[OK] Migrated {defects_count} defects to default project')
        else:
            print('[INFO] No defects to migrate')

        # 6. 更新项目统计信息
        print('\n6. Updating project statistics...')
        all_projects = Project.query.filter_by(is_deleted=False).all()

        for project in all_projects:
            try:
                project.update_statistics()
                print(f'[OK] Updated statistics for {project.name} - '
                      f'Suites:{project.test_suite_count}, '
                      f'Cases:{project.test_case_count}, '
                      f'Plans:{project.test_plan_count}, '
                      f'Defects:{project.defect_count}')
            except Exception as e:
                print(f'[ERROR] Failed to update statistics for {project.name}: {str(e)}')

        print('\n[OK] Data migration completed!')
        print('\nProject list:')
        for p in all_projects:
            print(f'  - {p.name} ({p.code}) - ID: {p.id}')


if __name__ == '__main__':
    migrate_data_to_projects()

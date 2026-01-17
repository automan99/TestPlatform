"""
测试计划管理API
"""
from flask import request, current_app
from flask_restx import Namespace, Resource, fields
from app import db
from app.models import TestPlan, TestPlanCase, TestExecution, TestCase, TestPlanFolder
from app.utils import success_response, error_response
import json
from datetime import datetime, date

# 命名空间
test_plan_ns = Namespace('TestPlans', description='测试计划管理')
test_execution_ns = Namespace('TestExecutions', description='测试执行管理')
test_plan_folder_ns = Namespace('TestPlanFolders', description='测试计划目录管理')

# Swagger模型定义
test_plan_model = test_plan_ns.model('TestPlan', {
    'name': fields.String(required=True, description='计划名称'),
    'plan_no': fields.String(description='计划编号'),
    'description': fields.String(description='描述'),
    'project_id': fields.Integer(description='项目ID'),
    'folder_id': fields.Integer(description='目录ID'),
    'start_date': fields.String(description='开始日期(YYYY-MM-DD)'),
    'end_date': fields.String(description='结束日期(YYYY-MM-DD)'),
    'status': fields.String(description='状态'),
    'priority': fields.String(description='优先级'),
    'build_version': fields.String(description='测试版本'),
    'target_environment_id': fields.Integer(description='目标环境ID'),
    'assigned_to': fields.String(description='指派给')
})

test_plan_folder_model = test_plan_folder_ns.model('TestPlanFolder', {
    'name': fields.String(required=True, description='目录名称'),
    'project_id': fields.Integer(required=True, description='项目ID'),
    'parent_id': fields.Integer(description='父目录ID'),
    'description': fields.String(description='描述')
})

test_execution_model = test_execution_ns.model('TestExecution', {
    'test_plan_id': fields.Integer(description='测试计划ID'),
    'test_case_id': fields.Integer(required=True, description='测试用例ID'),
    'test_plan_case_id': fields.Integer(description='计划用例关联ID'),
    'status': fields.String(description='执行状态'),
    'actual_result': fields.String(description='实际结果'),
    'notes': fields.String(description='备注'),
    'duration': fields.Integer(description='执行时长(秒)'),
    'environment_id': fields.Integer(description='环境ID'),
    'defect_ids': fields.String(description='关联缺陷ID(JSON)')
})


# ============== 测试计划API ==============

@test_plan_ns.route('')
class TestPlanListAPI(Resource):
    """测试计划列表API"""

    def get(self):
        """获取测试计划列表"""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            project_id = request.args.get('project_id', type=int)
            status = request.args.get('status')
            keyword = request.args.get('keyword')
            folder_id = request.args.get('folder_id', type=int)

            query = TestPlan.query.filter_by(is_deleted=False)

            if project_id:
                query = query.filter_by(project_id=project_id)
            if status:
                query = query.filter_by(status=status)
            if folder_id is not None:
                if folder_id == 0:
                    # 查询无目录的测试计划
                    query = query.filter(TestPlan.folder_id.is_(None))
                else:
                    query = query.filter_by(folder_id=folder_id)
            if keyword:
                query = query.filter(TestPlan.name.contains(keyword) |
                                     TestPlan.plan_no.contains(keyword))

            pagination = query.order_by(TestPlan.id.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )

            items = [item.to_dict() for item in pagination.items]

            return success_response(data={
                'items': items,
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page
            })
        except Exception as e:
            current_app.logger.error(f'获取测试计划失败: {str(e)}')
            return error_response(message=f'获取测试计划失败: {str(e)}', code=500)

    @test_plan_ns.expect(test_plan_model)
    def post(self):
        """创建测试计划"""
        try:
            data = request.get_json()

            # 处理日期
            start_date = None
            end_date = None
            if data.get('start_date'):
                start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d').date()
            if data.get('end_date'):
                end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d').date()

            test_plan = TestPlan(
                name=data.get('name'),
                plan_no=data.get('plan_no'),
                description=data.get('description'),
                project_id=data.get('project_id'),
                folder_id=data.get('folder_id'),
                start_date=start_date,
                end_date=end_date,
                status=data.get('status', 'draft'),
                priority=data.get('priority', 'medium'),
                build_version=data.get('build_version'),
                target_environment_id=data.get('target_environment_id'),
                assigned_to=data.get('assigned_to'),
                created_by=data.get('created_by')
            )

            db.session.add(test_plan)
            db.session.commit()

            return success_response(data=test_plan.to_dict(), message='创建成功', code=201)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'创建测试计划失败: {str(e)}')
            return error_response(message=f'创建测试计划失败: {str(e)}', code=500)


@test_plan_ns.route('/<int:plan_id>')
class TestPlanAPI(Resource):
    """测试计划详情API"""

    def get(self, plan_id):
        """获取测试计划详情"""
        try:
            test_plan = TestPlan.query.get_or_404(plan_id)

            plan_dict = test_plan.to_dict()
            # 获取关联的测试用例，包含用例详细信息
            plan_cases = TestPlanCase.query.filter_by(test_plan_id=plan_id).all()
            test_cases_data = []
            for pc in plan_cases:
                case_dict = pc.to_dict()
                # 添加测试用例的详细信息
                if pc.test_case:
                    case_dict['case_no'] = pc.test_case.case_no
                    case_dict['name'] = pc.test_case.name
                    case_dict['priority'] = pc.test_case.priority
                    case_dict['case_type'] = pc.test_case.case_type
                else:
                    case_dict['case_no'] = None
                    case_dict['name'] = '用例已删除'
                    case_dict['priority'] = 'medium'
                    case_dict['case_type'] = 'functional'
                test_cases_data.append(case_dict)
            plan_dict['test_cases'] = test_cases_data

            return success_response(data=plan_dict)
        except Exception as e:
            return error_response(message=f'获取测试计划失败: {str(e)}', code=500)

    @test_plan_ns.expect(test_plan_model)
    def put(self, plan_id):
        """更新测试计划"""
        try:
            test_plan = TestPlan.query.get_or_404(plan_id)
            data = request.get_json()

            test_plan.name = data.get('name', test_plan.name)
            test_plan.plan_no = data.get('plan_no', test_plan.plan_no)
            test_plan.description = data.get('description', test_plan.description)
            test_plan.project_id = data.get('project_id', test_plan.project_id)
            test_plan.folder_id = data.get('folder_id', test_plan.folder_id)
            test_plan.status = data.get('status', test_plan.status)
            test_plan.priority = data.get('priority', test_plan.priority)
            test_plan.build_version = data.get('build_version', test_plan.build_version)
            test_plan.target_environment_id = data.get('target_environment_id', test_plan.target_environment_id)
            test_plan.assigned_to = data.get('assigned_to', test_plan.assigned_to)

            if data.get('start_date'):
                test_plan.start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d').date()
            if data.get('end_date'):
                test_plan.end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d').date()


            test_plan.updated_by = data.get('updated_by')

            db.session.commit()
            return success_response(data=test_plan.to_dict(), message='更新成功')
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'更新测试计划失败: {str(e)}', code=500)

    def delete(self, plan_id):
        """删除测试计划"""
        try:
            test_plan = TestPlan.query.get_or_404(plan_id)
            test_plan.is_deleted = True
            db.session.commit()
            return success_response(message='删除成功')
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'删除测试计划失败: {str(e)}', code=500)


@test_plan_ns.route('/<int:plan_id>/add-cases')
class TestPlanAddCasesAPI(Resource):
    """添加测试用例到计划API"""

    def post(self, plan_id):
        """添加测试用例到测试计划"""
        try:
            data = request.get_json()
            case_ids = data.get('case_ids', [])

            if not case_ids:
                return error_response(message='请选择要添加的用例', code=400)

            test_plan = TestPlan.query.get_or_404(plan_id)
            added_count = 0

            for case_id in case_ids:
                # 检查是否已存在
                existing = TestPlanCase.query.filter_by(
                    test_plan_id=plan_id, test_case_id=case_id
                ).first()

                if not existing:
                    plan_case = TestPlanCase(
                        test_plan_id=plan_id,
                        test_case_id=case_id,
                        sort_order=data.get('sort_order', 0)
                    )
                    db.session.add(plan_case)
                    added_count += 1

            db.session.commit()
            return success_response(message=f'成功添加 {added_count} 条用例')
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'添加用例失败: {str(e)}', code=500)


@test_plan_ns.route('/<int:plan_id>/remove-cases')
class TestPlanRemoveCasesAPI(Resource):
    """从计划移除测试用例API"""

    def post(self, plan_id):
        """从测试计划移除测试用例"""
        try:
            data = request.get_json()
            case_ids = data.get('case_ids', [])

            if not case_ids:
                return error_response(message='请选择要移除的用例', code=400)

            TestPlanCase.query.filter(
                TestPlanCase.test_plan_id == plan_id,
                TestPlanCase.test_case_id.in_(case_ids)
            ).delete(synchronize_session=False)

            db.session.commit()
            return success_response(message=f'成功移除 {len(case_ids)} 条用例')
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'移除用例失败: {str(e)}', code=500)


@test_plan_ns.route('/<int:plan_id>/execute')
class TestPlanExecuteAPI(Resource):
    """执行测试计划API"""

    def post(self, plan_id):
        """执行测试计划"""
        try:
            data = request.get_json()
            test_plan = TestPlan.query.get_or_404(plan_id)

            # 启动测试计划
            test_plan.status = 'active'
            db.session.commit()
            return success_response(
                data=test_plan.to_dict(),
                message='测试计划已启动，可手动执行用例'
            )
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'执行测试计划失败: {str(e)}', code=500)


# ============== 测试执行API ==============

@test_execution_ns.route('')
class TestExecutionListAPI(Resource):
    """测试执行列表API"""

    def get(self):
        """获取测试执行列表"""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            test_plan_id = request.args.get('test_plan_id', type=int)
            test_case_id = request.args.get('test_case_id', type=int)
            status = request.args.get('status')

            query = TestExecution.query

            if test_plan_id:
                query = query.filter_by(test_plan_id=test_plan_id)
            if test_case_id:
                query = query.filter_by(test_case_id=test_case_id)
            if status:
                query = query.filter_by(status=status)

            pagination = query.order_by(TestExecution.id.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )

            return success_response(data={
                'items': [item.to_dict() for item in pagination.items],
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page
            })
        except Exception as e:
            current_app.logger.error(f'获取测试执行记录失败: {str(e)}')
            return error_response(message=f'获取测试执行记录失败: {str(e)}', code=500)

    @test_execution_ns.expect(test_execution_model)
    def post(self):
        """创建测试执行记录"""
        try:
            data = request.get_json()

            execution = TestExecution(
                test_plan_id=data.get('test_plan_id'),
                test_case_id=data.get('test_case_id'),
                test_plan_case_id=data.get('test_plan_case_id'),
                status=data.get('status', 'not_executed'),
                executed_by=data.get('executed_by'),
                actual_result=data.get('actual_result'),
                notes=data.get('notes'),
                duration=data.get('duration'),
                environment_id=data.get('environment_id'),
                defect_ids=json.dumps(data.get('defect_ids')) if data.get('defect_ids') else None
            )

            db.session.add(execution)
            db.session.commit()

            # 更新计划用例的最后执行状态
            if execution.test_plan_case_id:
                plan_case = TestPlanCase.query.get(execution.test_plan_case_id)
                if plan_case:
                    plan_case.last_status = execution.status
                    plan_case.last_execution_id = execution.id
                    db.session.commit()

            return success_response(data=execution.to_dict(), message='创建成功', code=201)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'创建测试执行记录失败: {str(e)}')
            return error_response(message=f'创建测试执行记录失败: {str(e)}', code=500)


@test_execution_ns.route('/<int:execution_id>')
class TestExecutionAPI(Resource):
    """测试执行详情API"""

    def get(self, execution_id):
        """获取测试执行详情"""
        try:
            execution = TestExecution.query.get_or_404(execution_id)
            return success_response(data=execution.to_dict())
        except Exception as e:
            return error_response(message=f'获取测试执行详情失败: {str(e)}', code=500)

    @test_execution_ns.expect(test_execution_model)
    def put(self, execution_id):
        """更新测试执行记录"""
        try:
            execution = TestExecution.query.get_or_404(execution_id)
            data = request.get_json()

            execution.status = data.get('status', execution.status)
            execution.actual_result = data.get('actual_result', execution.actual_result)
            execution.notes = data.get('notes', execution.notes)
            execution.duration = data.get('duration', execution.duration)
            execution.environment_id = data.get('environment_id', execution.environment_id)

            if data.get('defect_ids') is not None:
                execution.defect_ids = json.dumps(data.get('defect_ids'))

            db.session.commit()

            # 更新计划用例的最后执行状态
            if execution.test_plan_case_id:
                plan_case = TestPlanCase.query.get(execution.test_plan_case_id)
                if plan_case:
                    plan_case.last_status = execution.status
                    db.session.commit()

            return success_response(data=execution.to_dict(), message='更新成功')
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'更新测试执行记录失败: {str(e)}', code=500)


# ============== 测试计划目录API ==============

@test_plan_folder_ns.route('')
class TestPlanFolderListAPI(Resource):
    """测试计划目录列表API"""

    def get(self):
        """获取测试计划目录树"""
        try:
            project_id = request.args.get('project_id', type=int)
            if not project_id:
                return error_response(message='项目ID不能为空', code=400)

            # 获取所有目录
            folders = TestPlanFolder.query.filter_by(
                project_id=project_id,
                is_deleted=False
            ).order_by(TestPlanFolder.sort_order).all()

            # 构建树形结构
            def build_tree(parent_id=None):
                result = []
                for folder in folders:
                    if folder.parent_id == parent_id:
                        folder_dict = folder.to_dict()
                        folder_dict['children'] = build_tree(folder.id)
                        result.append(folder_dict)
                return result

            tree = build_tree()

            return success_response(data=tree)
        except Exception as e:
            return error_response(message=f'获取目录列表失败: {str(e)}', code=500)

    @test_plan_folder_ns.expect(test_plan_folder_model)
    def post(self):
        """创建测试计划目录"""
        try:
            data = request.get_json()

            folder = TestPlanFolder(
                name=data['name'],
                project_id=data['project_id'],
                parent_id=data.get('parent_id'),
                description=data.get('description'),
                created_by=data.get('created_by')
            )

            db.session.add(folder)
            db.session.commit()

            return success_response(data=folder.to_dict(), message='创建成功', code=201)
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'创建目录失败: {str(e)}', code=500)


@test_plan_folder_ns.route('/<int:folder_id>')
class TestPlanFolderAPI(Resource):
    """测试计划目录详情API"""

    def get(self, folder_id):
        """获取目录详情"""
        try:
            folder = TestPlanFolder.query.get_or_404(folder_id)
            return success_response(data=folder.to_dict())
        except Exception as e:
            return error_response(message=f'获取目录详情失败: {str(e)}', code=500)

    @test_plan_folder_ns.expect(test_plan_folder_model)
    def put(self, folder_id):
        """更新目录"""
        try:
            folder = TestPlanFolder.query.get_or_404(folder_id)
            data = request.get_json()

            folder.name = data.get('name', folder.name)
            folder.description = data.get('description', folder.description)
            folder.parent_id = data.get('parent_id', folder.parent_id)

            db.session.commit()

            return success_response(data=folder.to_dict(), message='更新成功')
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'更新目录失败: {str(e)}', code=500)

    def delete(self, folder_id):
        """删除目录"""
        try:
            folder = TestPlanFolder.query.get_or_404(folder_id)

            # 检查是否有子目录
            if folder.children.filter_by(is_deleted=False).first():
                return error_response(message='目录下有子目录，无法删除', code=400)

            # 检查是否有测试计划
            if folder.test_plans.filter_by(is_deleted=False).first():
                return error_response(message='目录下有测试计划，无法删除', code=400)

            folder.is_deleted = True
            db.session.commit()

            return success_response(message='删除成功')
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'删除目录失败: {str(e)}', code=500)

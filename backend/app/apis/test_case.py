"""
测试用例管理API
"""
from flask import request, current_app
from flask_restx import Namespace, Resource, fields
from app import db
from app.models import TestCase, TestSuite
from app.utils import success_response, error_response
import json
from datetime import datetime

# 命名空间
test_suite_ns = Namespace('TestSuites', description='测试套件/文件夹管理')
test_case_ns = Namespace('TestCases', description='测试用例管理')

# Swagger模型定义
test_suite_model = test_suite_ns.model('TestSuite', {
    'name': fields.String(required=True, description='套件名称'),
    'description': fields.String(description='描述'),
    'parent_id': fields.Integer(description='父套件ID'),
    'project_id': fields.Integer(description='项目ID'),
    'sort_order': fields.Integer(description='排序')
})

test_case_model = test_case_ns.model('TestCase', {
    'name': fields.String(required=True, description='用例名称'),
    'case_no': fields.String(description='用例编号'),
    'suite_id': fields.Integer(description='所属套件ID'),
    'description': fields.String(description='描述'),
    'preconditions': fields.String(description='前置条件'),
    'steps': fields.String(description='测试步骤(JSON)'),
    'expected_result': fields.String(description='预期结果'),
    'priority': fields.String(description='优先级'),
    'case_type': fields.String(description='用例类型'),
    'automation_status': fields.String(description='自动化状态'),
    'status': fields.String(description='状态'),
    'tags': fields.String(description='标签'),
    'estimated_time': fields.Integer(description='预估时间(分钟)'),
    'complexity': fields.String(description='复杂度'),
    'risk_level': fields.String(description='风险等级')
})


# ============== 测试套件API ==============

@test_suite_ns.route('')
class TestSuiteListAPI(Resource):
    """测试套件列表API"""

    def get(self):
        """获取所有测试套件(树形结构)"""
        try:
            project_id = request.args.get('project_id', type=int)

            # 获取所有套件
            query = TestSuite.query
            if project_id:
                query = query.filter_by(project_id=project_id)

            suites = query.order_by(TestSuite.sort_order).all()

            # 构建树形结构
            def build_tree(parent_id=None):
                result = []
                for suite in suites:
                    if suite.parent_id == parent_id:
                        suite_dict = suite.to_dict()
                        suite_dict['children'] = build_tree(suite.id)
                        suite_dict['case_count'] = suite.test_cases.count()
                        result.append(suite_dict)
                return result

            return success_response(data=build_tree())
        except Exception as e:
            current_app.logger.error(f'获取测试套件失败: {str(e)}')
            return error_response(message=f'获取测试套件失败: {str(e)}', code=500)

    @test_suite_ns.expect(test_suite_model)
    def post(self):
        """创建测试套件"""
        try:
            data = request.get_json()

            suite = TestSuite(
                name=data.get('name'),
                description=data.get('description'),
                parent_id=data.get('parent_id'),
                project_id=data.get('project_id'),
                created_by=data.get('created_by'),
                sort_order=data.get('sort_order', 0)
            )

            db.session.add(suite)
            db.session.commit()

            return success_response(data=suite.to_dict(), message='创建成功', code=201)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'创建测试套件失败: {str(e)}')
            return error_response(message=f'创建测试套件失败: {str(e)}', code=500)


@test_suite_ns.route('/<int:suite_id>')
class TestSuiteAPI(Resource):
    """测试套件详情API"""

    def get(self, suite_id):
        """获取测试套件详情"""
        try:
            suite = TestSuite.query.get_or_404(suite_id)
            return success_response(data=suite.to_dict())
        except Exception as e:
            return error_response(message=f'获取测试套件失败: {str(e)}', code=500)

    @test_suite_ns.expect(test_suite_model)
    def put(self, suite_id):
        """更新测试套件"""
        try:
            suite = TestSuite.query.get_or_404(suite_id)
            data = request.get_json()

            suite.name = data.get('name', suite.name)
            suite.description = data.get('description', suite.description)
            suite.parent_id = data.get('parent_id', suite.parent_id)
            suite.project_id = data.get('project_id', suite.project_id)
            suite.sort_order = data.get('sort_order', suite.sort_order)

            db.session.commit()
            return success_response(data=suite.to_dict(), message='更新成功')
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'更新测试套件失败: {str(e)}', code=500)

    def delete(self, suite_id):
        """删除测试套件"""
        try:
            suite = TestSuite.query.get_or_404(suite_id)

            # 检查是否有子套件
            if suite.children.count() > 0:
                return error_response(message='该套件下有子套件，无法删除', code=400)

            # 检查是否有测试用例
            if suite.test_cases.count() > 0:
                return error_response(message='该套件下有测试用例，无法删除', code=400)

            db.session.delete(suite)
            db.session.commit()
            return success_response(message='删除成功')
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'删除测试套件失败: {str(e)}', code=500)


# ============== 测试用例API ==============

@test_case_ns.route('')
class TestCaseListAPI(Resource):
    """测试用例列表API"""

    def get(self):
        """获取测试用例列表"""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            suite_id = request.args.get('suite_id', type=int)
            project_id = request.args.get('project_id', type=int)
            status = request.args.get('status')
            priority = request.args.get('priority')
            case_type = request.args.get('case_type')
            keyword = request.args.get('keyword')

            query = TestCase.query.filter_by(is_deleted=False)

            # 按项目过滤（需要join TestSuite）
            if project_id:
                query = query.join(TestSuite).filter(TestSuite.project_id == project_id)

            # 使用明确的字段名避免歧义
            if suite_id:
                query = query.filter(TestCase.suite_id == suite_id)
            if status:
                query = query.filter(TestCase.status == status)
            if priority:
                query = query.filter(TestCase.priority == priority)
            if case_type:
                query = query.filter(TestCase.case_type == case_type)
            if keyword:
                query = query.filter(TestCase.name.contains(keyword) |
                                     TestCase.case_no.contains(keyword))

            pagination = query.order_by(TestCase.id.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )

            return success_response(data={
                'items': [item.to_dict() for item in pagination.items],
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page
            })
        except Exception as e:
            current_app.logger.error(f'获取测试用例失败: {str(e)}')
            return error_response(message=f'获取测试用例失败: {str(e)}', code=500)

    @test_case_ns.expect(test_case_model)
    def post(self):
        """创建测试用例"""
        try:
            data = request.get_json()

            # 处理空字符串，转换为None
            case_no = data.get('case_no')
            if case_no == '' or case_no is None:
                case_no = None

            test_case = TestCase(
                name=data.get('name'),
                case_no=case_no,
                suite_id=data.get('suite_id'),
                description=data.get('description'),
                preconditions=data.get('preconditions'),
                steps=json.dumps(data.get('steps')) if data.get('steps') else None,
                expected_result=data.get('expected_result'),
                priority=data.get('priority', 'medium'),
                case_type=data.get('case_type', 'functional'),
                automation_status=data.get('automation_status', 'manual'),
                status=data.get('status', 'draft'),
                tags=data.get('tags'),
                estimated_time=data.get('estimated_time'),
                complexity=data.get('complexity', 'simple'),
                risk_level=data.get('risk_level', 'low'),
                created_by=data.get('created_by')
            )

            db.session.add(test_case)
            db.session.commit()

            return success_response(data=test_case.to_dict(), message='创建成功', code=201)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'创建测试用例失败: {str(e)}')
            return error_response(message=f'创建测试用例失败: {str(e)}', code=500)


@test_case_ns.route('/<int:case_id>')
class TestCaseAPI(Resource):
    """测试用例详情API"""

    def get(self, case_id):
        """获取测试用例详情"""
        try:
            test_case = TestCase.query.filter_by(id=case_id, is_deleted=False).first_or_404()
            return success_response(data=test_case.to_dict())
        except Exception as e:
            return error_response(message=f'获取测试用例失败: {str(e)}', code=500)

    @test_case_ns.expect(test_case_model)
    def put(self, case_id):
        """更新测试用例"""
        try:
            test_case = TestCase.query.filter_by(id=case_id, is_deleted=False).first_or_404()
            data = request.get_json()

            test_case.name = data.get('name', test_case.name)
            test_case.case_no = data.get('case_no', test_case.case_no)
            test_case.suite_id = data.get('suite_id', test_case.suite_id)
            test_case.description = data.get('description', test_case.description)
            test_case.preconditions = data.get('preconditions', test_case.preconditions)

            if data.get('steps') is not None:
                test_case.steps = json.dumps(data.get('steps'))

            test_case.expected_result = data.get('expected_result', test_case.expected_result)
            test_case.priority = data.get('priority', test_case.priority)
            test_case.case_type = data.get('case_type', test_case.case_type)
            test_case.automation_status = data.get('automation_status', test_case.automation_status)
            test_case.status = data.get('status', test_case.status)
            test_case.tags = data.get('tags', test_case.tags)
            test_case.estimated_time = data.get('estimated_time', test_case.estimated_time)
            test_case.complexity = data.get('complexity', test_case.complexity)
            test_case.risk_level = data.get('risk_level', test_case.risk_level)
            test_case.updated_by = data.get('updated_by')
            test_case.version += 1

            db.session.commit()
            return success_response(data=test_case.to_dict(), message='更新成功')
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'更新测试用例失败: {str(e)}', code=500)

    def delete(self, case_id):
        """删除测试用例(软删除)"""
        try:
            test_case = TestCase.query.filter_by(id=case_id, is_deleted=False).first_or_404()
            test_case.is_deleted = True
            db.session.commit()
            return success_response(message='删除成功')
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'删除测试用例失败: {str(e)}', code=500)


@test_case_ns.route('/batch-delete')
class TestCaseBatchDeleteAPI(Resource):
    """批量删除测试用例API"""

    def post(self):
        """批量删除测试用例"""
        try:
            data = request.get_json()
            case_ids = data.get('case_ids', [])

            if not case_ids:
                return error_response(message='请选择要删除的用例', code=400)

            TestCase.query.filter(TestCase.id.in_(case_ids)).update(
                {'is_deleted': True}, synchronize_session=False
            )
            db.session.commit()

            return success_response(message=f'成功删除 {len(case_ids)} 条用例')
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'批量删除失败: {str(e)}', code=500)


@test_case_ns.route('/batch-move')
class TestCaseBatchMoveAPI(Resource):
    """批量移动测试用例API"""

    def post(self):
        """批量移动测试用例到指定套件"""
        try:
            data = request.get_json()
            case_ids = data.get('case_ids', [])
            target_suite_id = data.get('target_suite_id')

            if not case_ids:
                return error_response(message='请选择要移动的用例', code=400)

            TestCase.query.filter(TestCase.id.in_(case_ids)).update(
                {'suite_id': target_suite_id}, synchronize_session=False
            )
            db.session.commit()

            return success_response(message=f'成功移动 {len(case_ids)} 条用例')
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'批量移动失败: {str(e)}', code=500)

"""
缺陷管理API
"""
from flask import request, current_app
from flask_restx import Namespace, Resource, fields
from app import db
from app.models import Defect, DefectWorkflow, DefectComment
from app.utils import success_response, error_response
import json
from datetime import datetime, date

# 命名空间
defect_workflow_ns = Namespace('DefectWorkflows', description='缺陷工作流状态管理')
defect_ns = Namespace('Defects', description='缺陷管理')
defect_comment_ns = Namespace('DefectComments', description='缺陷评论管理')

# Swagger模型定义
defect_workflow_model = defect_workflow_ns.model('DefectWorkflow', {
    'project_id': fields.Integer(description='项目ID'),
    'name': fields.String(required=True, description='状态名称'),
    'code': fields.String(required=True, description='状态代码'),
    'description': fields.String(description='描述'),
    'color': fields.String(description='显示颜色'),
    'sort_order': fields.Integer(description='排序'),
    'is_default': fields.Boolean(description='是否默认'),
    'is_closed': fields.Boolean(description='是否关闭状态'),
    'transitions': fields.String(description='可转换状态(JSON)')
})

defect_model = defect_ns.model('Defect', {
    'title': fields.String(required=True, description='缺陷标题'),
    'description': fields.String(description='描述'),
    'project_id': fields.Integer(description='项目ID'),
    'test_case_id': fields.Integer(description='关联测试用例ID'),
    'test_execution_id': fields.Integer(description='关联执行记录ID'),
    'test_plan_id': fields.Integer(description='关联测试计划ID'),
    'severity': fields.String(description='严重程度'),
    'priority': fields.String(description='优先级'),
    'status': fields.String(description='状态'),
    'defect_type': fields.String(description='缺陷类型'),
    'category': fields.String(description='分类'),
    'reproduction_steps': fields.String(description='复现步骤'),
    'expected_behavior': fields.String(description='期望行为'),
    'actual_behavior': fields.String(description='实际行为'),
    'environment': fields.String(description='环境'),
    'browser': fields.String(description='浏览器'),
    'os': fields.String(description='操作系统'),
    'assigned_to': fields.String(description='分配给'),
    'due_date': fields.String(description='期望解决日期'),
    'tags': fields.String(description='标签')
})

defect_comment_model = defect_comment_ns.model('DefectComment', {
    'defect_id': fields.Integer(required=True, description='缺陷ID'),
    'content': fields.String(required=True, description='评论内容'),
    'is_internal': fields.Boolean(description='是否内部评论'),
    'attachments': fields.String(description='附件(JSON)')
})


# ============== 缺陷工作流API ==============

@defect_workflow_ns.route('')
class DefectWorkflowListAPI(Resource):
    """缺陷工作流列表API"""

    def get(self):
        """获取缺陷工作流状态列表"""
        try:
            project_id = request.args.get('project_id', type=int)

            query = DefectWorkflow.query
            if project_id:
                query = query.filter_by(project_id=project_id)

            workflows = query.order_by(DefectWorkflow.sort_order).all()

            return success_response(data=[w.to_dict() for w in workflows])
        except Exception as e:
            current_app.logger.error(f'获取缺陷工作流失败: {str(e)}')
            return error_response(message=f'获取缺陷工作流失败: {str(e)}', code=500)

    @defect_workflow_ns.expect(defect_workflow_model)
    def post(self):
        """创建缺陷工作流状态"""
        try:
            data = request.get_json()

            workflow = DefectWorkflow(
                project_id=data.get('project_id'),
                name=data.get('name'),
                code=data.get('code'),
                description=data.get('description'),
                color=data.get('color', '#666666'),
                sort_order=data.get('sort_order', 0),
                is_default=data.get('is_default', False),
                is_closed=data.get('is_closed', False),
                transitions=json.dumps(data.get('transitions')) if data.get('transitions') else None
            )

            db.session.add(workflow)
            db.session.commit()

            return success_response(data=workflow.to_dict(), message='创建成功', code=201)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'创建缺陷工作流失败: {str(e)}')
            return error_response(message=f'创建缺陷工作流失败: {str(e)}', code=500)


@defect_workflow_ns.route('/<int:workflow_id>')
class DefectWorkflowAPI(Resource):
    """缺陷工作流详情API"""

    def get(self, workflow_id):
        """获取缺陷工作流详情"""
        try:
            workflow = DefectWorkflow.query.get_or_404(workflow_id)
            return success_response(data=workflow.to_dict())
        except Exception as e:
            return error_response(message=f'获取缺陷工作流失败: {str(e)}', code=500)

    @defect_workflow_ns.expect(defect_workflow_model)
    def put(self, workflow_id):
        """更新缺陷工作流"""
        try:
            workflow = DefectWorkflow.query.get_or_404(workflow_id)
            data = request.get_json()

            workflow.name = data.get('name', workflow.name)
            workflow.code = data.get('code', workflow.code)
            workflow.description = data.get('description', workflow.description)
            workflow.color = data.get('color', workflow.color)
            workflow.sort_order = data.get('sort_order', workflow.sort_order)
            workflow.is_default = data.get('is_default', workflow.is_default)
            workflow.is_closed = data.get('is_closed', workflow.is_closed)

            if data.get('transitions') is not None:
                workflow.transitions = json.dumps(data.get('transitions'))

            db.session.commit()
            return success_response(data=workflow.to_dict(), message='更新成功')
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'更新缺陷工作流失败: {str(e)}', code=500)

    def delete(self, workflow_id):
        """删除缺陷工作流"""
        try:
            workflow = DefectWorkflow.query.get_or_404(workflow_id)

            # 检查是否有缺陷使用此状态
            if workflow.defects.count() > 0:
                return error_response(message='该状态正在被使用，无法删除', code=400)

            db.session.delete(workflow)
            db.session.commit()
            return success_response(message='删除成功')
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'删除缺陷工作流失败: {str(e)}', code=500)


# ============== 缺陷API ==============

@defect_ns.route('')
class DefectListAPI(Resource):
    """缺陷列表API"""

    def get(self):
        """获取缺陷列表"""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            project_id = request.args.get('project_id', type=int)
            status = request.args.get('status')
            severity = request.args.get('severity')
            priority = request.args.get('priority')
            assigned_to = request.args.get('assigned_to')
            keyword = request.args.get('keyword')

            query = Defect.query

            if project_id:
                query = query.filter_by(project_id=project_id)
            if status:
                query = query.filter_by(status=status)
            if severity:
                query = query.filter_by(severity=severity)
            if priority:
                query = query.filter_by(priority=priority)
            if assigned_to:
                query = query.filter_by(assigned_to=assigned_to)
            if keyword:
                query = query.filter(Defect.title.contains(keyword) |
                                     Defect.defect_no.contains(keyword))

            pagination = query.order_by(Defect.id.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )

            return success_response(data={
                'items': [item.to_dict() for item in pagination.items],
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page
            })
        except Exception as e:
            current_app.logger.error(f'获取缺陷列表失败: {str(e)}')
            return error_response(message=f'获取缺陷列表失败: {str(e)}', code=500)

    @defect_ns.expect(defect_model)
    def post(self):
        """创建缺陷"""
        try:
            data = request.get_json()

            # 处理日期
            due_date = None
            if data.get('due_date'):
                due_date = datetime.strptime(data.get('due_date'), '%Y-%m-%d').date()

            defect = Defect(
                title=data.get('title'),
                description=data.get('description'),
                project_id=data.get('project_id'),
                test_case_id=data.get('test_case_id'),
                test_execution_id=data.get('test_execution_id'),
                test_plan_id=data.get('test_plan_id'),
                severity=data.get('severity', 'medium'),
                priority=data.get('priority', 'medium'),
                status=data.get('status', 'new'),
                defect_type=data.get('defect_type', 'bug'),
                category=data.get('category'),
                reproduction_steps=data.get('reproduction_steps'),
                expected_behavior=data.get('expected_behavior'),
                actual_behavior=data.get('actual_behavior'),
                environment=data.get('environment'),
                browser=data.get('browser'),
                os=data.get('os'),
                assigned_to=data.get('assigned_to'),
                reported_by=data.get('reported_by'),
                due_date=due_date,
                tags=data.get('tags'),
                screenshots=json.dumps(data.get('screenshots')) if data.get('screenshots') else None
            )

            db.session.add(defect)
            db.session.commit()

            return success_response(data=defect.to_dict(), message='创建成功', code=201)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'创建缺陷失败: {str(e)}')
            return error_response(message=f'创建缺陷失败: {str(e)}', code=500)


@defect_ns.route('/<int:defect_id>')
class DefectAPI(Resource):
    """缺陷详情API"""

    def get(self, defect_id):
        """获取缺陷详情"""
        try:
            defect = Defect.query.get_or_404(defect_id)

            # 增加查看次数
            defect.view_count += 1
            db.session.commit()

            defect_dict = defect.to_dict()
            # 获取评论
            comments = DefectComment.query.filter_by(defect_id=defect_id).order_by(
                DefectComment.created_at.desc()
            ).all()
            defect_dict['comments'] = [c.to_dict() for c in comments]

            return success_response(data=defect_dict)
        except Exception as e:
            return error_response(message=f'获取缺陷详情失败: {str(e)}', code=500)

    @defect_ns.expect(defect_model)
    def put(self, defect_id):
        """更新缺陷"""
        try:
            defect = Defect.query.get_or_404(defect_id)
            data = request.get_json()

            defect.title = data.get('title', defect.title)
            defect.description = data.get('description', defect.description)
            defect.project_id = data.get('project_id', defect.project_id)
            defect.test_case_id = data.get('test_case_id', defect.test_case_id)
            defect.test_execution_id = data.get('test_execution_id', defect.test_execution_id)
            defect.test_plan_id = data.get('test_plan_id', defect.test_plan_id)
            defect.severity = data.get('severity', defect.severity)
            defect.priority = data.get('priority', defect.priority)

            # 状态变更处理
            new_status = data.get('status')
            if new_status and new_status != defect.status:
                defect.status = new_status
                # 根据状态更新时间
                if new_status in ['resolved', 'closed']:
                    defect.resolved_date = datetime.utcnow()
                if new_status == 'assigned':
                    defect.assigned_date = datetime.utcnow()
                if new_status == 'in_progress':
                    defect.start_date = datetime.utcnow()
                if new_status == 'closed':
                    defect.closed_date = datetime.utcnow()
                if new_status == 'verified':
                    defect.verified_date = datetime.utcnow()

            defect.defect_type = data.get('defect_type', defect.defect_type)
            defect.category = data.get('category', defect.category)
            defect.reproduction_steps = data.get('reproduction_steps', defect.reproduction_steps)
            defect.expected_behavior = data.get('expected_behavior', defect.expected_behavior)
            defect.actual_behavior = data.get('actual_behavior', defect.actual_behavior)
            defect.environment = data.get('environment', defect.environment)
            defect.browser = data.get('browser', defect.browser)
            defect.os = data.get('os', defect.os)
            defect.assigned_to = data.get('assigned_to', defect.assigned_to)

            if data.get('due_date'):
                defect.due_date = datetime.strptime(data.get('due_date'), '%Y-%m-%d').date()

            defect.resolution = data.get('resolution', defect.resolution)
            defect.resolution_version = data.get('resolution_version', defect.resolution_version)
            defect.tags = data.get('tags', defect.tags)

            if data.get('screenshots') is not None:
                defect.screenshots = json.dumps(data.get('screenshots'))

            db.session.commit()
            return success_response(data=defect.to_dict(), message='更新成功')
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'更新缺陷失败: {str(e)}', code=500)

    def delete(self, defect_id):
        """删除缺陷"""
        try:
            defect = Defect.query.get_or_404(defect_id)
            db.session.delete(defect)
            db.session.commit()
            return success_response(message='删除成功')
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'删除缺陷失败: {str(e)}', code=500)


@defect_ns.route('/<int:defect_id>/assign')
class DefectAssignAPI(Resource):
    """分配缺陷API"""

    def post(self, defect_id):
        """分配缺陷"""
        try:
            data = request.get_json()
            defect = Defect.query.get_or_404(defect_id)

            defect.assigned_to = data.get('assigned_to')
            defect.assigned_date = datetime.utcnow()
            if defect.status == 'new':
                defect.status = 'assigned'

            db.session.commit()
            return success_response(data=defect.to_dict(), message='分配成功')
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'分配缺陷失败: {str(e)}', code=500)


# ============== 缺陷评论API ==============

@defect_comment_ns.route('')
class DefectCommentListAPI(Resource):
    """缺陷评论列表API"""

    def get(self):
        """获取缺陷评论列表"""
        try:
            defect_id = request.args.get('defect_id', type=int)

            if not defect_id:
                return error_response(message='请提供缺陷ID', code=400)

            comments = DefectComment.query.filter_by(defect_id=defect_id).order_by(
                DefectComment.created_at.desc()
            ).all()

            return success_response(data=[c.to_dict() for c in comments])
        except Exception as e:
            current_app.logger.error(f'获取缺陷评论失败: {str(e)}')
            return error_response(message=f'获取缺陷评论失败: {str(e)}', code=500)

    @defect_comment_ns.expect(defect_comment_model)
    def post(self):
        """创建缺陷评论"""
        try:
            data = request.get_json()

            comment = DefectComment(
                defect_id=data.get('defect_id'),
                content=data.get('content'),
                commented_by=data.get('commented_by'),
                is_internal=data.get('is_internal', False),
                attachments=json.dumps(data.get('attachments')) if data.get('attachments') else None
            )

            db.session.add(comment)

            # 更新缺陷评论数
            defect = Defect.query.get(data.get('defect_id'))
            if defect:
                defect.comment_count += 1

            db.session.commit()

            return success_response(data=comment.to_dict(), message='创建成功', code=201)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'创建缺陷评论失败: {str(e)}')
            return error_response(message=f'创建缺陷评论失败: {str(e)}', code=500)


@defect_comment_ns.route('/<int:comment_id>')
class DefectCommentAPI(Resource):
    """缺陷评论详情API"""

    def put(self, comment_id):
        """更新缺陷评论"""
        try:
            comment = DefectComment.query.get_or_404(comment_id)
            data = request.get_json()

            comment.content = data.get('content', comment.content)

            if data.get('attachments') is not None:
                comment.attachments = json.dumps(data.get('attachments'))

            db.session.commit()
            return success_response(data=comment.to_dict(), message='更新成功')
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'更新缺陷评论失败: {str(e)}', code=500)

    def delete(self, comment_id):
        """删除缺陷评论"""
        try:
            comment = DefectComment.query.get_or_404(comment_id)

            # 更新缺陷评论数
            defect = Defect.query.get(comment.defect_id)
            if defect and defect.comment_count > 0:
                defect.comment_count -= 1

            db.session.delete(comment)
            db.session.commit()
            return success_response(message='删除成功')
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'删除缺陷评论失败: {str(e)}', code=500)

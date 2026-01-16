"""
测试报告管理API
"""
from flask import request, current_app
from flask_restx import Namespace, Resource, fields
from app import db
from app.models import TestReport, ReportMetric, TestExecution, Defect
from app.utils import success_response, error_response
import json
from datetime import datetime, date
from sqlalchemy import func

# 命名空间
test_report_ns = Namespace('TestReports', description='测试报告管理')
report_metric_ns = Namespace('ReportMetrics', description='报告度量指标管理')

# Swagger模型定义
test_report_model = test_report_ns.model('TestReport', {
    'name': fields.String(required=True, description='报告名称'),
    'report_type': fields.String(description='报告类型'),
    'test_plan_id': fields.Integer(description='测试计划ID'),
    'project_id': fields.Integer(description='项目ID'),
    'start_time': fields.String(description='开始时间'),
    'end_time': fields.String(description='结束时间'),
    'environment': fields.String(description='环境'),
    'build_version': fields.String(description='版本')
})

report_metric_model = report_metric_ns.model('ReportMetric', {
    'report_id': fields.Integer(required=True, description='报告ID'),
    'metric_name': fields.String(required=True, description='指标名称'),
    'metric_key': fields.String(required=True, description='指标键值'),
    'metric_value': fields.String(description='指标值'),
    'metric_type': fields.String(description='指标类型'),
    'display_order': fields.Integer(description='显示顺序'),
    'category': fields.String(description='分类'),
    'description': fields.String(description='描述'),
    'trend_data': fields.String(description='趋势数据(JSON)')
})


# ============== 测试报告API ==============

@test_report_ns.route('')
class TestReportListAPI(Resource):
    """测试报告列表API"""

    def get(self):
        """获取测试报告列表"""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            project_id = request.args.get('project_id', type=int)
            test_plan_id = request.args.get('test_plan_id', type=int)
            report_type = request.args.get('report_type')
            keyword = request.args.get('keyword')

            query = TestReport.query

            if project_id:
                query = query.filter_by(project_id=project_id)
            if test_plan_id:
                query = query.filter_by(test_plan_id=test_plan_id)
            if report_type:
                query = query.filter_by(report_type=report_type)
            if keyword:
                query = query.filter(TestReport.name.contains(keyword) |
                                     TestReport.report_no.contains(keyword))

            # 排除模板
            query = query.filter_by(is_template=False)

            pagination = query.order_by(TestReport.id.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )

            return success_response(data={
                'items': [item.to_dict() for item in pagination.items],
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page
            })
        except Exception as e:
            current_app.logger.error(f'获取测试报告失败: {str(e)}')
            return error_response(message=f'获取测试报告失败: {str(e)}', code=500)

    @test_report_ns.expect(test_report_model)
    def post(self):
        """创建测试报告"""
        try:
            data = request.get_json()

            # 处理时间
            start_time = None
            end_time = None
            if data.get('start_time'):
                start_time = datetime.fromisoformat(data.get('start_time').replace('Z', '+00:00'))
            if data.get('end_time'):
                end_time = datetime.fromisoformat(data.get('end_time').replace('Z', '+00:00'))

            report = TestReport(
                name=data.get('name'),
                report_type=data.get('report_type', 'execution'),
                test_plan_id=data.get('test_plan_id'),
                project_id=data.get('project_id'),
                summary=json.dumps(data.get('summary')) if data.get('summary') else None,
                start_time=start_time,
                end_time=end_time,
                environment=data.get('environment'),
                build_version=data.get('build_version'),
                generated_by=data.get('generated_by'),
                status='generating'
            )

            db.session.add(report)
            db.session.flush()  # 获取report ID

            # 生成统计数据
            if data.get('auto_generate', True):
                report = generate_report_statistics(report, data)

            db.session.commit()

            return success_response(data=report.to_dict(), message='创建成功', code=201)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'创建测试报告失败: {str(e)}')
            return error_response(message=f'创建测试报告失败: {str(e)}', code=500)


def generate_report_statistics(report, data):
    """生成报告统计数据"""
    try:
        # 基于测试计划生成统计
        if report.test_plan_id:
            from app.models import TestPlanCase

            # 获取测试计划的所有用例
            plan_cases = TestPlanCase.query.filter_by(test_plan_id=report.test_plan_id).all()

            report.total_cases = len(plan_cases)
            report.passed_cases = sum(1 for pc in plan_cases if pc.last_status == 'passed')
            report.failed_cases = sum(1 for pc in plan_cases if pc.last_status == 'failed')
            report.blocked_cases = sum(1 for pc in plan_cases if pc.last_status == 'blocked')
            report.skipped_cases = sum(1 for pc in plan_cases if pc.last_status == 'skipped')

            # 计算通过率和执行率
            report.calculate_statistics()

            # 获取缺陷统计
            defect_query = Defect.query.filter_by(test_plan_id=report.test_plan_id)
            defects = defect_query.all()
            report.total_defects = len(defects)
            report.critical_defects = sum(1 for d in defects if d.severity == 'critical')
            report.high_defects = sum(1 for d in defects if d.severity == 'high')
            report.medium_defects = sum(1 for d in defects if d.severity == 'medium')
            report.low_defects = sum(1 for d in defects if d.severity == 'low')

        # 计算执行时长
        if report.start_time and report.end_time:
            report.duration = int((report.end_time - report.start_time).total_seconds())

        report.status = 'completed'

        return report
    except Exception as e:
        current_app.logger.error(f'生成报告统计失败: {str(e)}')
        report.status = 'failed'
        return report


@test_report_ns.route('/<int:report_id>')
class TestReportAPI(Resource):
    """测试报告详情API"""

    def get(self, report_id):
        """获取测试报告详情"""
        try:
            report = TestReport.query.get_or_404(report_id)

            report_dict = report.to_dict()

            # 获取度量指标
            metrics = ReportMetric.query.filter_by(report_id=report_id).order_by(
                ReportMetric.display_order
            ).all()
            report_dict['metrics'] = [m.to_dict() for m in metrics]

            return success_response(data=report_dict)
        except Exception as e:
            return error_response(message=f'获取测试报告失败: {str(e)}', code=500)

    @test_report_ns.expect(test_report_model)
    def put(self, report_id):
        """更新测试报告"""
        try:
            report = TestReport.query.get_or_404(report_id)
            data = request.get_json()

            report.name = data.get('name', report.name)
            report.report_type = data.get('report_type', report.report_type)
            report.environment = data.get('environment', report.environment)
            report.build_version = data.get('build_version', report.build_version)

            if data.get('summary') is not None:
                report.summary = json.dumps(data.get('summary'))

            if data.get('chart_config') is not None:
                report.chart_config = json.dumps(data.get('chart_config'))

            db.session.commit()
            return success_response(data=report.to_dict(), message='更新成功')
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'更新测试报告失败: {str(e)}', code=500)

    def delete(self, report_id):
        """删除测试报告"""
        try:
            report = TestReport.query.get_or_404(report_id)
            db.session.delete(report)
            db.session.commit()
            return success_response(message='删除成功')
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'删除测试报告失败: {str(e)}', code=500)


@test_report_ns.route('/<int:report_id>/export')
class TestReportExportAPI(Resource):
    """导出测试报告API"""

    def post(self, report_id):
        """导出测试报告"""
        try:
            data = request.get_json()
            report = TestReport.query.get_or_404(report_id)
            format_type = data.get('format', 'html')

            # TODO: 实现报告导出功能
            # 这里预留导出功能接口

            return success_response(
                data={'export_url': f'/exports/reports/{report_id}.{format_type}'},
                message=f'报告导出为 {format_type.upper()} 格式的任务已提交'
            )
        except Exception as e:
            return error_response(message=f'导出报告失败: {str(e)}', code=500)


@test_report_ns.route('/templates')
class TestReportTemplateListAPI(Resource):
    """报告模板列表API"""

    def get(self):
        """获取报告模板列表"""
        try:
            project_id = request.args.get('project_id', type=int)

            query = TestReport.query.filter_by(is_template=True)
            if project_id:
                query = query.filter_by(project_id=project_id)

            templates = query.order_by(TestReport.id).all()

            return success_response(data=[t.to_dict() for t in templates])
        except Exception as e:
            current_app.logger.error(f'获取报告模板失败: {str(e)}')
            return error_response(message=f'获取报告模板失败: {str(e)}', code=500)

    @test_report_ns.expect(test_report_model)
    def post(self):
        """创建报告模板"""
        try:
            data = request.get_json()

            template = TestReport(
                name=data.get('name'),
                report_type=data.get('report_type', 'execution'),
                project_id=data.get('project_id'),
                chart_config=json.dumps(data.get('chart_config')) if data.get('chart_config') else None,
                is_template=True,
                generated_by=data.get('generated_by')
            )

            db.session.add(template)
            db.session.commit()

            return success_response(data=template.to_dict(), message='创建成功', code=201)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'创建报告模板失败: {str(e)}')
            return error_response(message=f'创建报告模板失败: {str(e)}', code=500)


# ============== 报告度量指标API ==============

@report_metric_ns.route('')
class ReportMetricListAPI(Resource):
    """报告度量指标列表API"""

    def get(self):
        """获取报告度量指标列表"""
        try:
            report_id = request.args.get('report_id', type=int)

            if not report_id:
                return error_response(message='请提供报告ID', code=400)

            metrics = ReportMetric.query.filter_by(report_id=report_id).order_by(
                ReportMetric.display_order
            ).all()

            return success_response(data=[m.to_dict() for m in metrics])
        except Exception as e:
            current_app.logger.error(f'获取报告度量指标失败: {str(e)}')
            return error_response(message=f'获取报告度量指标失败: {str(e)}', code=500)

    @report_metric_ns.expect(report_metric_model)
    def post(self):
        """创建报告度量指标"""
        try:
            data = request.get_json()

            metric = ReportMetric(
                report_id=data.get('report_id'),
                metric_name=data.get('metric_name'),
                metric_key=data.get('metric_key'),
                metric_value=data.get('metric_value'),
                metric_type=data.get('metric_type', 'string'),
                display_order=data.get('display_order', 0),
                category=data.get('category'),
                description=data.get('description'),
                trend_data=json.dumps(data.get('trend_data')) if data.get('trend_data') else None
            )

            db.session.add(metric)
            db.session.commit()

            return success_response(data=metric.to_dict(), message='创建成功', code=201)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'创建报告度量指标失败: {str(e)}')
            return error_response(message=f'创建报告度量指标失败: {str(e)}', code=500)


@report_metric_ns.route('/<int:metric_id>')
class ReportMetricAPI(Resource):
    """报告度量指标详情API"""

    def get(self, metric_id):
        """获取报告度量指标详情"""
        try:
            metric = ReportMetric.query.get_or_404(metric_id)
            return success_response(data=metric.to_dict())
        except Exception as e:
            return error_response(message=f'获取报告度量指标失败: {str(e)}', code=500)

    @report_metric_ns.expect(report_metric_model)
    def put(self, metric_id):
        """更新报告度量指标"""
        try:
            metric = ReportMetric.query.get_or_404(metric_id)
            data = request.get_json()

            metric.metric_name = data.get('metric_name', metric.metric_name)
            metric.metric_key = data.get('metric_key', metric.metric_key)
            metric.metric_value = data.get('metric_value', metric.metric_value)
            metric.metric_type = data.get('metric_type', metric.metric_type)
            metric.display_order = data.get('display_order', metric.display_order)
            metric.category = data.get('category', metric.category)
            metric.description = data.get('description', metric.description)

            if data.get('trend_data') is not None:
                metric.trend_data = json.dumps(data.get('trend_data'))

            db.session.commit()
            return success_response(data=metric.to_dict(), message='更新成功')
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'更新报告度量指标失败: {str(e)}', code=500)

    def delete(self, metric_id):
        """删除报告度量指标"""
        try:
            metric = ReportMetric.query.get_or_404(metric_id)
            db.session.delete(metric)
            db.session.commit()
            return success_response(message='删除成功')
        except Exception as e:
            db.session.rollback()
            return error_response(message=f'删除报告度量指标失败: {str(e)}', code=500)


@report_metric_ns.route('/batch')
class ReportMetricBatchAPI(Resource):
    """批量创建报告度量指标API"""

    def post(self):
        """批量创建报告度量指标"""
        try:
            data = request.get_json()
            metrics_data = data.get('metrics', [])

            if not metrics_data:
                return error_response(message='请提供度量指标数据', code=400)

            created_metrics = []
            for metric_data in metrics_data:
                metric = ReportMetric(
                    report_id=metric_data.get('report_id'),
                    metric_name=metric_data.get('metric_name'),
                    metric_key=metric_data.get('metric_key'),
                    metric_value=metric_data.get('metric_value'),
                    metric_type=metric_data.get('metric_type', 'string'),
                    display_order=metric_data.get('display_order', 0),
                    category=metric_data.get('category'),
                    description=metric_data.get('description'),
                    trend_data=json.dumps(metric_data.get('trend_data')) if metric_data.get('trend_data') else None
                )
                db.session.add(metric)
                created_metrics.append(metric)

            db.session.commit()

            return success_response(
                data=[m.to_dict() for m in created_metrics],
                message=f'成功创建 {len(created_metrics)} 条度量指标',
                code=201
            )
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'批量创建报告度量指标失败: {str(e)}')
            return error_response(message=f'批量创建报告度量指标失败: {str(e)}', code=500)

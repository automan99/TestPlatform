"""
测试报告模型
"""
from datetime import datetime
from app import db


class TestReport(db.Model):
    """测试报告模型"""
    __tablename__ = 'test_reports'

    id = db.Column(db.Integer, primary_key=True, comment='主键ID')
    name = db.Column(db.String(200), nullable=False, comment='报告名称')
    report_no = db.Column(db.String(50), unique=True, comment='报告编号')
    report_type = db.Column(db.String(50), default='execution', comment='报告类型: execution, summary, trend, coverage')

    # 关联信息
    test_plan_id = db.Column(db.Integer, db.ForeignKey('test_plans.id'), nullable=True, comment='测试计划ID')
    project_id = db.Column(db.Integer, nullable=True, index=True, comment='所属项目ID')
    execution_id = db.Column(db.Integer, db.ForeignKey('test_executions.id'), nullable=True, comment='测试执行ID')

    # 报告数据
    summary = db.Column(db.Text, comment='报告摘要(JSON格式)')
    start_time = db.Column(db.DateTime, comment='开始时间')
    end_time = db.Column(db.DateTime, comment='结束时间')
    duration = db.Column(db.Integer, comment='执行时长(秒)')

    # 统计数据
    total_cases = db.Column(db.Integer, default=0, comment='总用例数')
    passed_cases = db.Column(db.Integer, default=0, comment='通过用例数')
    failed_cases = db.Column(db.Integer, default=0, comment='失败用例数')
    blocked_cases = db.Column(db.Integer, default=0, comment='阻塞用例数')
    skipped_cases = db.Column(db.Integer, default=0, comment='跳过用例数')
    pass_rate = db.Column(db.Float, default=0.0, comment='通过率')
    execution_rate = db.Column(db.Float, default=0.0, comment='执行率')

    # 缺陷统计
    total_defects = db.Column(db.Integer, default=0, comment='总缺陷数')
    critical_defects = db.Column(db.Integer, default=0, comment='严重缺陷数')
    high_defects = db.Column(db.Integer, default=0, comment='高危缺陷数')
    medium_defects = db.Column(db.Integer, default=0, comment='中危缺陷数')
    low_defects = db.Column(db.Integer, default=0, comment='低危缺陷数')

    # 环境信息
    environment = db.Column(db.String(100), comment='测试环境')
    build_version = db.Column(db.String(100), comment='构建版本')

    # 报告配置
    chart_config = db.Column(db.Text, comment='图表配置(JSON格式)')
    template_id = db.Column(db.Integer, comment='报告模板ID')
    is_template = db.Column(db.Boolean, default=False, comment='是否为模板')

    # 状态
    status = db.Column(db.String(20), default='completed', comment='状态: generating, completed, failed')
    generated_by = db.Column(db.String(100), comment='生成人')

    # 导出
    export_formats = db.Column(db.Text, comment='导出格式(JSON数组)')
    export_path = db.Column(db.String(500), comment='导出文件路径')

    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

    # 关系
    metrics = db.relationship('ReportMetric', backref='report', lazy='dynamic',
                              cascade='all, delete-orphan')

    def calculate_statistics(self):
        """计算统计数据"""
        if self.total_cases > 0:
            self.pass_rate = (self.passed_cases / self.total_cases) * 100
            executed = self.passed_cases + self.failed_cases + self.blocked_cases + self.skipped_cases
            self.execution_rate = (executed / self.total_cases) * 100 if self.total_cases > 0 else 0

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'report_no': self.report_no,
            'report_type': self.report_type,
            'test_plan_id': self.test_plan_id,
            'project_id': self.project_id,
            'execution_id': self.execution_id,
            'summary': self.summary,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration': self.duration,
            'total_cases': self.total_cases,
            'passed_cases': self.passed_cases,
            'failed_cases': self.failed_cases,
            'blocked_cases': self.blocked_cases,
            'skipped_cases': self.skipped_cases,
            'pass_rate': self.pass_rate,
            'execution_rate': self.execution_rate,
            'total_defects': self.total_defects,
            'critical_defects': self.critical_defects,
            'high_defects': self.high_defects,
            'medium_defects': self.medium_defects,
            'low_defects': self.low_defects,
            'environment': self.environment,
            'build_version': self.build_version,
            'chart_config': self.chart_config,
            'template_id': self.template_id,
            'is_template': self.is_template,
            'status': self.status,
            'generated_by': self.generated_by,
            'export_formats': self.export_formats,
            'export_path': self.export_path,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ReportMetric(db.Model):
    """报告度量指标模型"""
    __tablename__ = 'report_metrics'

    id = db.Column(db.Integer, primary_key=True, comment='主键ID')
    report_id = db.Column(db.Integer, db.ForeignKey('test_reports.id'), nullable=False, comment='报告ID')
    metric_name = db.Column(db.String(100), nullable=False, comment='指标名称')
    metric_key = db.Column(db.String(100), nullable=False, comment='指标键值')
    metric_value = db.Column(db.String(500), comment='指标值')
    metric_type = db.Column(db.String(50), default='string', comment='指标类型: string, number, percentage, chart')
    display_order = db.Column(db.Integer, default=0, comment='显示顺序')
    category = db.Column(db.String(100), comment='分类')
    description = db.Column(db.Text, comment='描述')
    trend_data = db.Column(db.Text, comment='趋势数据(JSON数组)')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'report_id': self.report_id,
            'metric_name': self.metric_name,
            'metric_key': self.metric_key,
            'metric_value': self.metric_value,
            'metric_type': self.metric_type,
            'display_order': self.display_order,
            'category': self.category,
            'description': self.description,
            'trend_data': self.trend_data,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

"""
缺陷管理模型
"""
from datetime import datetime
from app import db
import json


class DefectWorkflow(db.Model):
    """缺陷工作流状态模型 - 定义自定义状态流程"""
    __tablename__ = 'defect_workflows'

    id = db.Column(db.Integer, primary_key=True, comment='主键ID')
    project_id = db.Column(db.Integer, nullable=True, index=True, comment='所属项目ID')
    name = db.Column(db.String(100), nullable=False, comment='状态名称')
    code = db.Column(db.String(50), nullable=False, comment='状态代码')
    description = db.Column(db.Text, comment='描述')
    color = db.Column(db.String(20), default='#666666', comment='状态显示颜色')
    sort_order = db.Column(db.Integer, default=0, comment='排序号')
    is_default = db.Column(db.Boolean, default=False, comment='是否为默认状态')
    is_closed = db.Column(db.Boolean, default=False, comment='是否为关闭状态')
    transitions = db.Column(db.Text, comment='可转换到的状态(JSON数组)')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

    __table_args__ = (db.UniqueConstraint('project_id', 'code', name='unique_project_code'),)

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'color': self.color,
            'sort_order': self.sort_order,
            'is_default': self.is_default,
            'is_closed': self.is_closed,
            'transitions': self.transitions,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Defect(db.Model):
    """缺陷模型"""
    __tablename__ = 'defects'

    id = db.Column(db.Integer, primary_key=True, comment='主键ID')
    defect_no = db.Column(db.String(50), unique=True, comment='缺陷编号')
    title = db.Column(db.String(500), nullable=False, comment='缺陷标题')
    description = db.Column(db.Text, comment='缺陷描述')
    project_id = db.Column(db.Integer, nullable=True, index=True, comment='所属项目ID')

    # 关联信息
    test_case_id = db.Column(db.Integer, db.ForeignKey('test_cases.id'), nullable=True, comment='关联测试用例ID')
    test_execution_id = db.Column(db.Integer, db.ForeignKey('test_executions.id'), nullable=True, comment='关联测试执行ID')
    test_plan_id = db.Column(db.Integer, db.ForeignKey('test_plans.id'), nullable=True, comment='关联测试计划ID')
    module_id = db.Column(db.Integer, db.ForeignKey('defect_modules.id'), nullable=True, index=True, comment='所属模块ID')

    # 缺陷属性
    severity = db.Column(db.String(20), default='medium', comment='严重程度: critical, high, medium, low, trivial')
    priority = db.Column(db.String(20), default='medium', comment='优先级: urgent, high, medium, low')
    status_id = db.Column(db.Integer, db.ForeignKey('defect_workflows.id'), nullable=True, comment='状态ID')
    status = db.Column(db.String(50), default='new', comment='状态冗余字段，便于查询')

    # 分类
    defect_type = db.Column(db.String(50), default='bug', comment='缺陷类型: bug, feature, improvement, task')
    category = db.Column(db.String(100), comment='缺陷分类')
    reproduction_steps = db.Column(db.Text, comment='复现步骤')
    expected_behavior = db.Column(db.Text, comment='期望行为')
    actual_behavior = db.Column(db.Text, comment='实际行为')

    # 环境信息
    environment = db.Column(db.String(100), comment='测试环境')
    browser = db.Column(db.String(100), comment='浏览器')
    os = db.Column(db.String(100), comment='操作系统')

    # 分配与处理
    assigned_to = db.Column(db.String(100), comment='分配给')
    reported_by = db.Column(db.String(100), comment='报告人')
    fixed_by = db.Column(db.String(100), comment='修复人')
    verified_by = db.Column(db.String(100), comment='验证人')

    # 时间信息
    reported_date = db.Column(db.DateTime, default=datetime.utcnow, comment='报告日期')
    assigned_date = db.Column(db.DateTime, comment='分配日期')
    start_date = db.Column(db.DateTime, comment='开始处理日期')
    due_date = db.Column(db.Date, comment='期望解决日期')
    resolved_date = db.Column(db.DateTime, comment='解决日期')
    closed_date = db.Column(db.DateTime, comment='关闭日期')
    verified_date = db.Column(db.DateTime, comment='验证日期')

    # 解决信息
    resolution = db.Column(db.Text, comment='解决方案')
    resolution_version = db.Column(db.String(100), comment='解决版本')

    # 附件与标签
    attachments = db.Column(db.Text, comment='附件路径(JSON数组)')
    tags = db.Column(db.String(500), comment='标签')
    screenshots = db.Column(db.Text, comment='截图路径(JSON数组)')

    # 统计
    view_count = db.Column(db.Integer, default=0, comment='查看次数')
    comment_count = db.Column(db.Integer, default=0, comment='评论数')

    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

    # 关系
    status_obj = db.relationship('DefectWorkflow', backref='defects')
    comments = db.relationship('DefectComment', backref='defect', lazy='dynamic',
                               cascade='all, delete-orphan')
    test_case = db.relationship('TestCase', backref='defects')
    test_execution = db.relationship('TestExecution', backref='defects')
    test_plan = db.relationship('TestPlan', backref='defects')

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'defect_no': self.defect_no,
            'title': self.title,
            'description': self.description,
            'project_id': self.project_id,
            'test_case_id': self.test_case_id,
            'test_execution_id': self.test_execution_id,
            'test_plan_id': self.test_plan_id,
            'module_id': self.module_id,
            'severity': self.severity,
            'priority': self.priority,
            'status_id': self.status_id,
            'status': self.status,
            'defect_type': self.defect_type,
            'category': self.category,
            'reproduction_steps': self.reproduction_steps,
            'expected_behavior': self.expected_behavior,
            'actual_behavior': self.actual_behavior,
            'environment': self.environment,
            'browser': self.browser,
            'os': self.os,
            'assigned_to': self.assigned_to,
            'reported_by': self.reported_by,
            'fixed_by': self.fixed_by,
            'verified_by': self.verified_by,
            'reported_date': self.reported_date.isoformat() if self.reported_date else None,
            'assigned_date': self.assigned_date.isoformat() if self.assigned_date else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'resolved_date': self.resolved_date.isoformat() if self.resolved_date else None,
            'closed_date': self.closed_date.isoformat() if self.closed_date else None,
            'verified_date': self.verified_date.isoformat() if self.verified_date else None,
            'resolution': self.resolution,
            'resolution_version': self.resolution_version,
            'attachments': self.attachments,
            'tags': self.tags,
            'screenshots': self.screenshots,
            'view_count': self.view_count,
            'comment_count': self.comment_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class DefectModule(db.Model):
    """缺陷模块模型"""
    __tablename__ = 'defect_modules'

    id = db.Column(db.Integer, primary_key=True, comment='主键ID')
    project_id = db.Column(db.Integer, nullable=True, index=True, comment='所属项目ID')
    name = db.Column(db.String(100), nullable=False, comment='模块名称')
    parent_id = db.Column(db.Integer, db.ForeignKey('defect_modules.id'), nullable=True, comment='父级模块ID')
    description = db.Column(db.Text, nullable=True, comment='描述')
    sort_order = db.Column(db.Integer, default=0, comment='排序号')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

    # 关系
    children = db.relationship('DefectModule',
                              backref=db.backref('parent', remote_side=[id]),
                              lazy='dynamic')

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'name': self.name,
            'parent_id': self.parent_id,
            'description': self.description,
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class DefectComment(db.Model):
    """缺陷评论模型"""
    __tablename__ = 'defect_comments'

    id = db.Column(db.Integer, primary_key=True, comment='主键ID')
    defect_id = db.Column(db.Integer, db.ForeignKey('defects.id'), nullable=False, comment='缺陷ID')
    content = db.Column(db.Text, nullable=False, comment='评论内容')
    commented_by = db.Column(db.String(100), comment='评论人')
    is_internal = db.Column(db.Boolean, default=False, comment='是否为内部评论')
    attachments = db.Column(db.Text, comment='附件路径(JSON数组)')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'defect_id': self.defect_id,
            'content': self.content,
            'commented_by': self.commented_by,
            'is_internal': self.is_internal,
            'attachments': self.attachments,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

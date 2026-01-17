"""
缺陷管理模型
"""
from datetime import datetime
from app import db
import json


class DefectWorkflow(db.Model):
    """缺陷工作流状态模型 - 定义自定义状态流程"""
    __tablename__ = 'defect_workflows'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, nullable=True, index=True)
    name = db.Column(db.String(100), nullable=False)  # 状态名称
    code = db.Column(db.String(50), nullable=False)  # 状态代码
    description = db.Column(db.Text)
    color = db.Column(db.String(20), default='#666666')  # 状态显示颜色
    sort_order = db.Column(db.Integer, default=0)
    is_default = db.Column(db.Boolean, default=False)  # 是否为默认状态
    is_closed = db.Column(db.Boolean, default=False)  # 是否为关闭状态
    transitions = db.Column(db.Text)  # 可转换到的状态 (JSON数组)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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

    id = db.Column(db.Integer, primary_key=True)
    defect_no = db.Column(db.String(50), unique=True)  # 缺陷编号
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    project_id = db.Column(db.Integer, nullable=True, index=True)

    # 关联信息
    test_case_id = db.Column(db.Integer, db.ForeignKey('test_cases.id'), nullable=True)
    test_execution_id = db.Column(db.Integer, db.ForeignKey('test_executions.id'), nullable=True)
    test_plan_id = db.Column(db.Integer, db.ForeignKey('test_plans.id'), nullable=True)
    module_id = db.Column(db.Integer, db.ForeignKey('defect_modules.id'), nullable=True, index=True)

    # 缺陷属性
    severity = db.Column(db.String(20), default='medium')  # 严重程度: critical, high, medium, low, trivial
    priority = db.Column(db.String(20), default='medium')  # 优先级: urgent, high, medium, low
    status_id = db.Column(db.Integer, db.ForeignKey('defect_workflows.id'), nullable=True)
    status = db.Column(db.String(50), default='new')  # 状态冗余字段，便于查询

    # 分类
    defect_type = db.Column(db.String(50), default='bug')  # bug, feature, improvement, task
    category = db.Column(db.String(100))  # 缺陷分类
    reproduction_steps = db.Column(db.Text)  # 复现步骤
    expected_behavior = db.Column(db.Text)  # 期望行为
    actual_behavior = db.Column(db.Text)  # 实际行为

    # 环境信息
    environment = db.Column(db.String(100))
    browser = db.Column(db.String(100))
    os = db.Column(db.String(100))

    # 分配与处理
    assigned_to = db.Column(db.String(100))  # 分配给
    reported_by = db.Column(db.String(100))  # 报告人
    fixed_by = db.Column(db.String(100))  # 修复人
    verified_by = db.Column(db.String(100))  # 验证人

    # 时间信息
    reported_date = db.Column(db.DateTime, default=datetime.utcnow)
    assigned_date = db.Column(db.DateTime)
    start_date = db.Column(db.DateTime)  # 开始处理日期
    due_date = db.Column(db.Date)  # 期望解决日期
    resolved_date = db.Column(db.DateTime)  # 解决日期
    closed_date = db.Column(db.DateTime)  # 关闭日期
    verified_date = db.Column(db.DateTime)  # 验证日期

    # 解决信息
    resolution = db.Column(db.Text)  # 解决方案
    resolution_version = db.Column(db.String(100))  # 解决版本

    # 附件与标签
    attachments = db.Column(db.Text)  # 附件路径 (JSON数组)
    tags = db.Column(db.String(500))
    screenshots = db.Column(db.Text)  # 截图路径 (JSON数组)

    # 统计
    view_count = db.Column(db.Integer, default=0)
    comment_count = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, nullable=True, index=True)
    name = db.Column(db.String(100), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('defect_modules.id'), nullable=True)
    description = db.Column(db.Text, nullable=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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

    id = db.Column(db.Integer, primary_key=True)
    defect_id = db.Column(db.Integer, db.ForeignKey('defects.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    commented_by = db.Column(db.String(100))
    is_internal = db.Column(db.Boolean, default=False)  # 是否为内部评论
    attachments = db.Column(db.Text)  # 附件路径 (JSON数组)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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

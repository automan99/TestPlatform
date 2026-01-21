"""
测试用例模型
"""
from datetime import datetime
from app import db


class TestSuite(db.Model):
    """测试套件/文件夹模型"""
    __tablename__ = 'test_suites'

    id = db.Column(db.Integer, primary_key=True, comment='主键ID')
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=True, index=True, comment='租户ID')
    name = db.Column(db.String(200), nullable=False, comment='测试套件名称')
    description = db.Column(db.Text, comment='描述')
    parent_id = db.Column(db.Integer, db.ForeignKey('test_suites.id'), nullable=True, comment='父级套件ID')
    project_id = db.Column(db.Integer, nullable=True, index=True, comment='所属项目ID')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    created_by = db.Column(db.String(100), comment='创建人')
    sort_order = db.Column(db.Integer, default=0, comment='排序号')

    # 关系
    tenant = db.relationship('Tenant', backref='test_suites')
    children = db.relationship('TestSuite', backref=db.backref('parent', remote_side=[id]),
                               lazy='dynamic', cascade='all, delete-orphan')
    test_cases = db.relationship('TestCase', backref='suite', lazy='dynamic',
                                 cascade='all, delete-orphan')

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'name': self.name,
            'description': self.description,
            'parent_id': self.parent_id,
            'project_id': self.project_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'sort_order': self.sort_order
        }


class TestCase(db.Model):
    """测试用例模型"""
    __tablename__ = 'test_cases'

    id = db.Column(db.Integer, primary_key=True, comment='主键ID')
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=True, index=True, comment='租户ID')
    name = db.Column(db.String(200), nullable=False, comment='用例名称')
    case_no = db.Column(db.String(50), nullable=True, unique=True, comment='用例编号')
    suite_id = db.Column(db.Integer, db.ForeignKey('test_suites.id'), nullable=True, comment='所属测试套件ID')
    description = db.Column(db.Text, comment='用例描述')
    preconditions = db.Column(db.Text, comment='前置条件')
    steps = db.Column(db.Text, comment='测试步骤(JSON格式)')
    expected_result = db.Column(db.Text, comment='预期结果')
    actual_result = db.Column(db.Text, comment='实际结果')
    priority = db.Column(db.String(20), default='medium', comment='优先级: low, medium, high, critical')
    case_type = db.Column(db.String(50), default='functional', comment='用例类型: functional, performance, security, ui, api')
    automation_status = db.Column(db.String(20), default='manual', comment='自动化状态: manual, automated, semi-automated')
    status = db.Column(db.String(20), default='draft', comment='状态: draft, active, archived, deprecated')
    tags = db.Column(db.String(500), comment='标签(逗号分隔)')
    estimated_time = db.Column(db.Integer, comment='预估执行时间(分钟)')
    complexity = db.Column(db.String(20), default='simple', comment='复杂度: simple, medium, complex')
    risk_level = db.Column(db.String(20), default='low', comment='风险等级: low, medium, high')
    is_deleted = db.Column(db.Boolean, default=False, comment='是否删除')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    created_by = db.Column(db.String(100), comment='创建人')
    updated_by = db.Column(db.String(100), comment='更新人')
    version = db.Column(db.Integer, default=1, comment='版本号')

    # 关系
    tenant = db.relationship('Tenant', backref='test_cases')
    executions = db.relationship('TestExecution', backref='test_case', lazy='dynamic')

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'name': self.name,
            'case_no': self.case_no,
            'suite_id': self.suite_id,
            'description': self.description,
            'preconditions': self.preconditions,
            'steps': self.steps,
            'expected_result': self.expected_result,
            'actual_result': self.actual_result,
            'priority': self.priority,
            'case_type': self.case_type,
            'automation_status': self.automation_status,
            'status': self.status,
            'tags': self.tags,
            'estimated_time': self.estimated_time,
            'complexity': self.complexity,
            'risk_level': self.risk_level,
            'is_deleted': self.is_deleted,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'version': self.version
        }

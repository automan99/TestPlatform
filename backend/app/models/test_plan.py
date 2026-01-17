"""
测试计划模型
"""
from datetime import datetime
from app import db


class TestPlan(db.Model):
    """测试计划模型"""
    __tablename__ = 'test_plans'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    plan_no = db.Column(db.String(50), unique=True)  # 计划编号
    description = db.Column(db.Text)
    project_id = db.Column(db.Integer, nullable=True, index=True)
    folder_id = db.Column(db.Integer, db.ForeignKey('test_plan_folders.id'), nullable=True)  # 所属目录
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='draft')  # draft, active, completed, cancelled, archived
    priority = db.Column(db.String(20), default='medium')  # low, medium, high
    build_version = db.Column(db.String(100))  # 测试版本
    target_environment_id = db.Column(db.Integer, db.ForeignKey('test_environments.id'), nullable=True)
    assigned_to = db.Column(db.String(100))  # 指派给
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(100))
    updated_by = db.Column(db.String(100))
    is_deleted = db.Column(db.Boolean, default=False)

    # 关系
    test_plan_cases = db.relationship('TestPlanCase', backref='test_plan', lazy='dynamic',
                                      cascade='all, delete-orphan')
    executions = db.relationship('TestExecution', backref='test_plan', lazy='dynamic')
    target_environment = db.relationship('TestEnvironment', backref='test_plans')
    folder = db.relationship('TestPlanFolder', backref='test_plans')

    def get_progress(self):
        """获取执行进度"""
        total = self.test_plan_cases.count()
        if total == 0:
            return {'total': 0, 'passed': 0, 'failed': 0, 'skipped': 0, 'progress': 0}

        passed = self.test_plan_cases.filter_by(last_status='passed').count()
        failed = self.test_plan_cases.filter_by(last_status='failed').count()
        skipped = self.test_plan_cases.filter_by(last_status='skipped').count()
        executed = passed + failed + skipped
        progress = int((executed / total) * 100) if total > 0 else 0

        return {
            'total': total,
            'passed': passed,
            'failed': failed,
            'skipped': skipped,
            'progress': progress
        }

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'plan_no': self.plan_no,
            'description': self.description,
            'project_id': self.project_id,
            'folder_id': self.folder_id,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'priority': self.priority,
            'build_version': self.build_version,
            'target_environment_id': self.target_environment_id,
            'assigned_to': self.assigned_to,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'progress': self.get_progress()
        }


class TestPlanCase(db.Model):
    """测试计划用例关联模型"""
    __tablename__ = 'test_plan_cases'

    id = db.Column(db.Integer, primary_key=True)
    test_plan_id = db.Column(db.Integer, db.ForeignKey('test_plans.id'), nullable=False)
    test_case_id = db.Column(db.Integer, db.ForeignKey('test_cases.id'), nullable=False)
    assignee = db.Column(db.String(100))  # 分配给谁执行
    sort_order = db.Column(db.Integer, default=0)
    last_status = db.Column(db.String(20), default='not_executed')  # 最后一次执行状态
    last_execution_id = db.Column(db.Integer)  # 最后一次执行记录ID

    # 关系
    test_case = db.relationship('TestCase', backref='test_plan_cases')
    executions = db.relationship('TestExecution', backref='test_plan_case', lazy='dynamic')

    __table_args__ = (db.UniqueConstraint('test_plan_id', 'test_case_id', name='unique_plan_case'),)

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'test_plan_id': self.test_plan_id,
            'test_case_id': self.test_case_id,
            'assignee': self.assignee,
            'sort_order': self.sort_order,
            'last_status': self.last_status,
            'last_execution_id': self.last_execution_id
        }


class TestExecution(db.Model):
    """测试执行记录模型"""
    __tablename__ = 'test_executions'

    id = db.Column(db.Integer, primary_key=True)
    test_plan_id = db.Column(db.Integer, db.ForeignKey('test_plans.id'), nullable=True)
    test_case_id = db.Column(db.Integer, db.ForeignKey('test_cases.id'), nullable=False)
    test_plan_case_id = db.Column(db.Integer, db.ForeignKey('test_plan_cases.id'), nullable=True)
    status = db.Column(db.String(20), default='not_executed')  # passed, failed, blocked, skipped, not_executed
    execution_time = db.Column(db.DateTime, default=datetime.utcnow)
    executed_by = db.Column(db.String(100))
    actual_result = db.Column(db.Text)
    notes = db.Column(db.Text)
    duration = db.Column(db.Integer)  # 执行时长(秒)
    environment_id = db.Column(db.Integer, db.ForeignKey('test_environments.id'), nullable=True)
    screenshots = db.Column(db.Text)  # 截图路径 (JSON数组)
    defect_ids = db.Column(db.Text)  # 关联的缺陷ID列表 (JSON数组)

    # 关系
    environment = db.relationship('TestEnvironment', backref='executions')

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'test_plan_id': self.test_plan_id,
            'test_case_id': self.test_case_id,
            'test_plan_case_id': self.test_plan_case_id,
            'status': self.status,
            'execution_time': self.execution_time.isoformat() if self.execution_time else None,
            'executed_by': self.executed_by,
            'actual_result': self.actual_result,
            'notes': self.notes,
            'duration': self.duration,
            'environment_id': self.environment_id,
            'screenshots': self.screenshots,
            'defect_ids': self.defect_ids
        }


class TestPlanFolder(db.Model):
    """测试计划目录模型"""
    __tablename__ = 'test_plan_folders'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    project_id = db.Column(db.Integer, nullable=False, index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('test_plan_folders.id'), nullable=True)
    description = db.Column(db.Text)
    sort_order = db.Column(db.Integer, default=0)
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(100))

    # 关系
    children = db.relationship('TestPlanFolder', backref=db.backref('parent', remote_side=[id]),
                               lazy='dynamic', cascade='all, delete-orphan')

    def get_plan_count(self):
        """获取目录下的计划数量"""
        return TestPlan.query.filter_by(folder_id=self.id, is_deleted=False).count()

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'project_id': self.project_id,
            'parent_id': self.parent_id,
            'description': self.description,
            'sort_order': self.sort_order,
            'plan_count': self.get_plan_count(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

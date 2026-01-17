"""
项目管理模型
"""
from datetime import datetime
from app import db


class Project(db.Model):
    """项目模型"""
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=True, index=True, comment='租户ID')
    name = db.Column(db.String(200), nullable=False, comment='项目名称')
    code = db.Column(db.String(50), nullable=False, unique=True, comment='项目代码')
    description = db.Column(db.Text, comment='项目描述')
    project_type = db.Column(db.String(50), default='web', comment='项目类型: web, mobile, api, desktop')
    status = db.Column(db.String(20), default='active', comment='状态: active, archived, completed')

    # 项目配置
    key = db.Column(db.String(10), unique=True, comment='项目标识符（用于缺陷编号前缀）')
    url = db.Column(db.String(500), comment='项目URL')
    repository = db.Column(db.String(500), comment='代码仓库地址')

    # 限制配置
    max_test_suites = db.Column(db.Integer, default=100, comment='最大测试套件数')
    max_test_cases = db.Column(db.Integer, default=1000, comment='最大测试用例数')
    max_test_plans = db.Column(db.Integer, default=50, comment='最大测试计划数')

    # 统计信息
    test_suite_count = db.Column(db.Integer, default=0, comment='测试套件数')
    test_case_count = db.Column(db.Integer, default=0, comment='测试用例数')
    test_plan_count = db.Column(db.Integer, default=0, comment='测试计划数')
    defect_count = db.Column(db.Integer, default=0, comment='缺陷数')

    # 排序和显示
    sort_order = db.Column(db.Integer, default=0, comment='排序')
    icon = db.Column(db.String(100), comment='图标')
    color = db.Column(db.String(20), default='#409EFF', comment='颜色')

    # 时间和用户
    owner = db.Column(db.String(100), comment='项目负责人')
    lead = db.Column(db.String(100), comment='项目主管')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    created_by = db.Column(db.String(100), comment='创建人')
    updated_by = db.Column(db.String(100), comment='更新人')

    # 软删除
    is_deleted = db.Column(db.Boolean, default=False, comment='是否删除')

    # 关系
    tenant = db.relationship('Tenant', backref='projects')

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'project_type': self.project_type,
            'status': self.status,
            'key': self.key,
            'url': self.url,
            'repository': self.repository,
            'max_test_suites': self.max_test_suites,
            'max_test_cases': self.max_test_cases,
            'max_test_plans': self.max_test_plans,
            'test_suite_count': self.test_suite_count,
            'test_case_count': self.test_case_count,
            'test_plan_count': self.test_plan_count,
            'defect_count': self.defect_count,
            'sort_order': self.sort_order,
            'icon': self.icon,
            'color': self.color,
            'owner': self.owner,
            'lead': self.lead,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'is_deleted': self.is_deleted
        }

    def update_statistics(self):
        """更新项目统计信息"""
        from app.models import TestCase, TestSuite, TestPlan, Defect

        self.test_suite_count = TestSuite.query.filter_by(
            project_id=self.id
        ).count()

        self.test_case_count = TestCase.query.filter(
            TestCase.is_deleted == False,
            TestCase.suite_id.isnot(None)
        ).join(TestSuite).filter(TestSuite.project_id == self.id).count()

        self.test_plan_count = TestPlan.query.filter_by(
            project_id=self.id
        ).count()

        self.defect_count = Defect.query.filter_by(
            project_id=self.id
        ).count()

        db.session.commit()

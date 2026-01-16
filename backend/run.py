"""
测试管理平台 - 后端启动入口
"""
import os
from app import create_app, db
from app.models import (
    TestCase, TestSuite, TestPlan, TestPlanCase,
    TestEnvironment, Defect, DefectWorkflow,
    TestExecution, TestReport, Tenant, TenantUser, User
)

# 创建应用实例
app = create_app(os.getenv('FLASK_ENV') or 'development')

# Shell上下文
@app.shell_context_processor
def make_shell_context():
    """注册shell上下文"""
    return {
        'db': db,
        'TestCase': TestCase,
        'TestSuite': TestSuite,
        'TestPlan': TestPlan,
        'TestPlanCase': TestPlanCase,
        'TestEnvironment': TestEnvironment,
        'Defect': Defect,
        'DefectWorkflow': DefectWorkflow,
        'TestExecution': TestExecution,
        'TestReport': TestReport,
        'Tenant': Tenant,
        'TenantUser': TenantUser,
        'User': User,
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

"""
API模块初始化
"""
from flask import Blueprint
from flask_restx import Api
from app.config import Config

# 创建蓝图
api_blueprint = Blueprint('api', __name__)

# 创建API实例
api = Api(
    api_blueprint,
    version='v1',
    title=Config.API_TITLE,
    description='测试管理平台 REST API',
    doc=Config.API_PREFIX + '/doc',
    prefix=Config.API_PREFIX
)

# 导入所有命名空间
from app.apis.test_case import test_suite_ns, test_case_ns
from app.apis.test_plan import test_plan_ns, test_execution_ns, test_plan_folder_ns
from app.apis.test_env import test_environment_ns, environment_resource_ns
from app.apis.defect import defect_ns, defect_workflow_ns, defect_comment_ns, defect_module_ns
from app.apis.test_report import test_report_ns, report_metric_ns
from app.apis.tenant import tenant_ns
from app.apis.auth import auth_ns
from app.apis.user import user_ns
from app.apis.oauth import oauth_ns
from app.apis.project import project_ns
from app.apis.ai_execution import ai_execution_ns
from app.apis.mcp_skills import mcp_server_ns, skill_ns
from app.apis.skill_repositories import skill_repository_ns, git_skill_ns
from app.apis.llm_models import llm_model_ns
from app.apis.menu import menu_ns
from app.apis.role import role_ns

# 注册命名空间
api.add_namespace(project_ns, path='/projects')
api.add_namespace(test_suite_ns, path='/test-suites')
api.add_namespace(test_case_ns, path='/test-cases')
api.add_namespace(test_plan_ns, path='/test-plans')
api.add_namespace(test_execution_ns, path='/test-executions')
api.add_namespace(test_plan_folder_ns, path='/test-plan-folders')
api.add_namespace(test_environment_ns, path='/environments')
api.add_namespace(environment_resource_ns, path='/environment-resources')
api.add_namespace(defect_workflow_ns, path='/defect-workflows')
api.add_namespace(defect_ns, path='/defects')
api.add_namespace(defect_comment_ns, path='/defect-comments')
api.add_namespace(defect_module_ns, path='/defect-modules')
api.add_namespace(test_report_ns, path='/test-reports')
api.add_namespace(report_metric_ns, path='/report-metrics')
api.add_namespace(tenant_ns, path='/tenants')
api.add_namespace(auth_ns, path='/auth')
api.add_namespace(user_ns, path='/users')
api.add_namespace(oauth_ns, path='/oauth')
api.add_namespace(ai_execution_ns, path='/ai-execution')
api.add_namespace(mcp_server_ns, path='/mcp-servers')
api.add_namespace(skill_ns, path='/skills')
api.add_namespace(skill_repository_ns, path='/skill-repositories')
api.add_namespace(git_skill_ns, path='/git-skills')
api.add_namespace(llm_model_ns, path='/llm-models')
api.add_namespace(menu_ns, path='/menus')
api.add_namespace(role_ns, path='/roles')

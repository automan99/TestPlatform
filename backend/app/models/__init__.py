"""
数据模型模块
"""
from .tenant import Tenant, TenantUser
from .user import User
from .project import Project
from .test_case import TestCase, TestSuite
from .test_plan import TestPlan, TestPlanCase, TestExecution, TestPlanFolder
from .test_env import TestEnvironment, EnvironmentResource
from .defect import Defect, DefectWorkflow, DefectComment, DefectModule
from .test_report import TestReport, ReportMetric
from .mcp_tool import MCPServer, MCPTool, MCPResource, MCPToolExecution
from .skill import Skill
from .skill_repository import GitCredential, SkillRepository, GitSkill, SkillSyncLog
from .llm_model import LLMModel
from .menu import Menu, Role, RoleMenu, UserRole

__all__ = [
    'Tenant', 'TenantUser', 'User',
    'Project',
    'TestCase', 'TestSuite',
    'TestPlan', 'TestPlanCase', 'TestExecution', 'TestPlanFolder',
    'TestEnvironment', 'EnvironmentResource',
    'Defect', 'DefectWorkflow', 'DefectComment', 'DefectModule',
    'TestReport', 'ReportMetric',
    'MCPServer', 'MCPTool', 'MCPResource', 'MCPToolExecution', 'Skill',
    'GitCredential', 'SkillRepository', 'GitSkill', 'SkillSyncLog',
    'LLMModel',
    'Menu', 'Role', 'RoleMenu', 'UserRole'
]

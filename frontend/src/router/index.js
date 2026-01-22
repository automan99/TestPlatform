import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/',
    component: () => import('@/views/Layout.vue'),
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '首页', icon: 'House', code: 'dashboard' }
      },
      {
        path: 'test-cases',
        name: 'TestCases',
        component: () => import('@/views/TestCase/Index.vue'),
        meta: { title: '测试用例', icon: 'Document', code: 'test-cases' }
      },
      {
        path: 'test-cases/ai-execution',
        name: 'AIExecution',
        component: () => import('@/views/TestCase/AIExecution.vue'),
        meta: { title: 'AI执行', hidden: true }
      },
      {
        path: 'test-plans',
        name: 'TestPlans',
        component: () => import('@/views/TestPlan/Index.vue'),
        meta: { title: '测试计划', icon: 'Calendar', code: 'test-plans' }
      },
      {
        path: 'test-executions/:planId',
        name: 'TestExecutions',
        component: () => import('@/views/TestPlan/Execution.vue'),
        meta: { title: '执行测试', hidden: true }
      },
      {
        path: 'environments',
        name: 'Environments',
        component: () => import('@/views/Environment/Index.vue'),
        meta: { title: '测试环境', icon: 'Monitor', code: 'environments' }
      },
      {
        path: 'defects',
        name: 'Defects',
        component: () => import('@/views/Defect/Index.vue'),
        meta: { title: '缺陷管理', icon: 'CircleClose', code: 'defects' }
      },
      {
        path: 'defects/:id',
        name: 'DefectDetail',
        component: () => import('@/views/Defect/Detail.vue'),
        meta: { title: '缺陷详情', hidden: true }
      },
      {
        path: 'mcp-server',
        name: 'MCPServer',
        component: () => import('@/views/MCPSkills/Index.vue'),
        meta: { title: 'MCP Server', icon: 'Connection', code: 'mcp-server' }
      },
      {
        path: 'skills',
        name: 'Skills',
        component: () => import('@/views/Skills/Index.vue'),
        meta: { title: 'Skills', icon: 'Files', code: 'skills' }
      },
      {
        path: 'llm-models',
        name: 'LLMModels',
        component: () => import('@/views/Settings/LLMModels.vue'),
        meta: { title: 'LLM模型管理', icon: 'Operation', code: 'llm-models' }
      },
      {
        path: 'agent-management',
        redirect: 'mcp-server'
      },
      {
        path: 'reports',
        name: 'Reports',
        component: () => import('@/views/Report/Index.vue'),
        meta: { title: '测试报告', icon: 'DataAnalysis', code: 'reports' }
      },
      {
        path: 'projects',
        name: 'Projects',
        component: () => import('@/views/Projects.vue'),
        meta: { title: '项目管理', icon: 'FolderOpened', code: 'projects' }
      },
      {
        path: 'tenants',
        name: 'Tenants',
        component: () => import('@/views/Tenant/Index.vue'),
        meta: { title: '租户管理', icon: 'OfficeBuilding', code: 'tenants', requireSuperAdmin: true }
      },
      {
        path: 'menu-management',
        name: 'MenuManagement',
        component: () => import('@/views/Menu/Index.vue'),
        meta: { title: '菜单管理', icon: 'Menu', code: 'menu-management', requireSuperAdmin: true }
      },
      {
        path: 'system-config',
        redirect: 'settings'
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/Settings.vue'),
        meta: { title: '基本设置', icon: 'Setting', code: 'settings' }
      },
      {
        path: 'members',
        name: 'Members',
        component: () => import('@/views/Settings/Members.vue'),
        meta: { title: '成员管理', icon: 'User', code: 'members' }
      },
      {
        path: 'oauth',
        name: 'OAuth',
        component: () => import('@/views/Settings/OAuth.vue'),
        meta: { title: 'OAuth认证', icon: 'Connection', code: 'oauth' }
      },
      {
        path: 'workflow',
        name: 'Workflow',
        component: () => import('@/views/Settings/Workflow.vue'),
        meta: { title: '缺陷工作流', icon: 'Operation', code: 'workflow' }
      },
      {
        path: 'notification',
        name: 'Notification',
        component: () => import('@/views/Settings/Notification.vue'),
        meta: { title: '通知设置', icon: 'Bell', code: 'notification' }
      },
      {
        path: 'roles',
        name: 'Roles',
        component: () => import('@/views/Role/Index.vue'),
        meta: { title: '角色管理', icon: 'UserFilled', code: 'roles', requireSuperAdmin: true }
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/Settings.vue'),
        meta: { title: '系统设置', icon: 'Setting', code: 'settings' }
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/Profile.vue'),
        meta: { title: '个人信息', hidden: true }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫 - 权限控制
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')

  if (!token && to.path !== '/login') {
    next('/login')
    return
  }

  if (to.path === '/login' && token) {
    next('/dashboard')
    return
  }

  // 检查超级管理员权限
  if (to.meta.requireSuperAdmin) {
    const userStr = localStorage.getItem('user')
    if (userStr) {
      const user = JSON.parse(userStr)
      if (user.role !== 'super_admin') {
        // 不是超级管理员，跳转到首页
        next('/dashboard')
        return
      }
    }
  }

  document.title = to.meta.title ? `${to.meta.title} - 测试管理平台` : '测试管理平台'
  next()
})

export default router

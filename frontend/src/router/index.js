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
        meta: { title: '首页', icon: 'House' }
      },
      {
        path: 'test-cases',
        name: 'TestCases',
        component: () => import('@/views/TestCase/Index.vue'),
        meta: { title: '测试用例', icon: 'Document' }
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
        meta: { title: '测试计划', icon: 'Calendar' }
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
        meta: { title: '测试环境', icon: 'Monitor' }
      },
      {
        path: 'defects',
        name: 'Defects',
        component: () => import('@/views/Defect/Index.vue'),
        meta: { title: '缺陷管理', icon: 'CircleClose' }
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
        meta: { title: 'MCP Server', icon: 'Connection' }
      },
      {
        path: 'skills',
        name: 'Skills',
        component: () => import('@/views/Skills/Index.vue'),
        meta: { title: 'Skills', icon: 'Files' }
      },
      {
        path: 'reports',
        name: 'Reports',
        component: () => import('@/views/Report/Index.vue'),
        meta: { title: '测试报告', icon: 'DataAnalysis' }
      },
      {
        path: 'projects',
        name: 'Projects',
        component: () => import('@/views/Projects.vue'),
        meta: { title: '项目管理', icon: 'FolderOpened' }
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/Settings.vue'),
        meta: { title: '系统设置', icon: 'Setting' }
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

// 路由守卫
router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - 测试管理平台` : '测试管理平台'
  next()
})

export default router

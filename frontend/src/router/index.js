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
        path: 'tenants',
        name: 'Tenants',
        component: () => import('@/views/Tenant/Index.vue'),
        meta: { title: '租户管理', icon: 'OfficeBuilding' }
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/Settings.vue'),
        meta: { title: '系统设置', icon: 'Setting' }
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

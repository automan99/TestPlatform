import { defineStore } from 'pinia'
import { ref } from 'vue'
import { menuApi } from '@/api/menu'

export const useMenuStore = defineStore('menu', () => {
  const userMenus = ref([])

  async function loadUserMenus() {
    try {
      const token = localStorage.getItem('token')
      if (!token) {
        userMenus.value = []
        return
      }

      // 从后端API获取用户菜单
      const res = await menuApi.getUserMenus()
      // API返回格式: { success: true, data: [...] }
      // 后端已返回树形结构，包含children字段
      const apiMenus = res.data || []
      userMenus.value = transformMenus(apiMenus)
    } catch (error) {
      console.error('Failed to load user menus:', error)
      // 如果API调用失败，使用默认菜单作为降级方案
      const userStr = localStorage.getItem('user')
      if (userStr) {
        const user = JSON.parse(userStr)
        if (user.role === 'super_admin') {
          userMenus.value = getAllMenus()
        } else {
          userMenus.value = getDefaultMenus()
        }
      } else {
        userMenus.value = []
      }
    }
  }

  function transformMenus(menus) {
    return menus.map(m => {
      const menu = {
        name: m.code,
        title: m.title,
        icon: m.icon,
        path: m.path,
        code: m.code
      }
      // 如果有子菜单，递归转换
      if (m.children && m.children.length > 0) {
        menu.children = transformMenus(m.children)
      }
      return menu
    })
  }

  function getAllMenus() {
    return [
      { name: 'Dashboard', title: '首页', icon: 'House', path: '/dashboard', code: 'dashboard' },
      { name: 'TestCases', title: '测试用例', icon: 'Document', path: '/test-cases', code: 'test-cases' },
      { name: 'TestPlans', title: '测试计划', icon: 'Calendar', path: '/test-plans', code: 'test-plans' },
      { name: 'Environments', title: '测试环境', icon: 'Monitor', path: '/environments', code: 'environments' },
      { name: 'Defects', title: '缺陷管理', icon: 'CircleClose', path: '/defects', code: 'defects' },
      { name: 'Reports', title: '测试报告', icon: 'DataAnalysis', path: '/reports', code: 'reports' },
      { name: 'Projects', title: '项目管理', icon: 'FolderOpened', path: '/projects', code: 'projects' },
      { name: 'MCPServer', title: 'MCP Server', icon: 'Connection', path: '/mcp-server', code: 'mcp-server' },
      { name: 'Skills', title: 'Skills', icon: 'Files', path: '/skills', code: 'skills' },
      { name: 'Settings', title: '系统设置', icon: 'Setting', path: '/settings', code: 'settings' },
      { name: 'Tenants', title: '租户管理', icon: 'OfficeBuilding', path: '/tenants', code: 'tenants', requireSuperAdmin: true },
      { name: 'MenuManagement', title: '菜单管理', icon: 'Menu', path: '/menu-management', code: 'menu-management', requireSuperAdmin: true },
      { name: 'Roles', title: '角色管理', icon: 'UserFilled', path: '/roles', code: 'roles', requireSuperAdmin: true }
    ]
  }

  function getDefaultMenus() {
    return [
      { name: 'Dashboard', title: '首页', icon: 'House', path: '/dashboard', code: 'dashboard' },
      { name: 'TestCases', title: '测试用例', icon: 'Document', path: '/test-cases', code: 'test-cases' },
      { name: 'TestPlans', title: '测试计划', icon: 'Calendar', path: '/test-plans', code: 'test-plans' },
      { name: 'Environments', title: '测试环境', icon: 'Monitor', path: '/environments', code: 'environments' },
      { name: 'Defects', title: '缺陷管理', icon: 'CircleClose', path: '/defects', code: 'defects' },
      { name: 'Reports', title: '测试报告', icon: 'DataAnalysis', path: '/reports', code: 'reports' },
      { name: 'Projects', title: '项目管理', icon: 'FolderOpened', path: '/projects', code: 'projects' },
      { name: 'MCPServer', title: 'MCP Server', icon: 'Connection', path: '/mcp-server', code: 'mcp-server' },
      { name: 'Skills', title: 'Skills', icon: 'Files', path: '/skills', code: 'skills' },
      { name: 'Settings', title: '系统设置', icon: 'Setting', path: '/settings', code: 'settings' }
    ]
  }

  return {
    userMenus,
    loadUserMenus,
    getAllMenus,
    getDefaultMenus
  }
})

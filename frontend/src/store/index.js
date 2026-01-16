import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAppStore = defineStore('app', () => {
  // 侧边栏状态
  const sidebarCollapsed = ref(false)

  // 当前项目
  const currentProject = ref(null)

  // 用户信息
  const user = ref(null)

  // 语言设置
  const language = ref(localStorage.getItem('language') || 'zh-CN')

  // 计算属性
  const isSidebarCollapsed = computed(() => sidebarCollapsed.value)

  // Actions
  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  function setSidebarCollapsed(collapsed) {
    sidebarCollapsed.value = collapsed
  }

  function setCurrentProject(project) {
    currentProject.value = project
  }

  function setUser(userInfo) {
    user.value = userInfo
  }

  function setLanguage(lang) {
    language.value = lang
    localStorage.setItem('language', lang)
    // 可以在这里触发页面刷新或其他更新逻辑
  }

  function logout() {
    user.value = null
    currentProject.value = null
    localStorage.removeItem('token')
  }

  return {
    sidebarCollapsed,
    currentProject,
    user,
    language,
    isSidebarCollapsed,
    toggleSidebar,
    setSidebarCollapsed,
    setCurrentProject,
    setUser,
    setLanguage,
    logout
  }
})

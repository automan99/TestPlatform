import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { projectApi } from '@/api/project'

export const useProjectStore = defineStore('project', () => {
  // 状态
  const projectList = ref([])
  const currentProject = ref(null)
  const loading = ref(false)

  // 计算属性
  const currentProjectId = computed(() => currentProject.value?.id)
  const currentProjectName = computed(() => currentProject.value?.name || '选择项目')

  // Actions
  async function fetchProjects() {
    loading.value = true
    try {
      const res = await projectApi.getList({
        per_page: 100,
        status: 'active'
      })
      if (res.code === 200) {
        projectList.value = res.data.items || []
        // 如果没有当前项目，设置第一个为默认
        if (!currentProject.value && projectList.value.length > 0) {
          currentProject.value = projectList.value[0]
        }
      }
      return res
    } catch (error) {
      console.error('Failed to fetch projects:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  function setCurrentProject(project) {
    if (typeof project === 'number') {
      const found = projectList.value.find(p => p.id === project)
      currentProject.value = found || null
    } else {
      currentProject.value = project
    }
    // 保存到localStorage
    if (currentProject.value) {
      localStorage.setItem('currentProjectId', String(currentProject.value.id))
    }
  }

  async function switchProject(projectId) {
    try {
      const res = await projectApi.switch(projectId)
      if (res.code === 200) {
        setCurrentProject(res.data.project)
        return res
      }
    } catch (error) {
      console.error('Failed to switch project:', error)
      throw error
    }
  }

  function clearCurrentProject() {
    currentProject.value = null
    localStorage.removeItem('currentProjectId')
  }

  // 初始化：从localStorage恢复
  function init() {
    const savedProjectId = localStorage.getItem('currentProjectId')
    if (savedProjectId) {
      const projectId = parseInt(savedProjectId)
      const found = projectList.value.find(p => p.id === projectId)
      if (found) {
        currentProject.value = found
      }
    }
  }

  return {
    projectList,
    currentProject,
    currentProjectId,
    currentProjectName,
    loading,
    fetchProjects,
    setCurrentProject,
    switchProject,
    clearCurrentProject,
    init
  }
})

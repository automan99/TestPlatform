<template>
  <el-container class="layout-container">
    <el-aside :width="sidebarWidth" class="sidebar">
      <div class="logo">
        <el-icon :size="24"><Monitor /></el-icon>
        <span v-show="!appStore.isSidebarCollapsed">{{ systemName }}</span>
      </div>
      <el-menu
        :default-active="currentRoute"
        :collapse="appStore.isSidebarCollapsed"
        router
        class="sidebar-menu"
      >
        <el-menu-item index="/dashboard">
          <el-icon><House /></el-icon>
          <template #title>{{ t('menu.home') }}</template>
        </el-menu-item>
        <el-menu-item index="/test-cases">
          <el-icon><Document /></el-icon>
          <template #title>{{ t('menu.testCases') }}</template>
        </el-menu-item>
        <el-menu-item index="/test-plans">
          <el-icon><Calendar /></el-icon>
          <template #title>{{ t('menu.testPlans') }}</template>
        </el-menu-item>
        <el-menu-item index="/environments">
          <el-icon><Monitor /></el-icon>
          <template #title>{{ t('menu.environments') }}</template>
        </el-menu-item>
        <el-menu-item index="/defects">
          <el-icon><CircleClose /></el-icon>
          <template #title>{{ t('menu.defects') }}</template>
        </el-menu-item>
        <el-menu-item index="/reports">
          <el-icon><DataAnalysis /></el-icon>
          <template #title>{{ t('menu.reports') }}</template>
        </el-menu-item>
        <el-menu-item index="/projects">
          <el-icon><FolderOpened /></el-icon>
          <template #title>{{ t('project.title') }}</template>
        </el-menu-item>
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <template #title>{{ t('menu.settings') }}</template>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-button
            :icon="appStore.isSidebarCollapsed ? Expand : Fold"
          />
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">{{ t('menu.home') }}</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentRouteMeta?.title">
              {{ currentRouteMeta.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <!-- 项目切换器 -->
          <el-dropdown v-if="projectStore.projectList.length > 0" @command="handleProjectSwitch">
            <div class="project-info">
              <el-icon :size="18"><FolderOpened /></el-icon>
              <span class="project-name">{{ currentProjectName }}</span>
              <el-icon :size="12"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item
                  v-for="project in projectStore.projectList"
                  :key="project.id"
                  :command="project.id"
                  :disabled="project.id === currentProjectId"
                >
                  <span
                    v-if="project.icon"
                    class="project-icon"
                    :style="{ backgroundColor: project.color }"
                  >
                    {{ project.icon }}
                  </span>
                  <span
                    v-else
                    class="project-icon"
                    :style="{ backgroundColor: project.color }"
                  >
                    {{ project.name.charAt(0) }}
                  </span>
                  <span style="margin-left: 8px">{{ project.name }}</span>
                  <el-tag v-if="project.id === currentProjectId" size="small" type="success" style="margin-left: 8px">
                    当前
                  </el-tag>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          <div style="width: 1px; height: 24px; background: #e4e7ed"></div>
          <!-- 租户切换器 -->
          <el-dropdown v-if="tenantStore.tenantList.length > 0" @command="handleTenantSwitch">
            <div class="tenant-info">
              <el-icon :size="18"><OfficeBuilding /></el-icon>
              <span class="tenant-name">{{ currentTenantName }}</span>
              <el-icon :size="12"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item
                  v-for="tenant in tenantStore.tenantList"
                  :key="tenant.id"
                  :command="tenant.id"
                  :disabled="tenant.id === currentTenantId"
                >
                  {{ tenant.name }}
                  <el-tag v-if="tenant.id === currentTenantId" size="small" type="success" style="margin-left: 8px">
                    {{ t('tenant.currentTenant') }}
                  </el-tag>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          <div style="width: 1px; height: 24px; background: #e4e7ed"></div>
          <el-dropdown>
            <div class="user-info">
              <el-icon :size="20"><User /></el-icon>
              <span>Admin</span>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>{{ t('common.edit') }} Profile</el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">{{ t('common.back') }}</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '@/store'
import { useI18n } from '@/i18n'
import { useTenantStore } from '@/store/tenant'
import { useProjectStore } from '@/store/project'
import { ElMessage } from 'element-plus'
import {
  Monitor, House, Document, Calendar, CircleClose,
  DataAnalysis, Setting, Expand, Fold, User, OfficeBuilding, ArrowDown, FolderOpened
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()
const { t } = useI18n()
const tenantStore = useTenantStore()
const projectStore = useProjectStore()

// 系统名称
const systemName = ref(t('dashboard.title'))

// 加载系统名称
function loadSystemName() {
  const savedSettings = localStorage.getItem('systemSettings')
  if (savedSettings) {
    try {
      const settings = JSON.parse(savedSettings)
      if (settings.systemName) {
        systemName.value = settings.systemName
      }
    } catch (e) {
      console.error('Load system name failed:', e)
    }
  }
}

const currentRoute = computed(() => route.path)
const currentRouteMeta = computed(() => route.meta)

const sidebarWidth = computed(() =>
  appStore.isSidebarCollapsed ? '64px' : '200px'
)

const currentTenantId = computed(() => tenantStore.currentTenant?.id)
const currentTenantName = computed(() => tenantStore.currentTenant?.name || t('tenant.switchTenant'))

const currentProjectId = computed(() => projectStore.currentProject?.id)
const currentProjectName = computed(() => projectStore.currentProject?.name || '选择项目')

async function handleTenantSwitch(tenantId) {
  try {
    await tenantStore.setCurrentTenant(tenantId)
    ElMessage.success(t('tenant.switchSuccess'))
    router.push('/dashboard')
  } catch (error) {
    ElMessage.error(error.response?.data?.message || t('tenant.switchFailed'))
  }
}

async function handleProjectSwitch(projectId) {
  try {
    await projectStore.switchProject(projectId)
    ElMessage.success(t('project.switchSuccess'))
    // 各页面的watch会自动重新加载数据，不需要刷新整个页面
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '切换项目失败')
  }
}

function handleLogout() {
  appStore.logout()
  router.push('/login')
}

onMounted(async () => {
  // 加载系统名称
  loadSystemName()

  // 检查是否已登录
  const token = localStorage.getItem('token')
  if (!token) {
    return
  }

  // 加载租户
  try {
    await tenantStore.loadMyTenants()
    if (!tenantStore.currentTenant && tenantStore.tenantList.length > 0) {
      const savedTenantId = localStorage.getItem('currentTenantId')
      if (savedTenantId) {
        const tenant = tenantStore.tenantList.find(t => t.id === parseInt(savedTenantId))
        if (tenant) {
          tenantStore.currentTenant = tenant
        }
      }
    }

    // 加载项目
    await projectStore.fetchProjects()
    projectStore.init()
  } catch (error) {
    console.error('初始化数据失败:', error)
  }
})
</script>

<style scoped>
.layout-container {
  height: 100%;
}

.sidebar {
  background: #304156;
  transition: width 0.3s;
  overflow: hidden;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  gap: 8px;
}

.sidebar-menu {
  border: none;
  background: #304156;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 200px;
}

/* 菜单文字颜色 */
:deep(.el-menu-item) {
  color: #bfcbd9;
  font-size: 14px;
}

:deep(.el-menu-item:hover) {
  background: #263445 !important;
  color: #fff !important;
}

:deep(.el-menu-item.is-active) {
  background: #409eff !important;
  color: #fff !important;
}

/* 菜单图标颜色 */
:deep(.el-menu-item .el-icon) {
  color: inherit;
}

/* 折叠时的样式 */
:deep(.el-menu--collapse .el-menu-item) {
  color: #bfcbd9;
}

:deep(.el-menu--collapse .el-menu-item:hover) {
  color: #fff !important;
}

:deep(.el-menu--collapse .el-menu-item.is-active) {
  color: #fff !important;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #e4e7ed;
  background: #fff;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.tenant-info {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 4px;
  transition: background 0.2s;
}

.tenant-info:hover {
  background: #f5f7fa;
}

.tenant-name {
  font-size: 14px;
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.project-info {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 4px;
  transition: background 0.2s;
}

.project-info:hover {
  background: #f5f7fa;
}

.project-name {
  font-size: 14px;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.project-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 4px;
  color: white;
  font-weight: 500;
  font-size: 12px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
}

.user-info:hover {
  background: #f5f7fa;
}

.main-content {
  background: #f5f7fa;
  padding: 5px;
}
</style>

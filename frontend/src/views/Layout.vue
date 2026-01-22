<template>
  <el-container class="precision-layout">
    <!-- Sidebar with Precision Engineering Aesthetic -->
    <el-aside :width="sidebarWidth" class="precision-sidebar">
      <!-- Logo Area -->
      <div class="sidebar-logo">
        <div class="logo-mark">
          <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
            <rect x="2" y="2" width="24" height="24" rx="4" stroke="currentColor" stroke-width="1.5"/>
            <path d="M9 14L14 9L19 14M9 18L14 13L19 18" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <transition name="logo-fade">
          <span v-show="!appStore.isSidebarCollapsed" class="logo-type">{{ systemName }}</span>
        </transition>
      </div>

      <!-- Navigation Menu -->
      <el-menu
        :default-active="currentRoute"
        :collapse="appStore.isSidebarCollapsed"
        router
        class="sidebar-menu"
      >
        <template v-for="menu in menuList" :key="menu.code">
          <!-- 有子菜单的情况 -->
          <el-sub-menu v-if="menu.children && menu.children.length > 0" :index="menu.code">
            <template #title>
              <el-icon>
                <component :is="iconMap[menu.icon]" />
              </el-icon>
              <span>{{ menu.title }}</span>
            </template>
            <el-menu-item
              v-for="child in menu.children"
              :key="child.code"
              :index="child.path"
            >
              <el-icon>
                <component :is="iconMap[child.icon]" />
              </el-icon>
              <template #title>{{ child.title }}</template>
            </el-menu-item>
          </el-sub-menu>
          <!-- 无子菜单的情况 -->
          <el-menu-item
            v-else
            :index="menu.path"
            class="nav-item"
          >
            <el-icon>
              <component :is="iconMap[menu.icon]" />
            </el-icon>
            <template #title>{{ menu.title }}</template>
          </el-menu-item>
        </template>
      </el-menu>

      <!-- Sidebar Footer -->
      <div class="sidebar-footer" v-show="!appStore.isSidebarCollapsed">
        <div class="footer-badge">
          <span class="badge-label">TestP Platform</span>
          <span class="badge-version">v1.0.0</span>
        </div>
      </div>
    </el-aside>

    <!-- Main Content Area -->
    <el-container class="content-wrapper">
      <!-- Header -->
      <el-header class="precision-header">
        <div class="header-section header-left">
          <el-button
            :icon="appStore.isSidebarCollapsed ? Expand : Fold"
            class="icon-btn"
            @click="appStore.toggleSidebar"
          />
          <nav class="breadcrumb-nav">
            <el-breadcrumb separator="/">
              <el-breadcrumb-item :to="{ path: '/' }">{{ t('menu.home') }}</el-breadcrumb-item>
              <el-breadcrumb-item v-if="currentRouteMeta?.title">
                {{ currentRouteMeta.title }}
              </el-breadcrumb-item>
            </el-breadcrumb>
          </nav>
        </div>

        <div class="header-section header-right">
          <!-- Project Switcher -->
          <div v-if="projectStore.projectList.length > 0" class="header-control">
            <el-dropdown @command="handleProjectSwitch" trigger="click">
              <div class="control-trigger">
                <el-icon><FolderOpened /></el-icon>
                <span class="control-label">{{ currentProjectName }}</span>
                <el-icon class="control-caret"><ArrowDown /></el-icon>
              </div>
              <template #dropdown>
                <el-dropdown-menu class="precision-dropdown">
                  <el-dropdown-item
                    v-for="project in projectStore.projectList"
                    :key="project.id"
                    :command="project.id"
                    :disabled="project.id === currentProjectId"
                  >
                    <span
                      v-if="project.icon"
                      class="project-indicator"
                      :style="{ backgroundColor: project.color }"
                    ></span>
                    <span
                      v-else
                      class="project-indicator indicator-text"
                      :style="{ backgroundColor: project.color }"
                    >
                      {{ project.name.charAt(0) }}
                    </span>
                    <span class="dropdown-text">{{ project.name }}</span>
                    <span v-if="project.id === currentProjectId" class="current-badge">Current</span>
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>

          <!-- Tenant Switcher -->
          <div v-if="tenantStore.tenantList.length > 0" class="header-control">
            <el-dropdown @command="handleTenantSwitch" trigger="click">
              <div class="control-trigger">
                <el-icon><OfficeBuilding /></el-icon>
                <span class="control-label">{{ currentTenantName }}</span>
                <el-icon class="control-caret"><ArrowDown /></el-icon>
              </div>
              <template #dropdown>
                <el-dropdown-menu class="precision-dropdown">
                  <el-dropdown-item
                    v-for="tenant in tenantStore.tenantList"
                    :key="tenant.id"
                    :command="tenant.id"
                    :disabled="tenant.id === currentTenantId"
                  >
                    <span class="dropdown-text">{{ tenant.name }}</span>
                    <span v-if="tenant.id === currentTenantId" class="current-badge">Current</span>
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>

          <!-- User Menu -->
          <el-dropdown trigger="click" class="user-control">
            <div class="user-trigger">
              <div class="user-chip">
                <el-icon><User /></el-icon>
              </div>
              <span class="user-label">{{ username }}</span>
            </div>
            <template #dropdown>
              <el-dropdown-menu class="precision-dropdown">
                <el-dropdown-item @click="router.push('/profile')">
                  <el-icon><User /></el-icon>
                  <span class="dropdown-text">{{ t('profile.title') }}</span>
                </el-dropdown-item>
                <el-dropdown-item @click="router.push('/settings')">
                  <el-icon><Setting /></el-icon>
                  <span class="dropdown-text">{{ t('settings.title') }}</span>
                </el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout" class="dropdown-danger">
                  <el-icon><SwitchButton /></el-icon>
                  <span class="dropdown-text">{{ t('common.logout') }}</span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- Page Content -->
      <el-main class="precision-main">
        <div class="page-container">
          <router-view v-slot="{ Component }">
            <transition name="page-transition" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </div>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '@/store'
import { useI18n } from '@/i18n'
import { useTenantStore } from '@/store/tenant'
import { useProjectStore } from '@/store/project'
import { useMenuStore } from '@/store/menu'
import { ElMessage } from 'element-plus'
import {
  Monitor, House, Document, Calendar, CircleClose,
  DataAnalysis, Setting, Expand, Fold, User, OfficeBuilding,
  ArrowDown, FolderOpened, SwitchButton, Connection, Files, Menu, UserFilled, Operation, Bell
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()
const { t } = useI18n()
const tenantStore = useTenantStore()
const projectStore = useProjectStore()
const menuStore = useMenuStore()

// 动态菜单
const menuList = computed(() => menuStore.userMenus)

// 图标映射
const iconMap = {
  House,
  Document,
  Calendar,
  Monitor,
  CircleClose,
  DataAnalysis,
  Setting,
  FolderOpened,
  Connection,
  Files,
  OfficeBuilding,
  Menu,
  User,
  UserFilled,
  Operation,
  Bell
}

// System name
const systemName = ref(t('dashboard.title'))

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
  appStore.isSidebarCollapsed ? '64px' : '220px'
)

const currentTenantId = computed(() => tenantStore.currentTenant?.id)
const currentTenantName = computed(() => tenantStore.currentTenant?.name || t('tenant.switchTenant'))

const currentProjectId = computed(() => projectStore.currentProject?.id)
const currentProjectName = computed(() => projectStore.currentProject?.name || 'Select Project')

const username = computed(() => appStore.user?.real_name || appStore.user?.username || 'User')

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
  } catch (error) {
    ElMessage.error(error.response?.data?.message || 'Switch project failed')
  }
}

function handleLogout() {
  appStore.logout()
  router.push('/login')
}

onMounted(async () => {
  loadSystemName()

  const token = localStorage.getItem('token')
  if (!token) return

  // 从 localStorage 加载用户信息到 store
  if (!appStore.user) {
    const savedUser = localStorage.getItem('user')
    if (savedUser) {
      try {
        appStore.setUser(JSON.parse(savedUser))
      } catch (e) {
        console.error('Load user from localStorage failed:', e)
      }
    }
  }

  // 加载用户菜单
  await menuStore.loadUserMenus()

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

    await projectStore.fetchProjects()
    projectStore.init()
  } catch (error) {
    console.error('Initialize data failed:', error)
  }
})
</script>

<style scoped>
/* ========================================
   PRECISION LAYOUT - Design System v2
   ======================================== */
.precision-layout {
  height: 100vh;
  background: var(--color-bg);
  font-family: var(--font-body);
  overflow: hidden;
}

/* ========================================
   SIDEBAR
   ======================================== */
.precision-sidebar {
  background: var(--sidebar-bg, var(--color-primary));
  border-right: 1px solid var(--sidebar-border, rgba(99, 102, 241, 0.12));
  transition: width 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  position: relative;
}

/* Logo */
.sidebar-logo {
  height: 64px;
  display: flex;
  align-items: center;
  padding: 0 var(--space-5);
  gap: var(--space-3);
  border-bottom: 1px solid rgba(99, 102, 241, 0.12);
  position: relative;
  z-index: 1;
}

.logo-mark {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--color-accent) 0%, #818cf8 100%);
  border-radius: var(--radius-md);
  color: #ffffff;
  flex-shrink: 0;
  box-shadow: 0 2px 12px rgba(99, 102, 241, 0.35);
}

.logo-type {
  font-family: var(--font-display);
  font-size: 16px;
  font-weight: 700;
  color: #ffffff;
  letter-spacing: -0.02em;
  white-space: nowrap;
}

.logo-fade-enter-active,
.logo-fade-leave-active {
  transition: all 0.2s ease;
}

.logo-fade-enter-from,
.logo-fade-leave-to {
  opacity: 0;
  transform: translateX(-8px);
}

/* Menu */
.sidebar-menu {
  flex: 1;
  border: none;
  background: transparent;
  padding: var(--space-3) var(--space-2);
  overflow-y: auto;
  overflow-x: hidden;
  position: relative;
  z-index: 1;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 220px;
}

/* Custom scrollbar */
.sidebar-menu::-webkit-scrollbar {
  width: 4px;
}

.sidebar-menu::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar-menu::-webkit-scrollbar-thumb {
  background: var(--sidebar-scrollbar-bg, rgba(99, 102, 241, 0.2));
  border-radius: 2px;
}

.sidebar-menu::-webkit-scrollbar-thumb:hover {
  background: var(--sidebar-scrollbar-hover, rgba(99, 102, 241, 0.3));
}

/* Nav Items */
:deep(.nav-item) {
  margin-bottom: 2px;
  border-radius: var(--radius-md);
  height: 40px;
  line-height: 40px;
  color: var(--sidebar-item-color, rgba(255, 255, 255, 0.6));
  transition: all 0.15s ease;
  position: relative;
}

:deep(.nav-item::before) {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 2px;
  height: 0;
  background: var(--color-accent);
  border-radius: 1px;
  transition: height 0.15s ease;
}

:deep(.nav-item:hover) {
  background: var(--sidebar-item-hover-bg, rgba(255, 255, 255, 0.06));
  color: var(--sidebar-item-hover-color, rgba(255, 255, 255, 0.9));
}

:deep(.nav-item.is-active) {
  background: var(--sidebar-item-active-bg, linear-gradient(90deg, rgba(99, 102, 241, 0.16) 0%, transparent 100%));
  color: var(--sidebar-item-active-color, #ffffff);
  font-weight: 600;
}

:deep(.nav-item.is-active::before) {
  height: 20px;
}

:deep(.nav-item .el-icon) {
  font-size: 16px;
  margin-right: 10px;
}

:deep(.el-menu--collapse .nav-item) {
  padding: 0;
  justify-content: center;
}

:deep(.el-menu--collapse .nav-item .el-icon) {
  margin-right: 0;
}

:deep(.el-menu--collapse .nav-item span) {
  display: none;
}

/* Sub Menu Styles */
:deep(.el-sub-menu) {
  margin-bottom: 2px;
}

:deep(.el-sub-menu__title) {
  height: 40px;
  line-height: 40px;
  color: var(--sidebar-item-color, rgba(255, 255, 255, 0.6));
  border-radius: var(--radius-md);
  transition: all 0.15s ease;
}

:deep(.el-sub-menu__title:hover) {
  background: var(--sidebar-item-hover-bg, rgba(255, 255, 255, 0.06));
  color: var(--sidebar-item-hover-color, rgba(255, 255, 255, 0.9));
}

:deep(.el-sub-menu.is-opened > .el-sub-menu__title) {
  color: var(--sidebar-item-active-color, #ffffff);
  font-weight: 600;
}

/* 内嵌子菜单样式（非弹出） */
:deep(.el-sub-menu .el-menu) {
  background: transparent;
}

:deep(.el-sub-menu .el-menu-item) {
  height: 36px;
  line-height: 36px;
  padding-left: 52px !important;
  color: var(--sidebar-sub-item-color, rgba(255, 255, 255, 0.6));
  background: transparent;
  margin: 0 8px;
  border-radius: var(--radius-sm);
}

:deep(.el-sub-menu .el-menu-item:hover) {
  background: var(--sidebar-item-hover-bg, rgba(255, 255, 255, 0.08));
  color: var(--sidebar-sub-item-hover-color, rgba(255, 255, 255, 0.85));
}

:deep(.el-sub-menu .el-menu-item.is-active) {
  background: var(--sidebar-item-active-bg, rgba(99, 102, 241, 0.2));
  color: #ffffff;
}

/* 子菜单箭头 */
:deep(.el-sub-menu__icon-arrow) {
  color: var(--sidebar-item-color, rgba(255, 255, 255, 0.5));
  transition: transform 0.3s;
}

:deep(.el-sub-menu.is-opened > .el-sub-menu__title .el-sub-menu__icon-arrow) {
  transform: rotate(180deg);
}

/* 折叠状态下隐藏嵌套菜单 */
:deep(.el-menu--collapse .el-sub-menu .el-menu) {
  display: none;
}

/* Sidebar Footer */
.sidebar-footer {
  padding: var(--space-4) var(--space-5);
  border-top: 1px solid var(--sidebar-footer-border, rgba(99, 102, 241, 0.12));
  position: relative;
  z-index: 1;
}

.footer-badge {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.badge-label {
  font-family: var(--font-display);
  font-size: 10px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.4);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.badge-version {
  font-family: var(--font-display);
  font-size: 10px;
  color: rgba(255, 255, 255, 0.25);
}

/* ========================================
   CONTENT WRAPPER
   ======================================== */
.content-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* ========================================
   HEADER
   ======================================== */
.precision-header {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-6);
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  position: relative;
  z-index: 10;
}

.header-section {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.header-left {
  gap: var(--space-4);
}

.header-right {
  gap: var(--space-2);
}

/* Icon Button */
.icon-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  color: var(--color-text-secondary);
  transition: all 0.15s ease;
}

.icon-btn:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
  background: rgba(99, 102, 241, 0.06);
}

/* Breadcrumb */
.breadcrumb-nav :deep(.el-breadcrumb) {
  font-family: var(--font-display);
  font-size: 13px;
}

.breadcrumb-nav :deep(.el-breadcrumb__inner) {
  color: var(--color-text-secondary);
  font-weight: 500;
  transition: color 0.15s ease;
}

.breadcrumb-nav :deep(.el-breadcrumb__inner:hover) {
  color: var(--color-accent);
}

.breadcrumb-nav :deep(.el-breadcrumb__separator) {
  color: var(--color-text-muted);
  margin: 0 var(--space-2);
}

.breadcrumb-nav :deep(.el-breadcrumb__item:last-child .el-breadcrumb__inner) {
  color: var(--color-text);
  font-weight: 600;
}

/* Header Controls */
.header-control {
  display: flex;
  align-items: center;
}

.control-trigger {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  border-radius: 0;
  color: var(--color-text);
  cursor: pointer;
  transition: background var(--transition-fast);
  font-size: var(--text-sm);
}

.control-trigger:hover {
  background: var(--color-bg-alt);
}

.control-trigger .el-icon:first-child {
  color: var(--color-text);
  font-size: var(--text-md);
}

.control-label {
  font-family: var(--font-display);
  font-weight: 500;
  color: var(--color-text);
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.control-caret {
  font-size: var(--text-xs);
  color: var(--color-text);
  transition: transform var(--transition-fast);
}

/* User Control */
.user-control {
  display: flex;
  align-items: center;
}

.user-trigger {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: 4px 10px;
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: background 0.15s ease;
}

.user-trigger:hover {
  background: var(--color-bg-alt);
}

.user-chip {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-light) 100%);
  border-radius: var(--radius-md);
  color: #ffffff;
  font-size: 14px;
}

.user-label {
  font-family: var(--font-display);
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text);
}

/* ========================================
   DROPDOWN
   ======================================== */
.precision-dropdown {
  border: 1px solid var(--color-border) !important;
  border-radius: 0;
  padding: var(--space-2);
  background: var(--color-surface);
  box-shadow: none;
  min-width: 180px;
}

/* 针对 Element Plus popper 容器 */
:deep(.el-dropdown__popper),
:deep(.el-select__popper) {
  border: 1px solid var(--color-border) !important;
}

:deep(.el-popper) {
  border: 1px solid var(--color-border) !important;
}

/* 移除 popper 的白色背景 */
:deep(.el-popper.is-light),
:deep(.el-dropdown__popper.is-light),
:deep(.el-select__popper.is-light) {
  background: var(--color-surface) !important;
  box-shadow: none !important;
}

/* 确保下拉菜单有正确的背景和阴影 */
:deep(.el-popper.is-light .el-dropdown-menu),
:deep(.el-dropdown__popper.is-light .el-dropdown-menu) {
  background: var(--color-surface) !important;
  box-shadow: none !important;
  border-radius: 0 !important;
}

:deep(.precision-dropdown .el-dropdown-menu__item) {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: 8px 10px;
  border-radius: 0;
  font-family: var(--font-body);
  font-size: 13px;
  color: var(--color-text);
  transition: all 0.15s ease;
}

:deep(.precision-dropdown .el-dropdown-menu__item:hover) {
  background: var(--color-bg-alt);
  color: var(--color-accent);
}

:deep(.precision-dropdown .el-dropdown-menu__item.is-disabled) {
  opacity: 0.5;
  cursor: not-allowed;
}

:deep(.precision-dropdown .el-dropdown-menu__item .el-icon) {
  font-size: 15px;
  color: var(--color-text-secondary);
}

.project-indicator {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0;
  color: #ffffff;
  font-family: var(--font-display);
  font-size: 10px;
  font-weight: 600;
  flex-shrink: 0;
}

.indicator-text {
  font-size: 9px;
}

.dropdown-text {
  flex: 1;
  font-weight: 500;
}

.current-badge {
  padding: 2px 8px;
  background: rgba(34, 197, 94, 0.12);
  color: var(--color-success);
  font-family: var(--font-display);
  font-size: 10px;
  font-weight: 600;
  border-radius: 0;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.dropdown-danger {
  color: var(--color-error);
}

.dropdown-danger:hover {
  background: rgba(239, 68, 68, 0.08) !important;
  color: var(--color-error) !important;
}

/* ========================================
   MAIN CONTENT
   ======================================== */
.precision-main {
  flex: 1;
  overflow: hidden;
  background: var(--color-bg);
}

.page-container {
  height: 100%;
  overflow-y: auto;
  padding: 0;
}

.page-container > * {
  position: relative;
  z-index: 1;
}

/* Custom scrollbar */
.page-container::-webkit-scrollbar {
  width: 8px;
}

.page-container::-webkit-scrollbar-track {
  background: transparent;
}

.page-container::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: 0;
  transition: background 0.15s ease;
}

.page-container::-webkit-scrollbar-thumb:hover {
  background: var(--color-text-muted);
}

/* ========================================
   PAGE TRANSITIONS
   ======================================== */
.page-transition-enter-active,
.page-transition-leave-active {
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.page-transition-enter-from {
  opacity: 0;
  transform: translateY(8px);
}

.page-transition-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* ========================================
   RESPONSIVE
   ======================================== */
@media (max-width: 768px) {
  .precision-header {
    padding: 0 var(--space-4);
  }

  .page-container {
    padding: var(--space-4);
  }

  .control-label {
    display: none;
  }

  .user-label {
    display: none;
  }
}
</style>

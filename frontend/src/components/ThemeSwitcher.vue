<template>
  <el-dropdown trigger="click" @command="handleThemeChange">
    <div class="theme-switcher">
      <el-icon><Brush /></el-icon>
      <span class="theme-name">{{ currentTheme?.name || '主题' }}</span>
      <el-icon class="dropdown-arrow"><ArrowDown /></el-icon>
    </div>
    <template #dropdown>
      <el-dropdown-menu class="theme-dropdown-menu">
        <div class="theme-menu-header">
          <span>选择配色方案</span>
        </div>
        <div class="theme-list">
          <div
            v-for="theme in themes"
            :key="theme.id"
            :class="['theme-item', { active: themeId === theme.id }]"
            @click="handleThemeChange(theme.id)"
          >
            <div class="theme-preview">
              <div
                class="theme-color-circle"
                :style="{ backgroundColor: theme.colors.accent }"
              ></div>
              <div class="theme-colors">
                <span
                  v-for="(color, idx) in getThemeColors(theme)"
                  :key="idx"
                  class="theme-color-dot"
                  :style="{ backgroundColor: color }"
                ></span>
              </div>
            </div>
            <div class="theme-info">
              <span class="theme-label">{{ theme.name }}</span>
              <span class="theme-label-en">{{ theme.nameEn }}</span>
            </div>
            <el-icon v-if="themeId === theme.id" class="theme-check" color="#409eff">
              <Check />
            </el-icon>
          </div>
        </div>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Brush, ArrowDown, Check } from '@element-plus/icons-vue'
import { themes, getCurrentTheme, setTheme } from '@/composables/useTheme'

const themeId = ref(getCurrentTheme().id)
const currentTheme = computed(() => themes[themeId.value])

// 获取主题预览颜色
function getThemeColors(theme) {
  return [
    theme.colors.accent,
    theme.colors.success,
    theme.colors.warning,
    theme.colors.error
  ]
}

// 切换主题
function handleThemeChange(id) {
  if (id === themeId.value) return
  themeId.value = id
  setTheme(id)
}

onMounted(() => {
  // 监听主题变更
  window.addEventListener('theme-changed', (event) => {
    themeId.value = event.detail.themeId
  })
})
</script>

<style scoped>
.theme-switcher {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  cursor: pointer;
  border-radius: 0;
  transition: background var(--transition-fast);
  font-size: var(--text-sm);
  color: var(--color-text);
}

.theme-switcher:hover {
  background: var(--color-bg-alt);
}

.theme-name {
  font-size: var(--text-sm);
}

.dropdown-arrow {
  font-size: var(--text-xs);
  transition: transform var(--transition-fast);
}
</style>

<style>
/* 全局样式：用于下拉菜单（因为 Element Plus 使用 Teleport） */
.theme-dropdown-menu {
  background: var(--color-surface) !important;
  border: none !important;
}

/* Element Plus popper 容器 */
.el-dropdown__popper.theme-dropdown-menu,
.el-popper.is-light.theme-dropdown-menu {
  border: none !important;
  background: transparent !important;
  box-shadow: none !important;
}

/* 确保下拉菜单有正确的背景 */
.el-dropdown__popper.theme-dropdown-menu .theme-dropdown-menu,
.el-popper.is-light.theme-dropdown-menu .theme-dropdown-menu {
  background: var(--color-surface) !important;
  box-shadow: none !important;
  border-radius: 0 !important;
}

.theme-dropdown-menu .theme-menu-header {
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--color-border-light);
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text);
}

.theme-dropdown-menu .theme-list {
  padding: var(--space-2);
  max-height: 320px;
  overflow-y: auto;
}

.theme-dropdown-menu .theme-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: 10px var(--space-3);
  border-radius: 0;
  cursor: pointer;
  transition: background var(--transition-fast);
  margin-bottom: var(--space-1);
}

.theme-dropdown-menu .theme-item:hover {
  background: var(--color-bg-alt);
}

.theme-dropdown-menu .theme-item.active {
  background: var(--color-accent-light);
}

.theme-dropdown-menu .theme-preview {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  flex-shrink: 0;
}

.theme-dropdown-menu .theme-color-circle {
  width: 24px;
  height: 24px;
  border-radius: 0;
  border: 2px solid var(--color-border-light);
}

.theme-dropdown-menu .theme-colors {
  display: flex;
  gap: var(--space-1);
}

.theme-dropdown-menu .theme-color-dot {
  width: 12px;
  height: 12px;
  border-radius: 0;
  border: 1px solid var(--color-border-light);
}

.theme-dropdown-menu .theme-info {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  flex: 1;
}

.theme-dropdown-menu .theme-label {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text);
}

.theme-dropdown-menu .theme-label-en {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

.theme-dropdown-menu .theme-check {
  flex-shrink: 0;
}

/* 滚动条样式 */
.theme-dropdown-menu .theme-list::-webkit-scrollbar {
  width: 4px;
}

.theme-dropdown-menu .theme-list::-webkit-scrollbar-track {
  background: transparent;
}

.theme-dropdown-menu .theme-list::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: 0;
}

.theme-dropdown-menu .theme-list::-webkit-scrollbar-thumb:hover {
  background: var(--color-text-muted);
}
</style>

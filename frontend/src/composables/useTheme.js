import { ref } from 'vue'

/**
 * Theme System
 * 主题管理系统 - 支持多套配色方案切换
 */

// 主题配色方案
export const themes = {
  // 亮色主题 (默认)
  light: {
    id: 'light',
    name: '亮色主题',
    nameEn: 'Light Theme',
    colors: {
      // 背景色
      bg: '#f8f9fa',
      surface: '#ffffff',
      surfaceAlt: '#f1f3f5',
      bgAlt: '#f1f3f5',
      bgHover: '#e9ecef',

      // 文字色
      text: '#212529',
      textSecondary: '#495057',
      textMuted: '#868e96',
      textLight: '#adb5bd',

      // 强调色
      accent: '#228be6',
      accentHover: '#1c7ed6',
      accentLight: 'rgba(34, 139, 230, 0.1)',
      accentLighter: 'rgba(34, 139, 230, 0.05)',

      // 语义色
      success: '#40c057',
      successLight: 'rgba(64, 192, 87, 0.1)',
      warning: '#fab005',
      warningLight: 'rgba(250, 176, 5, 0.1)',
      error: '#fa5252',
      errorLight: 'rgba(250, 82, 82, 0.1)',
      info: '#15aabf',
      infoLight: 'rgba(21, 170, 191, 0.1)',

      // 边框
      border: '#dee2e6',
      borderLight: '#e9ecef',
      borderHover: '#adb5bd',

      // 主色
      primary: '#1971c2'
    },
    sidebar: {
      bg: '#0f172a',
      border: 'rgba(99, 102, 241, 0.12)',
      footerBorder: 'rgba(99, 102, 241, 0.12)',
      itemColor: 'rgba(255, 255, 255, 0.6)',
      itemHoverBg: 'rgba(255, 255, 255, 0.06)',
      itemHoverColor: 'rgba(255, 255, 255, 0.9)',
      itemActiveBg: 'linear-gradient(90deg, rgba(99, 102, 241, 0.16) 0%, transparent 100%)',
      itemActiveColor: '#ffffff',
      scrollbarBg: 'rgba(99, 102, 241, 0.2)',
      scrollbarHover: 'rgba(99, 102, 241, 0.3)'
    }
  },

  // 蓝色主题
  blue: {
    id: 'blue',
    name: '蓝色主题',
    nameEn: 'Blue Theme',
    colors: {
      bg: '#f0f4f8',
      surface: '#ffffff',
      surfaceAlt: '#e1e8f0',
      bgAlt: '#e1e8f0',
      bgHover: '#d3dbe5',

      text: '#1a202c',
      textSecondary: '#2d3748',
      textMuted: '#718096',
      textLight: '#a0aec0',

      accent: '#3182ce',
      accentHover: '#2b6cb0',
      accentLight: 'rgba(49, 130, 206, 0.1)',
      accentLighter: 'rgba(49, 130, 206, 0.05)',

      success: '#48bb78',
      successLight: 'rgba(72, 187, 120, 0.1)',
      warning: '#ecc94b',
      warningLight: 'rgba(236, 201, 75, 0.1)',
      error: '#f56565',
      errorLight: 'rgba(245, 101, 101, 0.1)',
      info: '#4299e1',
      infoLight: 'rgba(66, 153, 225, 0.1)',

      border: '#e2e8f0',
      borderLight: '#edf2f7',
      borderHover: '#cbd5e0',

      primary: '#2c5282'
    },
    sidebar: {
      bg: '#1e3a8a',
      border: 'rgba(49, 130, 206, 0.15)',
      footerBorder: 'rgba(49, 130, 206, 0.15)',
      itemColor: 'rgba(255, 255, 255, 0.6)',
      itemHoverBg: 'rgba(255, 255, 255, 0.08)',
      itemHoverColor: 'rgba(255, 255, 255, 0.9)',
      itemActiveBg: 'linear-gradient(90deg, rgba(49, 130, 206, 0.2) 0%, transparent 100%)',
      itemActiveColor: '#ffffff',
      scrollbarBg: 'rgba(49, 130, 206, 0.25)',
      scrollbarHover: 'rgba(49, 130, 206, 0.35)'
    }
  },

  // 绿色主题
  green: {
    id: 'green',
    name: '绿色主题',
    nameEn: 'Green Theme',
    colors: {
      bg: '#f0fdf4',
      surface: '#ffffff',
      surfaceAlt: '#dcfce7',
      bgAlt: '#dcfce7',
      bgHover: '#bbf7d0',

      text: '#14532d',
      textSecondary: '#166534',
      textMuted: '#65a30d',
      textLight: '#84cc16',

      accent: '#22c55e',
      accentHover: '#16a34a',
      accentLight: 'rgba(34, 197, 94, 0.1)',
      accentLighter: 'rgba(34, 197, 94, 0.05)',

      success: '#22c55e',
      successLight: 'rgba(34, 197, 94, 0.1)',
      warning: '#f59e0b',
      warningLight: 'rgba(245, 158, 11, 0.1)',
      error: '#ef4444',
      errorLight: 'rgba(239, 68, 68, 0.1)',
      info: '#06b6d4',
      infoLight: 'rgba(6, 182, 212, 0.1)',

      border: '#bbf7d0',
      borderLight: '#dcfce7',
      borderHover: '#86efac',

      primary: '#15803d'
    },
    sidebar: {
      bg: '#14532d',
      border: 'rgba(34, 197, 94, 0.2)',
      footerBorder: 'rgba(34, 197, 94, 0.2)',
      itemColor: 'rgba(255, 255, 255, 0.65)',
      itemHoverBg: 'rgba(255, 255, 255, 0.08)',
      itemHoverColor: 'rgba(255, 255, 255, 0.9)',
      itemActiveBg: 'linear-gradient(90deg, rgba(34, 197, 94, 0.2) 0%, transparent 100%)',
      itemActiveColor: '#ffffff',
      scrollbarBg: 'rgba(34, 197, 94, 0.25)',
      scrollbarHover: 'rgba(34, 197, 94, 0.35)'
    }
  },

  // 紫色主题
  purple: {
    id: 'purple',
    name: '紫色主题',
    nameEn: 'Purple Theme',
    colors: {
      bg: '#faf5ff',
      surface: '#ffffff',
      surfaceAlt: '#f3e8ff',
      bgAlt: '#f3e8ff',
      bgHover: '#e9d5ff',

      text: '#1a0b2e',
      textSecondary: '#2d1b4e',
      textMuted: '#7c3aed',
      textLight: '#a78bfa',

      accent: '#8b5cf6',
      accentHover: '#7c3aed',
      accentLight: 'rgba(139, 92, 246, 0.1)',
      accentLighter: 'rgba(139, 92, 246, 0.05)',

      success: '#10b981',
      successLight: 'rgba(16, 185, 129, 0.1)',
      warning: '#f59e0b',
      warningLight: 'rgba(245, 158, 11, 0.1)',
      error: '#ef4444',
      errorLight: 'rgba(239, 68, 68, 0.1)',
      info: '#3b82f6',
      infoLight: 'rgba(59, 130, 246, 0.1)',

      border: '#e9d5ff',
      borderLight: '#f3e8ff',
      borderHover: '#d8b4fe',

      primary: '#6d28d9'
    },
    sidebar: {
      bg: '#581c87',
      border: 'rgba(139, 92, 246, 0.2)',
      footerBorder: 'rgba(139, 92, 246, 0.2)',
      itemColor: 'rgba(255, 255, 255, 0.65)',
      itemHoverBg: 'rgba(255, 255, 255, 0.08)',
      itemHoverColor: 'rgba(255, 255, 255, 0.9)',
      itemActiveBg: 'linear-gradient(90deg, rgba(139, 92, 246, 0.2) 0%, transparent 100%)',
      itemActiveColor: '#ffffff',
      scrollbarBg: 'rgba(139, 92, 246, 0.25)',
      scrollbarHover: 'rgba(139, 92, 246, 0.35)'
    }
  },

  // 暗色主题
  dark: {
    id: 'dark',
    name: '暗色主题',
    nameEn: 'Dark Theme',
    colors: {
      bg: '#1a1a1a',
      surface: '#2d2d2d',
      surfaceAlt: '#3a3a3a',
      bgAlt: '#3a3a3a',
      bgHover: '#4a4a4a',

      text: '#e5e5e5',
      textSecondary: '#cccccc',
      textMuted: '#999999',
      textLight: '#666666',

      accent: '#3b82f6',
      accentHover: '#2563eb',
      accentLight: 'rgba(59, 130, 246, 0.15)',
      accentLighter: 'rgba(59, 130, 246, 0.08)',

      success: '#22c55e',
      successLight: 'rgba(34, 197, 94, 0.15)',
      warning: '#f59e0b',
      warningLight: 'rgba(245, 158, 11, 0.15)',
      error: '#ef4444',
      errorLight: 'rgba(239, 68, 68, 0.15)',
      info: '#06b6d4',
      infoLight: 'rgba(6, 182, 212, 0.15)',

      border: '#404040',
      borderLight: '#4a4a4a',
      borderHover: '#606060',

      primary: '#60a5fa'
    },
    sidebar: {
      bg: '#0d0d0d',
      border: 'rgba(255, 255, 255, 0.08)',
      footerBorder: 'rgba(255, 255, 255, 0.08)',
      itemColor: 'rgba(229, 229, 229, 0.6)',
      itemHoverBg: 'rgba(255, 255, 255, 0.05)',
      itemHoverColor: 'rgba(229, 229, 229, 0.9)',
      itemActiveBg: 'linear-gradient(90deg, rgba(59, 130, 246, 0.15) 0%, transparent 100%)',
      itemActiveColor: '#ffffff',
      scrollbarBg: 'rgba(59, 130, 246, 0.15)',
      scrollbarHover: 'rgba(59, 130, 246, 0.25)'
    }
  }
}

// 主题存储键
const THEME_STORAGE_KEY = 'app-theme'

/**
 * 获取当前主题
 */
export function getCurrentTheme() {
  const themeId = localStorage.getItem(THEME_STORAGE_KEY) || 'light'
  return themes[themeId] || themes.light
}

/**
 * 设置主题
 * @param {string} themeId - 主题ID
 */
export function setTheme(themeId) {
  const theme = themes[themeId]
  if (!theme) {
    console.warn(`Theme "${themeId}" not found`)
    return
  }

  // 保存到本地存储
  localStorage.setItem(THEME_STORAGE_KEY, themeId)

  // 应用主题样式
  applyTheme(theme)

  // 触发主题变更事件
  window.dispatchEvent(new CustomEvent('theme-changed', { detail: { themeId, theme } }))
}

/**
 * 应用主题样式到 CSS 变量
 * @param {Object} theme - 主题对象
 */
function applyTheme(theme) {
  const root = document.documentElement
  const { colors } = theme

  // 设置 data-theme 属性用于暗色主题样式覆盖
  if (theme.id === 'dark') {
    root.setAttribute('data-theme', 'dark')
  } else {
    root.removeAttribute('data-theme')
  }

  // 设置颜色变量
  root.style.setProperty('--color-bg', colors.bg)
  root.style.setProperty('--color-surface', colors.surface)
  root.style.setProperty('--color-surface-alt', colors.surfaceAlt)
  root.style.setProperty('--color-bg-alt', colors.bgAlt)
  root.style.setProperty('--color-bg-hover', colors.bgHover)

  root.style.setProperty('--color-text', colors.text)
  root.style.setProperty('--color-text-secondary', colors.textSecondary)
  root.style.setProperty('--color-text-muted', colors.textMuted)
  root.style.setProperty('--color-text-light', colors.textLight)

  root.style.setProperty('--color-accent', colors.accent)
  root.style.setProperty('--color-accent-hover', colors.accentHover)
  root.style.setProperty('--color-accent-light', colors.accentLight)
  root.style.setProperty('--color-accent-lighter', colors.accentLighter)

  root.style.setProperty('--color-success', colors.success)
  root.style.setProperty('--color-success-light', colors.successLight)
  root.style.setProperty('--color-warning', colors.warning)
  root.style.setProperty('--color-warning-light', colors.warningLight)
  root.style.setProperty('--color-error', colors.error)
  root.style.setProperty('--color-error-light', colors.errorLight)
  root.style.setProperty('--color-info', colors.info)
  root.style.setProperty('--color-info-light', colors.infoLight)

  root.style.setProperty('--color-border', colors.border)
  root.style.setProperty('--color-border-light', colors.borderLight)
  root.style.setProperty('--color-border-hover', colors.borderHover)

  root.style.setProperty('--color-primary', colors.primary)

  // 设置侧边栏颜色变量
  if (theme.sidebar) {
    root.style.setProperty('--sidebar-bg', theme.sidebar.bg)
    root.style.setProperty('--sidebar-border', theme.sidebar.border || 'rgba(99, 102, 241, 0.12)')
    root.style.setProperty('--sidebar-footer-border', theme.sidebar.footerBorder || theme.sidebar.border || 'rgba(99, 102, 241, 0.12)')
    root.style.setProperty('--sidebar-item-color', theme.sidebar.itemColor)
    root.style.setProperty('--sidebar-item-hover-bg', theme.sidebar.itemHoverBg)
    root.style.setProperty('--sidebar-item-hover-color', theme.sidebar.itemHoverColor)
    root.style.setProperty('--sidebar-item-active-bg', theme.sidebar.itemActiveBg)
    root.style.setProperty('--sidebar-item-active-color', theme.sidebar.itemActiveColor)
    root.style.setProperty('--sidebar-scrollbar-bg', theme.sidebar.scrollbarBg)
    root.style.setProperty('--sidebar-scrollbar-hover', theme.sidebar.scrollbarHover)
  }
}

/**
 * 初始化主题
 */
export function initTheme() {
  const theme = getCurrentTheme()
  applyTheme(theme)
  return theme
}

/**
 * 获取所有主题列表
 */
export function getThemeList() {
  return Object.values(themes)
}

/**
 * Vue Composable
 */
export function useTheme() {
  const currentTheme = ref(getCurrentTheme())
  const themeId = ref(currentTheme.value.id)

  // 监听主题变更
  const handleThemeChange = (event) => {
    currentTheme.value = event.detail.theme
    themeId.value = event.detail.themeId
  }

  // 组件挂载时添加监听
  if (typeof window !== 'undefined') {
    window.addEventListener('theme-changed', handleThemeChange)
  }

  const changeTheme = (id) => {
    setTheme(id)
    themeId.value = id
    currentTheme.value = themes[id]
  }

  return {
    themeId,
    currentTheme,
    themes: getThemeList(),
    changeTheme,
    setTheme
  }
}

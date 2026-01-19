import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

// Import Design System v3 - Dynamic Theme Support
import './styles/design-system-v3.css'
import './styles/element-plus-overrides.css'
import './styles/dark-theme-overrides.css'
import './styles/page-layout.css'

// Import Theme System
import { initTheme } from './composables/useTheme'

import App from './App.vue'
import router from './router'

const app = createApp(App)
const pinia = createPinia()

// Initialize theme system
initTheme()

// Register all icons
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(pinia)
app.use(router)
app.use(ElementPlus, {
  locale: zhCn,
  size: 'default',
  zIndex: 3000
})

app.mount('#app')

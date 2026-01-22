<template>
  <div class="settings-page animate-fade-in-up">
    <el-card>
      <el-tabs v-model="activeTab" class="settings-tabs">
        <!-- 基本设置 -->
        <el-tab-pane :label="t('settings.basic')" name="basic">
          <el-form :model="basicForm" label-width="120px" style="max-width: 600px">
            <el-form-item :label="t('settings.systemName')">
              <el-input v-model="basicForm.systemName" />
            </el-form-item>
            <el-form-item :label="t('settings.defaultProject')">
              <el-select v-model="basicForm.defaultProject" :placeholder="t('settings.defaultProject')" style="width: 100%">
                <el-option label="Project A" value="1" />
                <el-option label="Project B" value="2" />
              </el-select>
            </el-form-item>
            <el-form-item :label="t('settings.language')">
              <el-select v-model="basicForm.language" style="width: 100%" @change="handleLanguageChange">
                <el-option label="简体中文" value="zh-CN" />
                <el-option label="English" value="en-US" />
              </el-select>
            </el-form-item>
            <el-form-item :label="t('settings.timezone')">
              <el-select v-model="basicForm.timezone" style="width: 100%">
                <el-option label="Asia/Shanghai (UTC+8)" value="Asia/Shanghai" />
                <el-option label="America/New_York (UTC-5)" value="America/New_York" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleSaveBasic">{{ t('common.save') }}</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane :label="t('settings.about')" name="about">
          <el-descriptions :title="t('settings.sysInfo')" :column="1" border>
            <el-descriptions-item :label="t('settings.platformName')">TestP 测试管理平台</el-descriptions-item>
            <el-descriptions-item :label="t('settings.sysVersion')">v1.0.0</el-descriptions-item>
            <el-descriptions-item :label="t('settings.frontendStack')">Vue 3 + Element Plus</el-descriptions-item>
            <el-descriptions-item :label="t('settings.backendStack')">Flask + SQLAlchemy</el-descriptions-item>
            <el-descriptions-item :label="t('settings.license')">MIT License</el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useI18n } from '@/i18n'

const { t, locale } = useI18n()
const activeTab = ref('basic')

const basicForm = reactive({
  systemName: 'TestP Platform',
  defaultProject: '',
  language: 'zh-CN',
  timezone: 'Asia/Shanghai'
})

function loadSettings() {
  const savedSettings = localStorage.getItem('systemSettings')
  if (savedSettings) {
    try {
      const settings = JSON.parse(savedSettings)
      Object.assign(basicForm, settings)
    } catch (e) {
      console.error('Load settings failed:', e)
    }
  }
}

function handleLanguageChange() {
  // 语言切换处理
}

function handleSaveBasic() {
  const settings = {
    systemName: basicForm.systemName,
    defaultProject: basicForm.defaultProject,
    language: basicForm.language,
    timezone: basicForm.timezone
  }
  localStorage.setItem('systemSettings', JSON.stringify(settings))
  ElMessage.success(t('settings.saveSuccess'))
}

onMounted(() => {
  loadSettings()
})
</script>

<style scoped>
.settings-page {
  padding: var(--space-6);
  height: 100%;
  overflow-y: auto;
}

.settings-page :deep(.el-card) {
  background: var(--color-surface);
  border: none;
  border-radius: var(--radius-lg);
  box-shadow: none;
}

.settings-page :deep(.el-card__body) {
  padding: var(--space-5);
}

.settings-tabs :deep(.el-tabs__content) {
  padding-top: var(--space-5);
}
</style>

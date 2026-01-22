<template>
  <div class="settings-page animate-fade-in-up">
    <!-- Page Header -->
    <div class="page-header">
      <h1 class="page-title">OAuth认证</h1>
      <p class="page-description">配置第三方登录认证方式</p>
    </div>

    <!-- OAuth Providers -->
    <div class="oauth-providers">
      <div v-for="provider in oauthProviders" :key="provider.code" class="provider-card">
        <div class="provider-header">
          <div class="provider-info">
            <div class="provider-icon" :class="`provider-${provider.code}`">
              <svg v-if="provider.code === 'github'" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
              </svg>
              <svg v-else-if="provider.code === 'gitee'" viewBox="0 0 24 24" fill="currentColor">
                <path d="M11.984 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.016 0zm6.09 5.333c.328 0 .593.266.592.593v1.482a.594.594 0 0 1-.593.592H9.777c-.982 0-1.778.796-1.778 1.778v5.63c0 .327.266.592.593.592h5.63c.982 0 1.778-.796 1.778-1.778v-.296a.593.593 0 0 0-.592-.593h-4.037a.594.594 0 0 1-.592-.593v-1.482a.593.593 0 0 1 .593-.592h6.815c.327 0 .593.265.593.592v3.408a4 4 0 0 1-4 4H5.926a.593.593 0 0 1-.593-.593V9.778a4.444 4.444 0 0 1 4.445-4.444h8.296z"/>
              </svg>
              <svg v-else-if="provider.code === 'gitlab'" viewBox="0 0 24 24" fill="currentColor">
                <path d="M22.65 14.39L12 22.13 1.35 14.39a.84.84 0 0 1-.3-.94l1.22-3.78 2.44-7.51A.42.42 0 0 1 4.82 2a.43.43 0 0 1 .41.26l2.47 7.6h8.6l2.47-7.6A.43.43 0 0 1 18.77 2a.42.42 0 0 1 .41.16l2.44 7.51 1.22 3.78a.84.84 0 0 1-.3.94z"/>
              </svg>
              <svg v-else-if="provider.code === 'dingtalk'" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
              </svg>
              <el-icon v-else><Connection /></el-icon>
            </div>
            <div>
              <h3 class="provider-name">{{ provider.name }}</h3>
              <p class="provider-desc">{{ provider.description }}</p>
            </div>
          </div>
          <el-switch
            v-model="provider.enabled"
            @change="handleToggleProvider(provider)"
            :loading="provider.loading"
          />
        </div>

        <el-collapse-transition>
          <div v-show="provider.enabled" class="provider-config">
            <el-form :model="provider.config" label-width="120px" label-position="left">
              <el-form-item :label="`${provider.name} Client ID`">
                <el-input v-model="provider.config.clientId" placeholder="请输入Client ID" />
              </el-form-item>
              <el-form-item :label="`${provider.name} Client Secret`">
                <el-input v-model="provider.config.clientSecret" type="password" placeholder="请输入Client Secret" show-password />
              </el-form-item>
              <el-form-item label="回调地址">
                <el-input :model-value="getCallbackUrl(provider.code)" disabled>
                  <template #append>
                    <el-button :icon="CopyDocument" @click="copyCallbackUrl(provider.code)" />
                  </template>
                </el-input>
              </el-form-item>
              <el-form-item label="授权范围">
                <el-select v-model="provider.config.scope" multiple placeholder="选择授权范围" style="width: 100%">
                  <el-option v-for="scope in provider.scopes" :key="scope.value" :label="scope.label" :value="scope.value" />
                </el-select>
              </el-form-item>
            </el-form>
            <div class="provider-actions">
              <el-button type="primary" @click="handleSaveProvider(provider)" :loading="provider.saving">
                保存配置
              </el-button>
              <el-button @click="handleTestProvider(provider)" :loading="provider.testing">
                测试连接
              </el-button>
            </div>
          </div>
        </el-collapse-transition>
      </div>
    </div>

    <!-- Instructions Card -->
    <div class="instructions-card">
      <h3 class="instructions-title">配置说明</h3>
      <div class="instructions-content">
        <h4>GitHub OAuth 配置</h4>
        <ol>
          <li>访问 GitHub Settings > Developer settings > OAuth Apps</li>
          <li>点击 "New OAuth App" 创建应用</li>
          <li>填写应用信息，Homepage URL 和 Authorization callback URL 使用上方回调地址</li>
          <li>创建后复制 Client ID 和生成 Client Secret</li>
        </ol>
        <h4>Gitee OAuth 配置</h4>
        <ol>
          <li>访问 Gitee 设置 > 第三方应用 > 创建应用</li>
          <li>填写应用信息，回调地址使用上方回调地址</li>
          <li>创建后复制 Client ID 和 Client Secret</li>
        </ol>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Connection, CopyDocument } from '@element-plus/icons-vue'

const baseUrl = window.location.origin

const oauthProviders = ref([
  {
    code: 'github',
    name: 'GitHub',
    description: '使用 GitHub 账号登录',
    enabled: false,
    loading: false,
    saving: false,
    testing: false,
    scopes: [
      { label: '读取用户信息', value: 'read:user' },
      { label: '读取邮箱', value: 'user:email' }
    ],
    config: {
      clientId: '',
      clientSecret: '',
      scope: ['read:user', 'user:email']
    }
  },
  {
    code: 'gitee',
    name: 'Gitee',
    description: '使用 Gitee 账号登录',
    enabled: false,
    loading: false,
    saving: false,
    testing: false,
    scopes: [
      { label: '读取用户信息', value: 'user_info' },
      { label: '读取邮箱', value: 'emails' }
    ],
    config: {
      clientId: '',
      clientSecret: '',
      scope: ['user_info', 'emails']
    }
  },
  {
    code: 'gitlab',
    name: 'GitLab',
    description: '使用 GitLab 账号登录',
    enabled: false,
    loading: false,
    saving: false,
    testing: false,
    scopes: [
      { label: '读取用户信息', value: 'read_user' },
      { label: '读取邮箱', value: 'read_user_email' }
    ],
    config: {
      clientId: '',
      clientSecret: '',
      scope: ['read_user', 'read_user_email']
    }
  },
  {
    code: 'dingtalk',
    name: '钉钉',
    description: '使用钉钉账号登录',
    enabled: false,
    loading: false,
    saving: false,
    testing: false,
    scopes: [
      { label: '获取通讯录权限', value: 'contact:user:readonly' }
    ],
    config: {
      clientId: '',
      clientSecret: '',
      scope: ['contact:user:readonly']
    }
  }
])

function getCallbackUrl(provider) {
  return `${baseUrl}/api/oauth/callback/${provider}`
}

function copyCallbackUrl(provider) {
  const url = getCallbackUrl(provider)
  navigator.clipboard.writeText(url).then(() => {
    ElMessage.success('回调地址已复制')
  })
}

function handleToggleProvider(provider) {
  // TODO: 调用API启用/禁用OAuth提供商
  console.log('Toggle provider:', provider.code, provider.enabled)
}

function handleSaveProvider(provider) {
  provider.saving = true
  // TODO: 调用API保存配置
  setTimeout(() => {
    provider.saving = false
    ElMessage.success(`${provider.name} 配置已保存`)
  }, 500)
}

function handleTestProvider(provider) {
  provider.testing = true
  // TODO: 调用API测试连接
  setTimeout(() => {
    provider.testing = false
    ElMessage.success(`${provider.name} 连接测试成功`)
  }, 500)
}

function loadOAuthConfigs() {
  // TODO: 从后端加载OAuth配置
  const saved = localStorage.getItem('oauthConfigs')
  if (saved) {
    try {
      const configs = JSON.parse(saved)
      oauthProviders.value.forEach(provider => {
        if (configs[provider.code]) {
          Object.assign(provider.config, configs[provider.code].config)
          provider.enabled = configs[provider.code].enabled
        }
      })
    } catch (e) {
      console.error('Load OAuth configs failed:', e)
    }
  }
}

function saveOAuthConfigs() {
  const configs = {}
  oauthProviders.value.forEach(provider => {
    configs[provider.code] = {
      enabled: provider.enabled,
      config: provider.config
    }
  })
  localStorage.setItem('oauthConfigs', JSON.stringify(configs))
}

onMounted(() => {
  loadOAuthConfigs()
})
</script>

<style scoped>
.settings-page {
  padding: var(--space-6);
  background: var(--color-bg);
  min-height: 100vh;
}

.page-header {
  margin-bottom: var(--space-6);
}

.page-title {
  font-family: var(--font-display);
  font-size: 24px;
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: var(--space-2);
}

.page-description {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.oauth-providers {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.provider-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition: all var(--transition-base);
}

.provider-card:hover {
  border-color: var(--color-primary);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15);
}

.provider-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-5);
}

.provider-info {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.provider-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  font-size: 24px;
}

.provider-icon svg {
  width: 28px;
  height: 28px;
}

.provider-github {
  background: linear-gradient(135deg, #24292e 0%, #586069 100%);
  color: #fff;
}

.provider-gitee {
  background: linear-gradient(135deg, #c71d23 0%, #e74c3c 100%);
  color: #fff;
}

.provider-gitlab {
  background: linear-gradient(135deg, #fc6d26 0%, #e24329 100%);
  color: #fff;
}

.provider-dingtalk {
  background: linear-gradient(135deg, #0089ff 0%, #0066cc 100%);
  color: #fff;
}

.provider-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 4px;
}

.provider-desc {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.provider-config {
  padding: 0 var(--space-5) var(--space-5);
  border-top: 1px solid var(--color-border-light);
}

.provider-actions {
  display: flex;
  gap: var(--space-3);
  margin-top: var(--space-4);
}

.instructions-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
}

.instructions-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: var(--space-4);
}

.instructions-content h4 {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
  margin: var(--space-4) 0 var(--space-2);
}

.instructions-content ol {
  margin: 0 0 var(--space-4);
  padding-left: 20px;
}

.instructions-content li {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin-bottom: 8px;
}
</style>

<template>
  <div class="profile-page">
    <el-row :gutter="20">
      <!-- 左侧个人信息卡片 -->
      <el-col :span="8">
        <el-card class="profile-card">
          <div class="profile-header">
            <div class="avatar-wrapper">
              <el-avatar :size="80" :src="userAvatar" class="profile-avatar">
                <el-icon><User /></el-icon>
              </el-avatar>
              <el-upload
                class="avatar-upload"
                :action="uploadAction"
                :headers="uploadHeaders"
                :show-file-list="false"
                :before-upload="beforeAvatarUpload"
                :on-success="handleAvatarSuccess"
                accept="image/*"
              >
                <el-button class="avatar-edit-btn" circle size="small">
                  <el-icon><Edit /></el-icon>
                </el-button>
              </el-upload>
            </div>
            <div class="profile-info">
              <h3 class="profile-name">{{ userInfo.real_name || userInfo.username }}</h3>
              <p class="profile-username">@{{ userInfo.username }}</p>
              <el-tag v-if="userInfo.is_admin" type="warning" size="small">{{ t('user.admin') }}</el-tag>
              <el-tag v-else type="info" size="small">{{ t('user.member') }}</el-tag>
            </div>
          </div>
          <el-divider />
          <div class="profile-stats">
            <div class="stat-item">
              <div class="stat-value">{{ stats.testCases || 0 }}</div>
              <div class="stat-label">{{ t('testCase.title') }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ stats.testPlans || 0 }}</div>
              <div class="stat-label">{{ t('testPlan.title') }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ stats.defects || 0 }}</div>
              <div class="stat-label">{{ t('defect.title') }}</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧详细信息 -->
      <el-col :span="16">
        <el-card class="detail-card">
          <el-tabs v-model="activeTab">
            <!-- 基本信息 -->
            <el-tab-pane :label="t('profile.basicInfo')" name="info">
              <el-form :model="profileForm" :rules="profileRules" ref="profileFormRef" label-width="100px" class="profile-form">
                <el-form-item :label="t('user.username')">
                  <el-input v-model="userInfo.username" disabled />
                </el-form-item>
                <el-form-item :label="t('user.realName')" prop="real_name">
                  <el-input v-model="profileForm.real_name" :placeholder="t('profile.enterRealName')" />
                </el-form-item>
                <el-form-item :label="t('user.email')" prop="email">
                  <el-input v-model="profileForm.email" :placeholder="t('profile.enterEmail')" />
                </el-form-item>
                <el-form-item :label="t('user.phone')" prop="phone">
                  <el-input v-model="profileForm.phone" :placeholder="t('profile.enterPhone')" />
                </el-form-item>
                <el-form-item :label="t('profile.timezone')" prop="timezone">
                  <el-select v-model="profileForm.timezone" style="width: 100%">
                    <el-option label="Asia/Shanghai (UTC+8)" value="Asia/Shanghai" />
                    <el-option label="America/New_York (UTC-5)" value="America/New_York" />
                    <el-option label="Europe/London (UTC+0)" value="Europe/London" />
                    <el-option label="Asia/Tokyo (UTC+9)" value="Asia/Tokyo" />
                  </el-select>
                </el-form-item>
                <el-form-item :label="t('profile.language')" prop="language">
                  <el-select v-model="profileForm.language" style="width: 100%">
                    <el-option label="简体中文" value="zh-CN" />
                    <el-option label="English" value="en-US" />
                  </el-select>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="handleUpdateProfile" :loading="submitting">
                    {{ t('common.save') }}
                  </el-button>
                  <el-button @click="handleResetProfile">{{ t('common.reset') }}</el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>

            <!-- 安全设置 -->
            <el-tab-pane :label="t('profile.security')" name="security">
              <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="100px" class="password-form">
                <el-form-item :label="t('profile.currentPassword')" prop="old_password">
                  <el-input v-model="passwordForm.old_password" type="password" show-password :placeholder="t('profile.enterCurrentPassword')" />
                </el-form-item>
                <el-form-item :label="t('profile.newPassword')" prop="new_password">
                  <el-input v-model="passwordForm.new_password" type="password" show-password :placeholder="t('profile.enterNewPassword')" />
                </el-form-item>
                <el-form-item :label="t('profile.confirmPassword')" prop="confirm_password">
                  <el-input v-model="passwordForm.confirm_password" type="password" show-password :placeholder="t('profile.confirmNewPassword')" />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="handleChangePassword" :loading="passwordSubmitting">
                    {{ t('profile.updatePassword') }}
                  </el-button>
                  <el-button @click="handleResetPassword">{{ t('common.reset') }}</el-button>
                </el-form-item>
              </el-form>

              <!-- 安全提示 -->
              <el-alert :title="t('profile.passwordTip')" type="info" :closable="false" show-icon class="password-tip">
                <ul class="password-requirements">
                  <li>{{ t('profile.requirement1') }}</li>
                  <li>{{ t('profile.requirement2') }}</li>
                  <li>{{ t('profile.requirement3') }}</li>
                </ul>
              </el-alert>
            </el-tab-pane>

            <!-- 活动记录 -->
            <el-tab-pane :label="t('profile.activity')" name="activity">
              <el-timeline>
                <el-timeline-item
                  v-for="item in activityList"
                  :key="item.id"
                  :timestamp="item.timestamp"
                  :type="item.type"
                >
                  <div class="activity-content">
                    <span class="activity-title">{{ item.title }}</span>
                    <span class="activity-description">{{ item.description }}</span>
                  </div>
                </el-timeline-item>
              </el-timeline>
              <el-empty v-if="activityList.length === 0" :description="t('profile.noActivity')" />
            </el-tab-pane>

            <!-- 偏好设置 -->
            <el-tab-pane :label="t('profile.preferences')" name="preferences">
              <el-form :model="preferencesForm" label-width="120px" class="preferences-form">
                <el-form-item :label="t('profile.theme')">
                  <el-radio-group v-model="preferencesForm.theme" @change="handleThemeChange">
                    <el-radio-button label="light">{{ t('theme.light') }}</el-radio-button>
                    <el-radio-button label="dark">{{ t('theme.dark') }}</el-radio-button>
                    <el-radio-button label="blue">{{ t('theme.blue') }}</el-radio-button>
                    <el-radio-button label="green">{{ t('theme.green') }}</el-radio-button>
                  </el-radio-group>
                </el-form-item>
                <el-form-item :label="t('profile.notifications')">
                  <el-switch v-model="preferencesForm.emailNotifications" />
                  <span class="form-item-desc">{{ t('profile.notificationsDesc') }}</span>
                </el-form-item>
                <el-form-item :label="t('profile.autoSave')">
                  <el-switch v-model="preferencesForm.autoSave" />
                  <span class="form-item-desc">{{ t('profile.autoSaveDesc') }}</span>
                </el-form-item>
                <el-form-item :label="t('profile.itemsPerPage')">
                  <el-select v-model="preferencesForm.pageSize" style="width: 150px">
                    <el-option :label="10" :value="10" />
                    <el-option :label="20" :value="20" />
                    <el-option :label="50" :value="50" />
                    <el-option :label="100" :value="100" />
                  </el-select>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="handleSavePreferences">{{ t('common.save') }}</el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Edit } from '@element-plus/icons-vue'
import { userApi } from '@/api/user'
import { useAppStore } from '@/store'
import { useTheme } from '@/composables/useTheme'
import { useI18n } from '@/i18n'

const { t } = useI18n()
const router = useRouter()
const appStore = useAppStore()
const { setTheme } = useTheme()

const activeTab = ref('info')
const submitting = ref(false)
const passwordSubmitting = ref(false)
const profileFormRef = ref()
const passwordFormRef = ref()

// 头像上传
const uploadAction = computed(() => {
  const userId = userInfo.id || appStore.user?.id
  if (!userId) {
    console.warn('User ID not found for avatar upload')
    return ''
  }
  return `${import.meta.env.VITE_API_BASE_URL || '/api'}/users/${userId}/avatar`
})

const uploadHeaders = computed(() => {
  const token = localStorage.getItem('token')
  return token ? { Authorization: `Bearer ${token}` } : {}
})

// 头像上传前校验
function beforeAvatarUpload(file) {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error(t('profile.uploadImageOnly'))
    return false
  }
  if (!isLt2M) {
    ElMessage.error(t('profile.uploadImageSize'))
    return false
  }
  return true
}

// 头像上传成功
function handleAvatarSuccess(response) {
  if (response.code === 200 || response.success) {
    ElMessage.success(t('profile.avatarUploadSuccess'))
    if (response.data?.avatar_url) {
      userInfo.avatar_url = response.data.avatar_url
      appStore.user.avatar_url = response.data.avatar_url
    }
  } else {
    ElMessage.error(response.message || t('profile.avatarUploadFailed'))
  }
}

// 用户信息
const userInfo = reactive({
  id: null,
  username: '',
  real_name: '',
  email: '',
  phone: '',
  avatar_url: '',
  is_admin: false
})

// 个人信息表单
const profileForm = reactive({
  real_name: '',
  email: '',
  phone: '',
  timezone: 'Asia/Shanghai',
  language: 'zh-CN'
})

const profileRules = {
  real_name: [{ required: true, message: t('profile.enterRealName'), trigger: 'blur' }],
  email: [
    { required: true, message: t('profile.enterEmail'), trigger: 'blur' },
    { type: 'email', message: t('profile.invalidEmail'), trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: t('profile.invalidPhone'), trigger: 'blur' }
  ]
}

// 密码表单
const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== passwordForm.new_password) {
    callback(new Error(t('profile.passwordMismatch')))
  } else {
    callback()
  }
}

const passwordRules = {
  old_password: [{ required: true, message: t('profile.enterCurrentPassword'), trigger: 'blur' }],
  new_password: [
    { required: true, message: t('profile.enterNewPassword'), trigger: 'blur' },
    { min: 6, message: t('profile.passwordTooShort'), trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: t('profile.confirmNewPassword'), trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

// 统计信息
const stats = reactive({
  testCases: 0,
  testPlans: 0,
  defects: 0
})

// 活动记录
const activityList = ref([
  {
    id: 1,
    title: '登录系统',
    description: '从 Chrome 浏览器登录',
    timestamp: '2024-01-15 10:30:00',
    type: 'primary'
  },
  {
    id: 2,
    title: '更新用例',
    description: '更新了 3 个测试用例',
    timestamp: '2024-01-15 09:15:00',
    type: 'success'
  }
])

// 偏好设置
const preferencesForm = reactive({
  theme: 'light',
  emailNotifications: true,
  autoSave: true,
  pageSize: 20
})

// 用户头像
const userAvatar = computed(() => {
  // 如果有自定义头像，使用自定义头像
  if (userInfo.avatar_url) {
    return userInfo.avatar_url
  }
  // 否则使用基于姓名的自动生成头像
  return userInfo.real_name
    ? `https://api.dicebear.com/7.x/initials/svg?seed=${encodeURIComponent(userInfo.real_name)}`
    : null
})

// 加载用户信息
async function loadUserInfo() {
  // 如果没有用户ID，跳过API调用（使用store中的数据）
  if (!appStore.user?.id) {
    console.warn('User ID not found, skipping API call')
    return
  }

  try {
    const res = await userApi.getDetail(appStore.user.id)
    Object.assign(userInfo, res.data)
    Object.assign(profileForm, {
      real_name: res.data.real_name || '',
      email: res.data.email || '',
      phone: res.data.phone || '',
      timezone: res.data.timezone || 'Asia/Shanghai',
      language: res.data.language || 'zh-CN'
    })
  } catch (error) {
    console.error('Load user info failed:', error)
    // API调用失败时，继续使用store中的数据
  }
}

// 加载统计信息
async function loadStats() {
  // 如果没有用户ID，跳过API调用
  if (!appStore.user?.id) {
    console.warn('User ID not found, skipping stats load')
    return
  }

  try {
    const res = await userApi.getStats(appStore.user.id)
    if (res.data) {
      Object.assign(stats, {
        testCases: res.data.test_cases || 0,
        testPlans: res.data.test_plans || 0,
        defects: res.data.defects || 0
      })
    }
  } catch (error) {
    console.error('Load stats failed:', error)
    // API调用失败时，使用默认值
    stats.testCases = 0
    stats.testPlans = 0
    stats.defects = 0
  }
}

// 加载偏好设置
function loadPreferences() {
  const saved = localStorage.getItem('userPreferences')
  if (saved) {
    try {
      Object.assign(preferencesForm, JSON.parse(saved))
    } catch (e) {
      console.error('Load preferences failed:', e)
    }
  }
}

// 更新个人信息
async function handleUpdateProfile() {
  await profileFormRef.value.validate()

  // 检查用户ID是否存在
  if (!userInfo.id) {
    ElMessage.warning(t('profile.loadFailed'))
    return
  }

  submitting.value = true
  try {
    await userApi.update(userInfo.id, profileForm)
    Object.assign(userInfo, profileForm)
    // 更新store中的用户信息
    if (appStore.user) {
      Object.assign(appStore.user, profileForm)
      localStorage.setItem('user', JSON.stringify(appStore.user))
    }
    ElMessage.success(t('profile.updateSuccess'))
  } catch (error) {
    ElMessage.error(error.response?.data?.message || t('profile.updateFailed'))
  } finally {
    submitting.value = false
  }
}

// 重置个人信息表单
function handleResetProfile() {
  Object.assign(profileForm, {
    real_name: userInfo.real_name || '',
    email: userInfo.email || '',
    phone: userInfo.phone || '',
    timezone: 'Asia/Shanghai',
    language: 'zh-CN'
  })
  profileFormRef.value?.clearValidate()
}

// 修改密码
async function handleChangePassword() {
  await passwordFormRef.value.validate()
  passwordSubmitting.value = true
  try {
    // TODO: 实现修改密码 API
    ElMessage.success(t('profile.passwordChangeSuccess'))
    handleResetPassword()
  } catch (error) {
    ElMessage.error(t('profile.passwordChangeFailed'))
  } finally {
    passwordSubmitting.value = false
  }
}

// 重置密码表单
function handleResetPassword() {
  Object.assign(passwordForm, {
    old_password: '',
    new_password: '',
    confirm_password: ''
  })
  passwordFormRef.value?.clearValidate()
}

// 主题切换
function handleThemeChange(theme) {
  setTheme(theme)
}

// 保存偏好设置
function handleSavePreferences() {
  localStorage.setItem('userPreferences', JSON.stringify(preferencesForm))
  ElMessage.success(t('profile.preferencesSaved'))
}

onMounted(async () => {
  // 初始化用户信息（从 store 中获取）
  if (appStore.user) {
    console.log('User data from store:', appStore.user)
    Object.assign(userInfo, appStore.user)
    Object.assign(profileForm, {
      real_name: appStore.user.real_name || '',
      email: appStore.user.email || '',
      phone: appStore.user.phone || '',
      timezone: appStore.user.timezone || 'Asia/Shanghai',
      language: appStore.user.language || 'zh-CN'
    })
  } else {
    console.warn('No user data in store')
  }
  await loadUserInfo()
  await loadStats()
  loadPreferences()
})
</script>

<style scoped>
.profile-page {
  padding: 0;
}

/* ========================================
   PROFILE CARD
   ======================================== */
.profile-card {
  margin-bottom: var(--space-4);
}

.profile-header {
  text-align: center;
  padding: var(--space-4) 0;
}

.avatar-wrapper {
  position: relative;
  display: inline-block;
  margin-bottom: var(--space-4);
}

.avatar-upload {
  position: absolute;
  bottom: 0;
  right: 0;
}

.avatar-edit-btn {
  background: var(--color-surface);
  border: 2px solid var(--color-border);
  box-shadow: var(--shadow-md);
}

.avatar-edit-btn:hover {
  background: var(--color-bg-alt);
  border-color: var(--color-accent);
}

.profile-avatar {
  margin-bottom: 0;
}

.profile-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
}

.profile-name {
  font-family: var(--font-display);
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
}

.profile-username {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  margin: 0;
}

.profile-stats {
  display: flex;
  justify-content: space-around;
  padding: var(--space-4) 0;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-family: var(--font-display);
  font-size: var(--text-2xl);
  font-weight: 600;
  color: var(--color-accent);
}

.stat-label {
  font-family: var(--font-body);
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
  margin-top: var(--space-1);
}

/* ========================================
   DETAIL CARD
   ======================================== */
.detail-card {
  min-height: 500px;
}

.detail-card :deep(.el-tabs__content) {
  padding-top: var(--space-4);
}

.profile-form,
.password-form,
.preferences-form {
  max-width: 500px;
}

.form-item-desc {
  margin-left: var(--space-2);
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
}

/* ========================================
   PASSWORD
   ======================================== */
.password-tip {
  margin-top: var(--space-4);
}

.password-requirements {
  margin: var(--space-2) 0 0 0;
  padding-left: var(--space-4);
}

.password-requirements li {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  margin-bottom: var(--space-1);
}

/* ========================================
   ACTIVITY
   ======================================== */
.activity-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.activity-title {
  font-family: var(--font-display);
  font-weight: 500;
  color: var(--color-text);
}

.activity-description {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
}

/* ========================================
   RESPONSIVE
   ======================================== */
@media (max-width: 768px) {
  .profile-page :deep(.el-col) {
    width: 100%;
    margin-bottom: var(--space-4);
  }

  .profile-form,
  .password-form,
  .preferences-form {
    max-width: 100%;
  }
}
</style>

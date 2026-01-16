<template>
  <div class="settings-page">
    <el-card>
      <template #header>
        <span>{{ t('settings.title') }}</span>
      </template>
      <el-tabs v-model="activeTab">
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

        <!-- 成员管理 -->
        <el-tab-pane label="成员管理" name="members">
          <div class="toolbar">
            <el-input
              v-model="userSearch.keyword"
              :placeholder="t('common.search')"
              clearable
              style="width: 200px"
              @change="loadUsers"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-select v-model="userSearch.status" :placeholder="t('user.status')" clearable @change="loadUsers" style="width: 120px">
              <el-option label="激活" value="active" />
              <el-option label="禁用" value="disabled" />
            </el-select>
            <div style="flex: 1"></div>
            <el-button type="primary" :icon="Plus" @click="handleCreateUser">新建用户</el-button>
          </div>
          <el-table :data="userList" style="width: 100%">
            <el-table-column prop="username" :label="t('user.username')" width="120" />
            <el-table-column prop="real_name" :label="t('user.realName')" />
            <el-table-column prop="email" :label="t('user.email')" />
            <el-table-column prop="phone" :label="t('user.phone')" />
            <el-table-column prop="status" :label="t('user.status')" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
                  {{ row.status === 'active' ? '激活' : '禁用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="is_admin" :label="t('user.isAdmin')" width="100">
              <template #default="{ row }">
                <el-tag v-if="row.is_admin" type="warning">管理员</el-tag>
                <el-tag v-else type="info">普通用户</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="oauth_provider" label="OAuth" width="100">
              <template #default="{ row }">
                <el-tag v-if="row.oauth_provider" type="info">{{ row.oauth_provider }}</el-tag>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column :label="t('common.operation')" width="240" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="handleEditUser(row)">{{ t('common.edit') }}</el-button>
                <el-button type="warning" link size="small" @click="handleResetPassword(row)">重置密码</el-button>
                <el-button type="danger" link size="small" @click="handleDeleteUser(row)">{{ t('common.delete') }}</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-pagination
            v-model:current-page="userPagination.page"
            v-model:page-size="userPagination.pageSize"
            :total="userPagination.total"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @current-change="loadUsers"
            @size-change="loadUsers"
            style="margin-top: 20px; justify-content: flex-end"
          />
        </el-tab-pane>

        <!-- OAuth配置 -->
        <el-tab-pane label="OAuth认证" name="oauth">
          <el-form :model="oauthForm" label-width="120px" style="max-width: 600px">
            <el-form-item label="启用的平台">
              <el-checkbox-group v-model="oauthForm.enabledProviders">
                <el-checkbox label="github">GitHub</el-checkbox>
                <el-checkbox label="gitee">Gitee</el-checkbox>
                <el-checkbox label="gitlab">GitLab</el-checkbox>
                <el-checkbox label="dingtalk">钉钉</el-checkbox>
              </el-checkbox-group>
            </el-form-item>

            <el-divider content-position="left">GitHub 配置</el-divider>
            <el-form-item label="Client ID">
              <el-input v-model="oauthForm.github.clientId" placeholder="GitHub Client ID" />
            </el-form-item>
            <el-form-item label="Client Secret">
              <el-input v-model="oauthForm.github.clientSecret" type="password" placeholder="GitHub Client Secret" />
            </el-form-item>

            <el-divider content-position="left">Gitee 配置</el-divider>
            <el-form-item label="Client ID">
              <el-input v-model="oauthForm.gitee.clientId" placeholder="Gitee Client ID" />
            </el-form-item>
            <el-form-item label="Client Secret">
              <el-input v-model="oauthForm.gitee.clientSecret" type="password" placeholder="Gitee Client Secret" />
            </el-form-item>

            <el-divider content-position="left">GitLab 配置</el-divider>
            <el-form-item label="Application ID">
              <el-input v-model="oauthForm.gitlab.clientId" placeholder="GitLab Application ID" />
            </el-form-item>
            <el-form-item label="Secret">
              <el-input v-model="oauthForm.gitlab.clientSecret" type="password" placeholder="GitLab Secret" />
            </el-form-item>

            <el-divider content-position="left">钉钉配置</el-divider>
            <el-form-item label="AppKey">
              <el-input v-model="oauthForm.dingtalk.appKey" placeholder="钉钉 AppKey" />
            </el-form-item>
            <el-form-item label="AppSecret">
              <el-input v-model="oauthForm.dingtalk.appSecret" type="password" placeholder="钉钉 AppSecret" />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="handleSaveOAuth">保存配置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane :label="t('settings.workflow')" name="workflow">
          <div class="toolbar">
            <div style="flex: 1"></div>
            <el-button type="primary" :icon="Plus" @click="handleCreateWorkflow">{{ t('settings.newStatus') }}</el-button>
          </div>
          <el-table :data="workflowList" style="width: 100%">
            <el-table-column prop="name" :label="t('settings.statusName')" />
            <el-table-column prop="code" :label="t('settings.statusCode')" />
            <el-table-column :label="t('settings.displayColor')" width="150">
              <template #default="{ row }">
                <div class="color-preview">
                  <span class="color-box" :style="{ backgroundColor: row.color }"></span>
                  <span>{{ row.color }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="sort_order" :label="t('settings.sortOrder')" width="100" />
            <el-table-column prop="is_default" :label="t('settings.setDefault')" width="100">
              <template #default="{ row }">
                <el-tag v-if="row.is_default" type="success">{{ t('settings.yes') }}</el-tag>
                <el-tag v-else type="info">{{ t('settings.no') }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column :label="t('common.operation')" width="150">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="handleEditWorkflow(row)">{{ t('common.edit') }}</el-button>
                <el-button type="danger" link size="small" @click="handleDeleteWorkflow(row)">{{ t('common.delete') }}</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane :label="t('settings.notification')" name="notification">
          <el-form :model="notificationForm" label-width="120px" style="max-width: 600px">
            <el-form-item :label="t('settings.emailNotification')">
              <el-switch v-model="notificationForm.emailEnabled" />
            </el-form-item>
            <el-form-item :label="t('settings.smtpServer')">
              <el-input v-model="notificationForm.smtpHost" />
            </el-form-item>
            <el-form-item :label="t('settings.smtpPort')">
              <el-input-number v-model="notificationForm.smtpPort" :min="1" :max="65535" />
            </el-form-item>
            <el-form-item :label="t('settings.fromEmail')">
              <el-input v-model="notificationForm.fromEmail" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleSaveNotification">{{ t('common.save') }}</el-button>
              <el-button @click="handleTestEmail">{{ t('settings.sendTestEmail') }}</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane :label="t('settings.about')" name="about">
          <el-descriptions :title="t('settings.sysInfo')" :column="1" border>
            <el-descriptions-item :label="t('settings.platformName')">{{ t('settings.platformName') }}</el-descriptions-item>
            <el-descriptions-item :label="t('settings.sysVersion')">{{ t('settings.version') }}</el-descriptions-item>
            <el-descriptions-item :label="t('settings.frontendStack')">{{ t('settings.frontendTech') }}</el-descriptions-item>
            <el-descriptions-item :label="t('settings.backendStack')">{{ t('settings.backendTech') }}</el-descriptions-item>
            <el-descriptions-item :label="t('settings.license')">{{ t('settings.licenseType') }}</el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 用户表单对话框 -->
    <el-dialog v-model="userDialogVisible" :title="userDialogTitle" width="600px" destroy-on-close>
      <el-form :model="userForm" :rules="userRules" ref="userFormRef" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" :disabled="isEditUser" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!isEditUser">
          <el-input v-model="userForm.password" type="password" placeholder="不填则使用默认密码123456" />
        </el-form-item>
        <el-form-item label="真实姓名" prop="real_name">
          <el-input v-model="userForm.real_name" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="userForm.phone" />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="userForm.status">
            <el-radio label="active">激活</el-radio>
            <el-radio label="disabled">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="管理员">
          <el-switch v-model="userForm.is_admin" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="userDialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" @click="handleSubmitUser">{{ t('common.confirm') }}</el-button>
      </template>
    </el-dialog>

    <!-- 工作流状态编辑对话框 -->
    <el-dialog v-model="workflowDialogVisible" :title="workflowDialogTitle" width="500px" destroy-on-close>
      <el-form :model="workflowForm" :rules="workflowRules" ref="workflowFormRef" label-width="100px">
        <el-form-item :label="t('settings.statusName')" prop="name">
          <el-input v-model="workflowForm.name" :placeholder="t('settings.statusName')" />
        </el-form-item>
        <el-form-item :label="t('settings.statusCode')" prop="code">
          <el-input v-model="workflowForm.code" placeholder="e.g.: new, in_progress" />
        </el-form-item>
        <el-form-item :label="t('settings.displayColor')" prop="color">
          <div class="color-picker-wrapper">
            <el-color-picker v-model="workflowForm.color" show-alpha />
            <span class="color-value">{{ workflowForm.color }}</span>
            <span class="color-preview-box" :style="{ backgroundColor: workflowForm.color }"></span>
          </div>
        </el-form-item>
        <el-form-item :label="t('settings.sortOrder')" prop="sort_order">
          <el-input-number v-model="workflowForm.sort_order" :min="1" :max="100" />
        </el-form-item>
        <el-form-item :label="t('settings.setDefault')">
          <el-switch v-model="workflowForm.is_default" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="workflowDialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" @click="handleSubmitWorkflow">{{ t('common.confirm') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAppStore } from '@/store'
import { useI18n } from '@/i18n'
import { Plus, Search } from '@element-plus/icons-vue'
import { userApi } from '@/api/user'
import { oauthApi } from '@/api/oauth'

const appStore = useAppStore()
const { t, locale } = useI18n()
const activeTab = ref('basic')
const workflowDialogVisible = ref(false)
const workflowDialogTitle = ref('')
const workflowFormRef = ref()
const isEditWorkflow = ref(false)

// 用户管理相关
const userDialogVisible = ref(false)
const userDialogTitle = ref('')
const userFormRef = ref()
const isEditUser = ref(false)
const userList = ref([])
const userSearch = reactive({
  keyword: '',
  status: ''
})
const userPagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const userForm = reactive({
  id: null,
  username: '',
  password: '',
  real_name: '',
  email: '',
  phone: '',
  status: 'active',
  is_admin: false
})

const userRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  real_name: [{ required: true, message: '请输入真实姓名', trigger: 'blur' }],
  email: [{ type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }]
}

// OAuth配置
const oauthForm = reactive({
  enabledProviders: [],
  github: { clientId: '', clientSecret: '' },
  gitee: { clientId: '', clientSecret: '' },
  gitlab: { clientId: '', clientSecret: '' },
  dingtalk: { appKey: '', appSecret: '' }
})

const basicForm = reactive({
  systemName: 'Test Management Platform',
  defaultProject: '',
  language: 'zh-CN',
  timezone: 'Asia/Shanghai'
})

const notificationForm = reactive({
  emailEnabled: false,
  smtpHost: '',
  smtpPort: 587,
  fromEmail: ''
})

const workflowForm = reactive({
  id: null,
  name: '',
  code: '',
  color: '#409eff',
  sort_order: 1,
  is_default: false
})

const workflowRules = ref({})
const workflowList = ref([
  { id: 1, name: '新建', code: 'new', color: '#909399', sort_order: 1, is_default: true },
  { id: 2, name: '已分配', code: 'assigned', color: '#e6a23c', sort_order: 2, is_default: false },
  { id: 3, name: '进行中', code: 'in_progress', color: '#409eff', sort_order: 3, is_default: false },
  { id: 4, name: '已解决', code: 'resolved', color: '#67c23a', sort_order: 4, is_default: false },
  { id: 5, name: '已关闭', code: 'closed', color: '#909399', sort_order: 5, is_default: false }
])

// 用户管理方法
async function loadUsers() {
  try {
    const res = await userApi.getList({
      page: userPagination.page,
      per_page: userPagination.pageSize,
      ...userSearch
    })
    userList.value = res.data.items || []
    userPagination.total = res.data.total || 0
  } catch (error) {
    ElMessage.error('加载用户列表失败')
  }
}

function handleCreateUser() {
  isEditUser.value = false
  userDialogTitle.value = '新建用户'
  Object.assign(userForm, {
    id: null,
    username: '',
    password: '',
    real_name: '',
    email: '',
    phone: '',
    status: 'active',
    is_admin: false
  })
  userDialogVisible.value = true
}

function handleEditUser(row) {
  isEditUser.value = true
  userDialogTitle.value = '编辑用户'
  Object.assign(userForm, {
    id: row.id,
    username: row.username,
    real_name: row.real_name,
    email: row.email,
    phone: row.phone,
    status: row.status,
    is_admin: row.is_admin
  })
  userDialogVisible.value = true
}

async function handleSubmitUser() {
  userFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const data = { ...userForm }
        if (!data.password) {
          delete data.password
        }

        if (isEditUser.value) {
          await userApi.update(userForm.id, data)
          ElMessage.success('更新成功')
        } else {
          await userApi.create(data)
          ElMessage.success('创建成功')
        }
        userDialogVisible.value = false
        loadUsers()
      } catch (error) {
        ElMessage.error(error.response?.data?.message || '操作失败')
      }
    }
  })
}

function handleResetPassword(row) {
  ElMessageBox.confirm('确定要重置该用户的密码吗？重置后密码为：123456', '确认重置', {
    type: 'warning'
  }).then(async () => {
    try {
      await userApi.resetPassword(row.id)
      ElMessage.success('密码已重置为：123456')
    } catch (error) {
      ElMessage.error('重置失败')
    }
  })
}

function handleDeleteUser(row) {
  ElMessageBox.confirm('确定要删除该用户吗？', '确认删除', {
    type: 'warning'
  }).then(async () => {
    try {
      await userApi.delete(row.id)
      ElMessage.success('删除成功')
      loadUsers()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

// OAuth配置方法
async function handleSaveOAuth() {
  try {
    // 保存每个平台的配置
    for (const provider of oauthForm.enabledProviders) {
      const config = oauthForm[provider]
      if (provider === 'dingtalk') {
        await oauthApi.updateConfig({
          provider,
          client_id: config.appKey,
          client_secret: config.appSecret
        })
      } else {
        await oauthApi.updateConfig({
          provider,
          client_id: config.clientId,
          client_secret: config.clientSecret
        })
      }
    }
    ElMessage.success('OAuth配置已保存')
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

function updateWorkflowRules() {
  workflowRules.value = {
    name: [{ required: true, message: t('settings.statusName') + ' is required', trigger: 'blur' }],
    code: [{ required: true, message: t('settings.statusCode') + ' is required', trigger: 'blur' }],
    color: [{ required: true, message: t('settings.displayColor') + ' is required', trigger: 'change' }]
  }
}

function loadSettings() {
  const savedSettings = localStorage.getItem('systemSettings')
  if (savedSettings) {
    try {
      const settings = JSON.parse(savedSettings)
      Object.assign(basicForm, settings)
      if (settings.language) {
        appStore.setLanguage(settings.language)
      }
    } catch (e) {
      console.error('Load settings failed:', e)
    }
  }
}

function handleLanguageChange() {
  updateWorkflowRules()
}

function handleSaveBasic() {
  const settings = {
    systemName: basicForm.systemName,
    defaultProject: basicForm.defaultProject,
    language: basicForm.language,
    timezone: basicForm.timezone
  }
  localStorage.setItem('systemSettings', JSON.stringify(settings))
  appStore.setLanguage(basicForm.language)
  ElMessage.success(t('settings.saveSuccess'))
}

function handleSaveNotification() {
  const settings = {
    emailEnabled: notificationForm.emailEnabled,
    smtpHost: notificationForm.smtpHost,
    smtpPort: notificationForm.smtpPort,
    fromEmail: notificationForm.fromEmail
  }
  localStorage.setItem('notificationSettings', JSON.stringify(settings))
  ElMessage.success(t('settings.notificationSaveSuccess'))
}

function handleTestEmail() {
  ElMessage.success(t('settings.testEmailSent'))
}

onMounted(() => {
  loadSettings()
  updateWorkflowRules()
  loadUsers()
})

watch(locale, () => {
  updateWorkflowRules()
})

function handleCreateWorkflow() {
  isEditWorkflow.value = false
  workflowDialogTitle.value = t('settings.newStatus')
  Object.assign(workflowForm, {
    id: null,
    name: '',
    code: '',
    color: '#409eff',
    sort_order: workflowList.value.length + 1,
    is_default: false
  })
  workflowDialogVisible.value = true
}

function handleEditWorkflow(row) {
  isEditWorkflow.value = true
  workflowDialogTitle.value = t('common.edit') + ' ' + t('settings.workflow')
  Object.assign(workflowForm, {
    id: row.id,
    name: row.name,
    code: row.code,
    color: row.color,
    sort_order: row.sort_order,
    is_default: row.is_default
  })
  workflowDialogVisible.value = true
}

function handleDeleteWorkflow(row) {
  ElMessageBox.confirm(t('settings.deleteConfirm'), t('common.confirm'), {
    type: 'warning'
  }).then(() => {
    const index = workflowList.value.findIndex(item => item.id === row.id)
    if (index > -1) {
      workflowList.value.splice(index, 1)
      ElMessage.success(t('common.deleteSuccess'))
    }
  })
}

function handleSubmitWorkflow() {
  workflowFormRef.value.validate((valid) => {
    if (valid) {
      if (isEditWorkflow.value) {
        const index = workflowList.value.findIndex(item => item.id === workflowForm.id)
        if (index > -1) {
          Object.assign(workflowList.value[index], workflowForm)
          ElMessage.success(t('settings.updateSuccess'))
        }
      } else {
        workflowList.value.push({
          id: Date.now(),
          name: workflowForm.name,
          code: workflowForm.code,
          color: workflowForm.color,
          sort_order: workflowForm.sort_order,
          is_default: workflowForm.is_default
        })
        ElMessage.success(t('settings.addSuccess'))
      }
      workflowDialogVisible.value = false
    }
  })
}
</script>

<style scoped>
.toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.color-preview {
  display: flex;
  align-items: center;
  gap: 8px;
}

.color-box {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
}

.color-picker-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.color-value {
  color: #606266;
  font-size: 14px;
  min-width: 80px;
}

.color-preview-box {
  width: 30px;
  height: 30px;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
}
</style>

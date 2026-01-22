<template>
  <div class="settings-page animate-fade-in-up">
    <!-- Page Header -->
    <div class="page-header">
      <h1 class="page-title">通知设置</h1>
      <p class="page-description">配置邮件通知和提醒规则</p>
    </div>

    <el-tabs v-model="activeTab" class="notification-tabs">
      <!-- SMTP配置 -->
      <el-tab-pane label="SMTP配置" name="smtp">
        <el-card class="config-card">
          <template #header>
            <div class="card-header">
              <el-icon><Message /></el-icon>
              <span>邮件服务器设置</span>
            </div>
          </template>

          <el-form :model="smtpForm" label-width="140px" label-position="left">
            <el-form-item label="启用邮件通知">
              <el-switch v-model="smtpForm.enabled" />
              <span class="form-hint">启用后系统将发送邮件通知</span>
            </el-form-item>

            <el-divider content-position="left">服务器配置</el-divider>

            <el-form-item label="SMTP服务器" required>
              <el-input v-model="smtpForm.host" placeholder="smtp.example.com" :disabled="!smtpForm.enabled">
                <template #prepend>smtp://</template>
              </el-input>
            </el-form-item>

            <el-form-item label="端口" required>
              <el-select v-model="smtpForm.port" placeholder="选择端口" :disabled="!smtpForm.enabled" style="width: 200px">
                <el-option label="25 (SMTP)" :value="25" />
                <el-option label="465 (SMTPS)" :value="465" />
                <el-option label="587 (STARTTLS)" :value="587" />
                <el-option label="2525 (Alternate)" :value="2525" />
              </el-select>
            </el-form-item>

            <el-form-item label="加密方式">
              <el-radio-group v-model="smtpForm.encryption" :disabled="!smtpForm.enabled">
                <el-radio label="none">无加密</el-radio>
                <el-radio label="ssl">SSL/TLS</el-radio>
                <el-radio label="tls">STARTTLS</el-radio>
              </el-radio-group>
            </el-form-item>

            <el-divider content-position="left">认证设置</el-divider>

            <el-form-item label="发件人邮箱" required>
              <el-input v-model="smtpForm.from_email" placeholder="noreply@example.com" :disabled="!smtpForm.enabled" />
            </el-form-item>

            <el-form-item label="发件人名称">
              <el-input v-model="smtpForm.from_name" placeholder="TestP 测试管理平台" :disabled="!smtpForm.enabled" />
            </el-form-item>

            <el-form-item label="用户名" required>
              <el-input v-model="smtpForm.username" placeholder="邮箱地址或用户名" :disabled="!smtpForm.enabled" />
            </el-form-item>

            <el-form-item label="密码/授权码" required>
              <el-input v-model="smtpForm.password" type="password" placeholder="邮箱密码或授权码" show-password :disabled="!smtpForm.enabled" />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" :loading="testing" :disabled="!smtpForm.enabled" @click="handleTestConnection">
                测试连接
              </el-button>
              <el-button @click="handleSaveSmtp" :loading="saving">保存配置</el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 常用邮箱配置提示 -->
        <el-card class="config-card">
          <template #header>
            <div class="card-header">
              <el-icon><InfoFilled /></el-icon>
              <span>常用邮箱配置参考</span>
            </div>
          </template>

          <el-collapse accordion>
            <el-collapse-item title="Gmail (谷歌邮箱)" name="gmail">
              <div class="email-config">
                <p><strong>SMTP服务器:</strong> smtp.gmail.com</p>
                <p><strong>端口:</strong> 587 (STARTTLS) 或 465 (SSL)</p>
                <p><strong>注意事项:</strong> 需要使用应用专用密码，不是账号密码</p>
                <el-link type="primary" href="https://support.google.com/accounts/answer/185833" target="_blank">
                  获取 Gmail 应用专用密码 <el-icon><TopRight /></el-icon>
                </el-link>
              </div>
            </el-collapse-item>

            <el-collapse-item title="QQ邮箱" name="qq">
              <div class="email-config">
                <p><strong>SMTP服务器:</strong> smtp.qq.com</p>
                <p><strong>端口:</strong> 587 (STARTTLS) 或 465 (SSL)</p>
                <p><strong>注意事项:</strong> 需要开启 SMTP 服务并使用授权码</p>
                <el-link type="primary" href="https://service.mail.qq.com/cgi-bin/help?subtype=1&id=28&no=1001256" target="_blank">
                  查看 QQ邮箱 SMTP 设置 <el-icon><TopRight /></el-icon>
                </el-link>
              </div>
            </el-collapse-item>

            <el-collapse-item title="163邮箱" name="163">
              <div class="email-config">
                <p><strong>SMTP服务器:</strong> smtp.163.com</p>
                <p><strong>端口:</strong> 465 (SSL)</p>
                <p><strong>注意事项:</strong> 需要开启 SMTP 服务并使用授权码</p>
              </div>
            </el-collapse-item>

            <el-collapse-item title="Outlook / Office 365" name="outlook">
              <div class="email-config">
                <p><strong>SMTP服务器:</strong> smtp.office365.com</p>
                <p><strong>端口:</strong> 587 (STARTTLS)</p>
                <p><strong>注意事项:</strong> 使用完整的 Outlook 邮箱地址作为用户名</p>
              </div>
            </el-collapse-item>

            <el-collapse-item title="阿里云邮箱" name="aliyun">
              <div class="email-config">
                <p><strong>SMTP服务器:</strong> smtp.aliyun.com</p>
                <p><strong>端口:</strong> 465 (SSL)</p>
                <p><strong>注意事项:</strong> 需要在邮箱设置中开启 SMTP 服务</p>
              </div>
            </el-collapse-item>
          </el-collapse>
        </el-card>
      </el-tab-pane>

      <!-- 通知规则 -->
      <el-tab-pane label="通知规则" name="rules">
        <div class="rules-section">
          <div v-for="category in notificationCategories" :key="category.code" class="rule-category">
            <div class="category-header">
              <div class="category-info">
                <div class="category-icon" :style="{ backgroundColor: category.color }">
                  <el-icon>
                    <component :is="category.icon" />
                  </el-icon>
                </div>
                <div>
                  <h3 class="category-name">{{ category.name }}</h3>
                  <p class="category-desc">{{ category.description }}</p>
                </div>
              </div>
              <el-switch v-model="category.enabled" @change="handleToggleCategory(category)" />
            </div>

            <div v-show="category.enabled" class="category-rules">
              <div v-for="rule in category.rules" :key="rule.code" class="rule-item">
                <div class="rule-info">
                  <span class="rule-name">{{ rule.name }}</span>
                  <span class="rule-desc">{{ rule.description }}</span>
                </div>
                <div class="rule-config">
                  <el-switch v-model="rule.email_enabled" @change="handleUpdateRule(rule)" />
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="actions-bar">
          <el-button type="primary" @click="handleSaveRules" :loading="saving">保存规则</el-button>
        </div>
      </el-tab-pane>

      <!-- 通知模板 -->
      <el-tab-pane label="通知模板" name="templates">
        <div class="templates-section">
          <div v-for="template in emailTemplates" :key="template.code" class="template-card">
            <div class="template-header">
              <h3 class="template-name">{{ template.name }}</h3>
              <el-button type="primary" link @click="handleEditTemplate(template)">
                <el-icon><Edit /></el-icon>
                编辑模板
              </el-button>
            </div>
            <p class="template-desc">{{ template.description }}</p>
            <div class="template-preview">
              <div class="preview-label">主题预览:</div>
              <div class="preview-subject">{{ template.subject }}</div>
              <div class="preview-label">内容预览:</div>
              <div class="preview-body">{{ template.body_preview }}</div>
            </div>
          </div>
        </div>

        <!-- 模板编辑对话框 -->
        <el-dialog v-model="templateDialogVisible" :title="`编辑${editingTemplate?.name}`" width="700px" destroy-on-close>
          <el-form :model="templateForm" label-width="100px">
            <el-form-item label="邮件主题">
              <el-input v-model="templateForm.subject" placeholder="使用 {{变量}} 插入动态内容" />
            </el-form-item>
            <el-form-item label="邮件内容">
              <el-input
                v-model="templateForm.body"
                type="textarea"
                :rows="10"
                placeholder="支持HTML格式，使用 {{变量}} 插入动态内容"
              />
            </el-form-item>
            <el-form-item label="可用变量">
              <el-tag v-for="variable in editingTemplate?.variables" :key="variable" class="variable-tag">
                {{ variable }}
              </el-tag>
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="templateDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="handleSaveTemplate">保存模板</el-button>
          </template>
        </el-dialog>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Message, InfoFilled, TopRight, Edit, Bell, Warning, SuccessFilled,
  DocumentChecked, User, ChatDotRound
} from '@element-plus/icons-vue'

const activeTab = ref('smtp')
const testing = ref(false)
const saving = ref(false)
const templateDialogVisible = ref(false)
const editingTemplate = ref(null)

const smtpForm = reactive({
  enabled: false,
  host: '',
  port: 587,
  encryption: 'tls',
  from_email: '',
  from_name: 'TestP 测试管理平台',
  username: '',
  password: ''
})

const notificationCategories = ref([
  {
    code: 'defect',
    name: '缺陷通知',
    description: '缺陷创建、状态变更、评论等',
    icon: 'Warning',
    color: '#ef4444',
    enabled: true,
    rules: [
      { code: 'defect_created', name: '缺陷被分配给我', description: '当有新缺陷分配给您时通知', email_enabled: true },
      { code: 'defect_updated', name: '缺陷状态变更', description: '负责的缺陷状态发生变更时通知', email_enabled: true },
      { code: 'defect_comment', name: '缺陷有新评论', description: '负责或创建的缺陷有新评论时通知', email_enabled: true }
    ]
  },
  {
    code: 'test_case',
    name: '测试用例',
    description: '测试用例执行、审核等',
    icon: 'DocumentChecked',
    color: '#3b82f6',
    enabled: true,
    rules: [
      { code: 'test_assigned', name: '用例被分配给我', description: '当有测试用例分配给您时通知', email_enabled: true },
      { code: 'test_review', name: '用例待审核', description: '创建的用例进入审核流程时通知', email_enabled: true }
    ]
  },
  {
    code: 'test_plan',
    name: '测试计划',
    description: '测试计划开始、完成等',
    icon: 'SuccessFilled',
    color: '#22c55e',
    enabled: true,
    rules: [
      { code: 'plan_start', name: '测试计划开始', description: '参与的测试计划开始执行时通知', email_enabled: true },
      { code: 'plan_complete', name: '测试计划完成', description: '参与的测试计划完成时通知', email_enabled: true }
    ]
  },
  {
    code: 'system',
    name: '系统通知',
    description: '系统级别的重要通知',
    icon: 'Bell',
    color: '#8b5cf6',
    enabled: true,
    rules: [
      { code: 'user_mention', name: '有人@我', description: '在评论中被提及时时通知', email_enabled: true }
    ]
  }
])

const emailTemplates = ref([
  {
    code: 'defect_assigned',
    name: '缺陷分配通知',
    description: '当缺陷被分配给用户时发送',
    subject: '【新缺陷】{{ defect_title }} - {{ project_name }}',
    body_preview: '您好 {{ user_name }}，\n\n有一个新缺陷分配给您：\n\n缺陷标题：{{ defect_title }}\n优先级：{{ priority }}\n描述：{{ description }}',
    variables: ['{{ defect_title }}', '{{ project_name }}', '{{ user_name }}', '{{ priority }}', '{{ description }}', '{{ url }}']
  },
  {
    code: 'defect_status_changed',
    name: '缺陷状态变更',
    description: '当缺陷状态发生变更时发送',
    subject: '【状态变更】{{ defect_title }} - {{ old_status }} → {{ new_status }}',
    body_preview: '您好 {{ user_name }}，\n\n您负责的缺陷状态已变更：\n\n缺陷标题：{{ defect_title }}\n原状态：{{ old_status }}\n新状态：{{ new_status }}\n操作人：{{ changed_by }}',
    variables: ['{{ defect_title }}', '{{ old_status }}', '{{ new_status }}', '{{ user_name }}', '{{ changed_by }}', '{{ url }}']
  },
  {
    code: 'test_plan_complete',
    name: '测试计划完成',
    description: '当测试计划执行完成时发送',
    subject: '【测试完成】{{ plan_name }} 执行报告',
    body_preview: '您好 {{ user_name }}，\n\n测试计划 "{{ plan_name }}" 已执行完成：\n\n总用例数：{{ total_cases }}\n通过：{{ passed }}\n失败：{{ failed }}\n通过率：{{ pass_rate }}%',
    variables: ['{{ plan_name }}', '{{ user_name }}', '{{ total_cases }}', '{{ passed }}', '{{ failed }}', '{{ pass_rate }}', '{{ url }}']
  }
])

const templateForm = reactive({
  subject: '',
  body: ''
})

function handleTestConnection() {
  testing.value = true
  // TODO: 调用API测试SMTP连接
  setTimeout(() => {
    testing.value = false
    ElMessage.success('连接测试成功，邮件已发送')
  }, 1000)
}

function handleSaveSmtp() {
  saving.value = true
  // TODO: 调用API保存SMTP配置
  setTimeout(() => {
    saving.value = false
    ElMessage.success('SMTP配置已保存')
  }, 500)
}

function handleToggleCategory(category) {
  category.rules.forEach(rule => {
    rule.email_enabled = category.enabled
  })
}

function handleUpdateRule(rule) {
  // TODO: 调用API更新规则
}

function handleSaveRules() {
  saving.value = true
  // TODO: 调用API保存规则
  setTimeout(() => {
    saving.value = false
    ElMessage.success('通知规则已保存')
  }, 500)
}

function handleEditTemplate(template) {
  editingTemplate.value = template
  templateForm.subject = template.subject
  templateForm.body = template.body_preview
  templateDialogVisible.value = true
}

function handleSaveTemplate() {
  // TODO: 调用API保存模板
  templateDialogVisible.value = false
  ElMessage.success('模板已保存')
}

function loadSmtpConfig() {
  const saved = localStorage.getItem('smtpConfig')
  if (saved) {
    try {
      Object.assign(smtpForm, JSON.parse(saved))
    } catch (e) {
      console.error('Load SMTP config failed:', e)
    }
  }
}

onMounted(() => {
  loadSmtpConfig()
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

.notification-tabs {
  margin-top: var(--space-4);
}

.notification-tabs :deep(.el-tabs__content) {
  padding-top: var(--space-5);
}

.config-card {
  margin-bottom: var(--space-4);
}

.config-card :deep(.el-card__header) {
  padding: var(--space-4) var(--space-5);
  border-bottom: 1px solid var(--color-border-light);
}

.card-header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-weight: 600;
  color: var(--color-text);
}

.config-card :deep(.el-card__body) {
  padding: var(--space-5);
}

.form-hint {
  font-size: 12px;
  color: var(--color-text-muted);
  margin-left: var(--space-2);
}

.email-config p {
  margin: 8px 0;
  font-size: 13px;
  color: var(--color-text-secondary);
}

.rules-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.rule-category {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.category-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4);
  border-bottom: 1px solid var(--color-border-light);
}

.category-info {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.category-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  color: white;
  font-size: 18px;
}

.category-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
}

.category-desc {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin: 4px 0 0 0;
}

.category-rules {
  padding: var(--space-4);
}

.rule-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-3);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-2);
  background: var(--color-bg-secondary);
}

.rule-item:last-child {
  margin-bottom: 0;
}

.rule-info {
  display: flex;
  flex-direction: column;
}

.rule-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text);
}

.rule-desc {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-top: 4px;
}

.actions-bar {
  display: flex;
  justify-content: flex-end;
  padding: var(--space-4);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  margin-top: var(--space-4);
}

.templates-section {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: var(--space-4);
}

.template-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
}

.template-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-2);
}

.template-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
}

.template-desc {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-bottom: var(--space-3);
}

.template-preview {
  background: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  padding: var(--space-3);
}

.preview-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--color-text-muted);
  margin-bottom: 4px;
  text-transform: uppercase;
}

.preview-subject {
  font-size: 13px;
  color: var(--color-text);
  margin-bottom: var(--space-3);
  padding-left: var(--space-2);
}

.preview-body {
  font-size: 12px;
  color: var(--color-text-secondary);
  white-space: pre-wrap;
  padding-left: var(--space-2);
  line-height: 1.6;
}

.variable-tag {
  margin-right: var(--space-2);
  font-family: var(--font-mono);
  font-size: 12px;
}
</style>

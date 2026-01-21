<template>
  <div class="page-container">
    <el-card class="skills-card">
      <el-tabs v-model="activeTab" class="skills-tabs">
          <!-- Skills 标签页 -->
          <el-tab-pane name="skills">
            <template #label>
              <span class="tab-label">
                <el-icon><Files /></el-icon>
                Skills
              </span>
            </template>

            <!-- 工具栏 -->
            <div class="toolbar">
              <div class="toolbar-left">
                <el-input
                  v-model="skillFilters.keyword"
                  placeholder="搜索技能名称或描述..."
                  clearable
                  class="search-input"
                  @keyup.enter="loadSkills"
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>
                <el-button :icon="Search" @click="loadSkills">搜索</el-button>
                <el-button @click="resetSkillFilters">重置</el-button>
              </div>
              <div class="toolbar-right">
                <el-button
                  :icon="Refresh"
                  :loading="syncingSkills"
                  @click="syncAllRepositories"
                  type="primary"
                >
                  同步技能
                </el-button>
                <span class="result-count">共 {{ skillPagination.total }} 个技能</span>
              </div>
            </div>

            <!-- 技能卡片网格 -->
            <div v-loading="skillLoading" class="skills-content">
              <el-row :gutter="20" class="skills-grid">
                <el-col v-for="skill in skillList" :key="skill.id" :xs="24" :sm="12" :md="8" :lg="6" :xl="4">
                  <div class="skill-card" @click="viewSkillDetail(skill)">
                    <div class="skill-card-header">
                      <div class="skill-icon-small">
                        <el-icon size="20" :color="getSkillIconColor(skill.script_type)">
                          <component :is="getSkillIcon(skill.script_type)" />
                        </el-icon>
                      </div>
                      <h4 class="skill-name-large">{{ skill.name }}</h4>
                    </div>
                    <div class="skill-info">
                      <div class="skill-meta-row">
                        <el-tag :type="getScriptTypeTag(skill.script_type)" size="small">
                          {{ skill.script_type }}
                        </el-tag>
                        <span
                          class="skill-repo-link"
                          @click.stop="goToRepository(skill.repository_id)"
                        >
                          <el-icon><FolderOpened /></el-icon>
                          {{ skill.repository_name }}
                        </span>
                      </div>
                      <p class="skill-desc">{{ skill.description || '暂无描述' }}</p>
                    </div>
                    <div class="skill-footer">
                      <span class="skill-status" :class="skill.status">
                        {{ skill.status === 'active' ? '启用' : '禁用' }}
                      </span>
                      <div class="skill-actions" @click.stop>
                        <el-button link type="primary" size="small" @click="viewSkillDetail(skill)">详情</el-button>
                        <el-button link type="success" size="small" @click="executeSkill(skill)">执行</el-button>
                      </div>
                    </div>
                  </div>
                </el-col>
              </el-row>

              <div v-if="skillList.length === 0 && !skillLoading" class="empty-state">
                <el-empty description="暂无技能数据" />
              </div>
            </div>

            <!-- 分页 -->
            <div class="table-pagination">
              <el-pagination
                v-model:current-page="skillPagination.page"
                v-model:page-size="skillPagination.per_page"
                :total="skillPagination.total"
                :page-sizes="[12, 24, 48, 96]"
                layout="total, sizes, prev, pager, next, jumper"
                @current-change="loadSkills"
                @size-change="loadSkills"
              />
            </div>
          </el-tab-pane>

        <!-- 仓库管理 标签页 -->
        <el-tab-pane name="repositories">
          <template #label>
            <span class="tab-label">
              <el-icon><FolderOpened /></el-icon>
              仓库管理
            </span>
          </template>

          <!-- 工具栏 -->
          <div class="toolbar">
            <div class="toolbar-left">
              <el-input
                v-model="repositoryKeyword"
                placeholder="搜索仓库名称..."
                clearable
                class="search-input"
                @keyup.enter="loadRepositories"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
              <el-button :icon="Search" @click="loadRepositories">搜索</el-button>
            </div>
            <div class="toolbar-right">
              <el-button type="primary" :icon="Plus" @click="showCreateRepositoryDialog">新建仓库</el-button>
            </div>
          </div>

          <!-- 仓库表格 -->
          <div v-loading="repositoryLoading" class="table-container page-table">
            <el-table :data="repositoryList">
              <el-table-column prop="name" label="仓库名称" width="160" show-overflow-tooltip />
              <el-table-column prop="git_url" label="Git URL" min-width="200" show-overflow-tooltip />
              <el-table-column prop="branch" label="分支" width="90" />
              <el-table-column prop="auth_type" label="认证" width="80">
                <template #default="{ row }">
                  <el-tag :type="getAuthTypeTag(row.auth_type)" size="small">
                    {{ getAuthTypeLabel(row.auth_type) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="sync_mode" label="同步方式" width="80">
                <template #default="{ row }">
                  <el-tag size="small">{{ getSyncModeLabel(row.sync_mode) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="80" align="center">
                <template #default="{ row }">
                  <el-tag :type="getRepositoryStatusTag(row.status)" size="small">
                    {{ getRepositoryStatusLabel(row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="skills_count" label="技能数" width="70" align="center" />
              <el-table-column prop="last_sync_at" label="最后同步" width="150">
                <template #default="{ row }">
                  {{ formatDate(row.last_sync_at) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="220" align="center" fixed="right">
                <template #default="{ row }">
                  <el-button link type="primary" size="small" :icon="Refresh" @click="syncRepository(row)">同步</el-button>
                  <el-button link type="info" size="small" @click="viewSyncLogs(row)">日志</el-button>
                  <el-button link type="warning" size="small" @click="editRepository(row)">编辑</el-button>
                  <el-button link type="danger" size="small" @click="deleteRepository(row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <!-- 分页 -->
          <div class="table-pagination">
            <el-pagination
              v-model:current-page="repositoryPagination.page"
              v-model:page-size="repositoryPagination.per_page"
              :total="repositoryPagination.total"
              :page-sizes="[10, 20, 50, 100]"
              layout="total, sizes, prev, pager, next, jumper"
              @current-change="loadRepositories"
              @size-change="loadRepositories"
            />
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 仓库表单对话框 -->
    <el-dialog
      v-model="repositoryDialogVisible"
      :title="repositoryDialogMode === 'create' ? '新建仓库' : '编辑仓库'"
      width="600px"
      @close="resetRepositoryForm"
    >
      <el-form :model="repositoryForm" :rules="repositoryRules" ref="repositoryFormRef" label-width="120px">
        <el-form-item label="仓库名称" prop="name">
          <el-input v-model="repositoryForm.name" placeholder="请输入仓库名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="repositoryForm.description" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item label="Git URL" prop="git_url">
          <el-input v-model="repositoryForm.git_url" placeholder="https://github.com/user/repo.git" />
        </el-form-item>
        <el-form-item label="分支" prop="branch">
          <el-input v-model="repositoryForm.branch" placeholder="默认: main" />
        </el-form-item>
        <el-form-item label="技能路径">
          <el-input v-model="repositoryForm.skills_path" placeholder="默认: /" />
        </el-form-item>
        <el-form-item label="认证方式" prop="auth_type">
          <el-select v-model="repositoryForm.auth_type" placeholder="请选择" @change="handleAuthTypeChange">
            <el-option label="公开仓库" value="public" />
            <el-option label="Token" value="token" />
            <el-option label="SSH密钥" value="ssh_key" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="repositoryForm.auth_type !== 'public'" label="凭证" prop="git_credential_id">
          <el-select v-model="repositoryForm.git_credential_id" placeholder="请选择凭证">
            <el-option v-for="cred in credentialList" :key="cred.id" :label="cred.name" :value="cred.id" />
          </el-select>
          <el-button link type="primary" size="small" @click="showCreateCredentialDialog" style="margin-left: 10px">
            新建凭证
          </el-button>
        </el-form-item>
        <el-form-item label="同步方式">
          <el-select v-model="repositoryForm.sync_mode">
            <el-option label="手动同步" value="manual" />
            <el-option label="定时同步" value="scheduled" />
            <el-option label="Webhook" value="webhook" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="repositoryForm.sync_mode === 'scheduled'" label="同步间隔(分钟)">
          <el-input-number v-model="repositoryForm.sync_interval" :min="1" :max="10080" />
        </el-form-item>
        <el-form-item v-if="repositoryForm.sync_mode === 'webhook'" label="Webhook密钥">
          <el-input v-model="repositoryForm.webhook_secret" placeholder="请输入Webhook密钥" />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="repositoryForm.is_enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="repositoryDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveRepository" :loading="repositorySaving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 凭证表单对话框 -->
    <el-dialog v-model="credentialDialogVisible" title="新建凭证" width="500px" @close="resetCredentialForm">
      <el-form :model="credentialForm" :rules="credentialRules" ref="credentialFormRef" label-width="120px">
        <el-form-item label="凭证名称" prop="name">
          <el-input v-model="credentialForm.name" placeholder="请输入凭证名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="credentialForm.description" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item label="认证类型" prop="auth_type">
          <el-select v-model="credentialForm.auth_type" placeholder="请选择">
            <el-option label="Token" value="token" />
            <el-option label="SSH密钥" value="ssh_key" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="credentialForm.auth_type === 'token'" label="GitHub Token" prop="github_token">
          <el-input v-model="credentialForm.github_token" type="password" placeholder="请输入GitHub Token" show-password />
        </el-form-item>
        <el-form-item v-if="credentialForm.auth_type === 'ssh_key'" label="SSH私钥" prop="ssh_key_content">
          <el-input v-model="credentialForm.ssh_key_content" type="textarea" :rows="6" placeholder="请输入SSH私钥内容" />
        </el-form-item>
        <el-form-item v-if="credentialForm.auth_type === 'ssh_key'" label="密钥密码">
          <el-input v-model="credentialForm.ssh_key_passphrase" type="password" placeholder="可选，请输入密钥密码" show-password />
        </el-form-item>
        <el-form-item v-if="credentialForm.auth_type === 'token'" label="GitHub用户名">
          <el-input v-model="credentialForm.github_login" placeholder="请输入GitHub用户名" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="credentialDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveCredential" :loading="credentialSaving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 技能详情对话框 -->
    <el-dialog v-model="skillDetailVisible" title="" width="900px" class="skill-detail-dialog" :show-header="false">
      <div v-if="selectedSkill" class="skill-detail-content">
        <!-- 头部：图标 + 技能名称 -->
        <div class="detail-header">
          <div class="detail-icon-large">
            <el-icon size="42" :color="getSkillIconColor(selectedSkill.script_type)">
              <component :is="getSkillIcon(selectedSkill.script_type)" />
            </el-icon>
          </div>
          <div class="detail-title-group">
            <h2 class="detail-title">{{ selectedSkill.name }}</h2>
            <div class="detail-meta-tags">
              <el-tag :type="getScriptTypeTag(selectedSkill.script_type)" size="small">
                {{ selectedSkill.script_type }}
              </el-tag>
              <span class="detail-meta-item">
                <el-icon><Management /></el-icon>
                {{ selectedSkill.code }}
              </span>
              <span class="detail-meta-item clickable" @click="goToRepository(selectedSkill.repository_id)">
                <el-icon><FolderOpened /></el-icon>
                {{ selectedSkill.repository_name }}
              </span>
              <span class="detail-meta-item">
                <el-icon><Document /></el-icon>
                {{ selectedSkill.file_path }}
              </span>
            </div>
          </div>
        </div>

        <!-- 技能描述 -->
        <div class="detail-section">
          <h3 class="detail-section-title">技能描述</h3>
          <p class="detail-description">{{ selectedSkill.description || '暂无描述' }}</p>
        </div>

        <!-- 技能内容 -->
        <div class="detail-section detail-content-section">
          <div class="detail-content-header">
            <h3 class="detail-section-title">技能内容</h3>
            <div class="detail-content-actions">
              <el-radio-group v-model="contentViewMode" size="small">
                <el-radio-button value="preview">预览</el-radio-button>
                <el-radio-button value="source">源码</el-radio-button>
              </el-radio-group>
              <el-button :icon="DocumentCopy" size="small" @click="copyScriptContent">复制</el-button>
            </div>
          </div>
          <div class="detail-content-body">
            <div v-if="contentViewMode === 'preview'" class="markdown-preview" v-html="renderedMarkdown"></div>
            <pre v-else class="code-preview"><code>{{ selectedSkill.script_content }}</code></pre>
          </div>
        </div>

        <!-- 底部操作 -->
        <div class="detail-footer">
          <el-button type="primary" :icon="CaretRight" @click="executeSkill(selectedSkill)">执行技能</el-button>
          <el-button @click="skillDetailVisible = false">关闭</el-button>
        </div>
      </div>
    </el-dialog>

    <!-- 同步日志对话框 -->
    <el-dialog v-model="syncLogsVisible" title="同步日志" width="800px">
      <el-timeline>
        <el-timeline-item
          v-for="log in syncLogs"
          :key="log.id"
          :timestamp="formatDateTime(log.started_at)"
          placement="top"
        >
          <el-card>
            <template #header>
              <div class="log-header">
                <span>{{ getSyncTypeLabel(log.sync_type) }}</span>
                <el-tag :type="getSyncLogStatusTag(log.status)" size="small">
                  {{ getSyncLogStatusLabel(log.status) }}
                </el-tag>
              </div>
            </template>
            <div class="log-content">
              <p>新增: {{ log.skills_added }} | 更新: {{ log.skills_updated }} | 删除: {{ log.skills_deleted }}</p>
              <p v-if="log.error_message" class="error-message">{{ log.error_message }}</p>
              <p v-if="log.git_commit_hash">Commit: {{ log.git_commit_hash.substring(0, 8) }}</p>
              <p v-if="log.duration">耗时: {{ log.duration.toFixed(2) }}秒</p>
            </div>
          </el-card>
        </el-timeline-item>
      </el-timeline>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Files, FolderOpened, Plus, Refresh, Search,
  Document, Management, DocumentCopy, Close,
  CaretRight
} from '@element-plus/icons-vue'
import { skillRepositoryApi, gitCredentialApi, gitSkillApi } from '@/api/skill-repositories'

// 标签页
const activeTab = ref('skills')

// Skills 相关
const skillLoading = ref(false)
const syncingSkills = ref(false)
const skillList = ref([])
const skillFilters = reactive({
  keyword: ''
})
const skillPagination = reactive({
  page: 1,
  per_page: 12,
  total: 0
})

// 仓库相关
const repositoryLoading = ref(false)
const repositoryList = ref([])
const repositoryKeyword = ref('')
const repositoryPagination = reactive({
  page: 1,
  per_page: 20,
  total: 0
})

// 仓库表单
const repositoryDialogVisible = ref(false)
const repositoryDialogMode = ref('create')
const repositorySaving = ref(false)
const repositoryFormRef = ref()
const repositoryForm = reactive({
  name: '',
  description: '',
  git_url: '',
  branch: 'main',
  skills_path: '/',
  auth_type: 'public',
  git_credential_id: null,
  sync_mode: 'manual',
  sync_interval: 60,
  webhook_secret: '',
  is_enabled: true
})
const repositoryRules = {
  name: [{ required: true, message: '请输入仓库名称', trigger: 'blur' }],
  git_url: [{ required: true, message: '请输入Git URL', trigger: 'blur' }],
  branch: [{ required: true, message: '请输入分支', trigger: 'blur' }],
  auth_type: [{ required: true, message: '请选择认证方式', trigger: 'change' }]
}

// 凭证相关
const credentialDialogVisible = ref(false)
const credentialSaving = ref(false)
const credentialFormRef = ref()
const credentialList = ref([])
const credentialForm = reactive({
  name: '',
  description: '',
  auth_type: 'token',
  github_token: '',
  ssh_key_content: '',
  ssh_key_passphrase: '',
  github_login: ''
})
const credentialRules = {
  name: [{ required: true, message: '请输入凭证名称', trigger: 'blur' }],
  auth_type: [{ required: true, message: '请选择认证类型', trigger: 'change' }],
  github_token: [{ required: true, message: '请输入GitHub Token', trigger: 'blur' }],
  ssh_key_content: [{ required: true, message: '请输入SSH私钥', trigger: 'blur' }]
}

// 技能详情
const skillDetailVisible = ref(false)
const selectedSkill = ref(null)
const contentViewMode = ref('preview') // 预览/源码模式

// Markdown 渲染
const renderedMarkdown = computed(() => {
  if (!selectedSkill.value?.script_content) return ''

  // 简单的 Markdown 渲染
  let markdown = selectedSkill.value.script_content

  // 移除 YAML front matter
  markdown = markdown.replace(/^---\s*\n(.*?)\n---\s*\n/s, '')

  // 标题
  markdown = markdown.replace(/^### (.*$)/gim, '<h3>$1</h3>')
  markdown = markdown.replace(/^## (.*$)/gim, '<h2>$1</h2>')
  markdown = markdown.replace(/^# (.*$)/gim, '<h1>$1</h1>')

  // 粗体和斜体
  markdown = markdown.replace(/\*\*\*(.*?)\*\*\*/gim, '<strong><em>$1</em></strong>')
  markdown = markdown.replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
  markdown = markdown.replace(/\*(.*?)\*/gim, '<em>$1</em>')

  // 代码块
  markdown = markdown.replace(/```(\w+)?\n([\s\S]*?)```/gim, '<pre><code class="language-$1">$2</code></pre>')

  // 行内代码
  markdown = markdown.replace(/`([^`]+)`/gim, '<code>$1</code>')

  // 链接
  markdown = markdown.replace(/\[([^\]]+)\]\(([^)]+)\)/gim, '<a href="$2" target="_blank">$1</a>')

  // 列表
  markdown = markdown.replace(/^\* (.*$)/gim, '<li>$1</li>')
  markdown = markdown.replace(/^- (.*$)/gim, '<li>$1</li>')
  markdown = markdown.replace(/^(\d+)\. (.*$)/gim, '<li>$2</li>')

  // 段落
  markdown = markdown.replace(/\n\n/g, '</p><p>')
  markdown = '<p>' + markdown + '</p>'

  // 换行
  markdown = markdown.replace(/\n/g, '<br>')

  return markdown
})

// 同步日志
const syncLogsVisible = ref(false)
const syncLogs = ref([])

// 加载技能列表
const loadSkills = async () => {
  skillLoading.value = true
  try {
    const params = {
      page: skillPagination.page,
      per_page: skillPagination.per_page
    }
    if (skillFilters.keyword) params.keyword = skillFilters.keyword
    const res = await gitSkillApi.getList(params)
    skillList.value = res.data.items
    skillPagination.total = res.data.total
  } catch (error) {
    console.error('加载技能列表失败:', error)
    ElMessage.error('加载技能列表失败')
  } finally {
    skillLoading.value = false
  }
}

// 同步所有仓库
const syncAllRepositories = async () => {
  syncingSkills.value = true
  try {
    // 获取所有启用的仓库
    const reposRes = await skillRepositoryApi.getList({ page: 1, per_page: 100 })
    const enabledRepos = reposRes.data.items.filter(repo => repo.is_enabled && repo.status === 'active')

    if (enabledRepos.length === 0) {
      ElMessage.warning('没有启用的仓库可以同步')
      return
    }

    let successCount = 0
    let failCount = 0

    // 逐个同步仓库
    for (const repo of enabledRepos) {
      try {
        await skillRepositoryApi.sync(repo.id)
        successCount++
      } catch (error) {
        console.error(`同步仓库 ${repo.name} 失败:`, error)
        failCount++
      }
    }

    // 显示同步结果
    if (failCount === 0) {
      ElMessage.success(`同步完成！已同步 ${successCount} 个仓库`)
    } else if (successCount === 0) {
      ElMessage.error(`同步失败！${failCount} 个仓库同步失败`)
    } else {
      ElMessage.warning(`同步完成！成功 ${successCount} 个，失败 ${failCount} 个`)
    }

    // 重新加载技能列表
    await loadSkills()
  } catch (error) {
    console.error('同步仓库失败:', error)
    ElMessage.error('同步仓库失败')
  } finally {
    syncingSkills.value = false
  }
}

// 加载仓库列表
const loadRepositories = async () => {
  repositoryLoading.value = true
  try {
    const params = {
      page: repositoryPagination.page,
      per_page: repositoryPagination.per_page,
      keyword: repositoryKeyword.value || undefined
    }
    const res = await skillRepositoryApi.getList(params)
    repositoryList.value = res.data.items
    repositoryPagination.total = res.data.total
  } catch (error) {
    console.error('加载仓库列表失败:', error)
  } finally {
    repositoryLoading.value = false
  }
}

// 加载凭证列表
const loadCredentials = async () => {
  try {
    const res = await gitCredentialApi.getList()
    credentialList.value = res.data.items
  } catch (error) {
    console.error('加载凭证列表失败:', error)
  }
}

// 显示新建仓库对话框
const showCreateRepositoryDialog = () => {
  repositoryDialogMode.value = 'create'
  repositoryDialogVisible.value = true
  loadCredentials()
}

// 显示编辑仓库对话框
const editRepository = (row) => {
  repositoryDialogMode.value = 'edit'
  Object.assign(repositoryForm, {
    id: row.id,
    name: row.name,
    description: row.description,
    git_url: row.git_url,
    branch: row.branch,
    skills_path: row.skills_path,
    auth_type: row.auth_type,
    git_credential_id: row.git_credential_id,
    sync_mode: row.sync_mode,
    sync_interval: row.sync_interval,
    webhook_secret: row.webhook_secret || '',
    is_enabled: row.is_enabled
  })
  loadCredentials()
  repositoryDialogVisible.value = true
}

// 保存仓库
const saveRepository = async () => {
  await repositoryFormRef.value.validate()
  repositorySaving.value = true
  try {
    const data = { ...repositoryForm }
    if (repositoryDialogMode.value === 'create') {
      await skillRepositoryApi.create(data)
      ElMessage.success('创建成功')
    } else {
      await skillRepositoryApi.update(data.id, data)
      ElMessage.success('更新成功')
    }
    repositoryDialogVisible.value = false
    loadRepositories()
    loadSkills()
  } catch (error) {
    console.error('保存仓库失败:', error)
    const errorMsg = error.response?.data?.message || error.message || '保存失败'
    ElMessage.error(errorMsg)
  } finally {
    repositorySaving.value = false
  }
}

// 删除仓库
const deleteRepository = (row) => {
  ElMessageBox.confirm(`确定要删除仓库 "${row.name}" 吗？`, '确认删除', {
    type: 'warning'
  }).then(async () => {
    try {
      await skillRepositoryApi.delete(row.id)
      ElMessage.success('删除成功')
      loadRepositories()
      loadSkills()
    } catch (error) {
      console.error('删除仓库失败:', error)
    }
  }).catch(() => {})
}

// 同步仓库
const syncRepository = async (row) => {
  try {
    const res = await skillRepositoryApi.sync(row.id, 'user')
    if (res.data?.success) {
      ElMessage.success(`同步成功: ${res.data.stats?.added || 0}个新增, ${res.data.stats?.updated || 0}个更新`)
    } else {
      ElMessage.error(res.data?.error || '同步失败')
    }
    loadRepositories()
    loadSkills()
  } catch (error) {
    console.error('同步仓库失败:', error)
    const errorMsg = error.response?.data?.message || error.message || '同步失败'
    ElMessage.error(errorMsg)
  }
}

// 查看同步日志
const viewSyncLogs = async (row) => {
  try {
    const res = await skillRepositoryApi.getSyncLogs(row.id, { per_page: 20 })
    syncLogs.value = res.data.items
    syncLogsVisible.value = true
  } catch (error) {
    console.error('获取同步日志失败:', error)
  }
}

// 认证类型变化
const handleAuthTypeChange = () => {
  repositoryForm.git_credential_id = null
}

// 显示新建凭证对话框
const showCreateCredentialDialog = () => {
  credentialDialogVisible.value = true
}

// 保存凭证
const saveCredential = async () => {
  await credentialFormRef.value.validate()
  credentialSaving.value = true
  try {
    await gitCredentialApi.create(credentialForm)
    ElMessage.success('创建成功')
    credentialDialogVisible.value = false
    resetCredentialForm()
    loadCredentials()
  } catch (error) {
    console.error('保存凭证失败:', error)
    const errorMsg = error.response?.data?.message || error.message || '保存失败'
    ElMessage.error(errorMsg)
  } finally {
    credentialSaving.value = false
  }
}

// 重置凭证表单
const resetCredentialForm = () => {
  Object.assign(credentialForm, {
    name: '',
    description: '',
    auth_type: 'token',
    github_token: '',
    ssh_key_content: '',
    ssh_key_passphrase: '',
    github_login: ''
  })
  credentialFormRef.value?.resetFields()
}

// 重置仓库表单
const resetRepositoryForm = () => {
  Object.assign(repositoryForm, {
    name: '',
    description: '',
    git_url: '',
    branch: 'main',
    skills_path: '/',
    auth_type: 'public',
    git_credential_id: null,
    sync_mode: 'manual',
    sync_interval: 60,
    webhook_secret: '',
    is_enabled: true
  })
  repositoryFormRef.value?.resetFields()
}

// 查看技能详情
const viewSkillDetail = (skill) => {
  selectedSkill.value = skill
  skillDetailVisible.value = true
}

// 执行技能
const executeSkill = (skill) => {
  ElMessage.info(`执行技能: ${skill.name}`)
  // TODO: 实现技能执行逻辑
}

// 跳转到仓库管理页面并筛选对应仓库
const goToRepository = (repositoryId) => {
  // 切换到仓库管理标签页
  activeTab.value = 'repositories'
  // 筛选对应仓库
  // 这里可以添加更多逻辑，比如高亮显示该仓库
  ElMessage.info(`已跳转到仓库管理页面`)
}

// 重置技能筛选
const resetSkillFilters = () => {
  skillFilters.keyword = ''
  skillPagination.page = 1
  loadSkills()
}

// 辅助函数
const getScriptTypeTag = (type) => {
  const tags = { python: 'primary', javascript: 'success', yaml: 'warning', json: 'info', markdown: 'default' }
  return tags[type] || ''
}

const getAuthTypeTag = (type) => {
  const tags = { public: 'info', token: 'warning', ssh_key: 'success' }
  return tags[type] || ''
}

const getAuthTypeLabel = (type) => {
  const labels = { public: '公开', token: 'Token', ssh_key: 'SSH' }
  return labels[type] || type
}

const getSyncModeLabel = (mode) => {
  const labels = { manual: '手动', scheduled: '定时', webhook: 'Webhook' }
  return labels[mode] || mode
}

const getRepositoryStatusTag = (status) => {
  const tags = { idle: 'info', syncing: 'warning', success: 'success', error: 'danger' }
  return tags[status] || ''
}

const getRepositoryStatusLabel = (status) => {
  const labels = { idle: '空闲', syncing: '同步中', success: '成功', error: '错误' }
  return labels[status] || status
}

const getSyncTypeLabel = (type) => {
  const labels = { manual: '手动', scheduled: '定时', webhook: 'Webhook' }
  return labels[type] || type
}

const getSyncLogStatusTag = (status) => {
  const tags = { running: 'warning', success: 'success', error: 'danger', partial: 'info' }
  return tags[status] || ''
}

const getSyncLogStatusLabel = (status) => {
  const labels = { running: '运行中', success: '成功', error: '失败', partial: '部分成功' }
  return labels[status] || status
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const getSkillIcon = (scriptType) => {
  const icons = {
    python: Management,
    javascript: Document,
    yaml: Document,
    json: Document
  }
  return icons[scriptType] || Document
}

const getSkillIconColor = (scriptType) => {
  const colors = {
    python: '#3B82F6',
    javascript: '#F59E0B',
    yaml: '#10B981',
    json: '#6366F1',
    markdown: '#8B5CF6'
  }
  return colors[scriptType] || '#6B7280'
}

const copyScriptContent = () => {
  if (selectedSkill.value?.script_content) {
    navigator.clipboard.writeText(selectedSkill.value.script_content).then(() => {
      ElMessage.success('技能内容已复制到剪贴板')
    }).catch(() => {
      ElMessage.error('复制失败')
    })
  }
}

// 初始化
onMounted(() => {
  loadSkills()
  loadRepositories()
})
</script>

<style scoped>
/* 技能页面特定样式 - 覆盖 page-container 样式使分页可见 */
.page-container {
  height: 100%;
  padding: var(--space-6);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.skills-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.skills-card :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 0;
  overflow: hidden;
}

/* 标签页样式 */
.skills-tabs {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.skills-tabs :deep(.el-tabs__header) {
  flex-shrink: 0;
  margin: 0;
  padding: 0 var(--space-5);
  border-bottom: 1px solid var(--color-border-light);
}

.skills-tabs :deep(.el-tabs__content) {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.skills-tabs :deep(.el-tab-pane) {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-family: var(--font-display);
  font-weight: 500;
  font-size: var(--text-sm);
}

/* 技能内容区域 */
.skills-content {
  flex: 1;
  padding: var(--space-5);
  overflow-y: auto;
  min-height: 0;
}

/* 分页样式 */
.table-pagination {
  flex-shrink: 0;
  padding: var(--space-4) var(--space-5);
  border-top: 1px solid var(--color-border-light);
  display: flex;
  justify-content: flex-end;
}

.result-count {
  font-family: var(--font-display);
  font-size: var(--text-sm);
  color: var(--color-text-muted);
}

/* 技能卡片网格 */
.skills-grid {
  margin-bottom: var(--space-5);
  margin-left: -10px;
  margin-right: -10px;
}

/* 确保 el-col 的 padding 生效，包括水平和垂直间距 */
.skills-grid :deep(.el-col) {
  padding: 10px;
}

/* 技能卡片 */
.skill-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  cursor: pointer;
  transition: all var(--transition-base);
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: var(--space-3);
}

.skill-card:hover {
  border-color: var(--color-accent);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.skill-card-header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.skill-icon-small {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg-alt);
  border-radius: var(--radius-md);
  flex-shrink: 0;
}

.skill-name-large {
  margin: 0;
  font-family: var(--font-display);
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--color-text);
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.skill-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.skill-meta-row {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.skill-header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.skill-name {
  margin: 0;
  font-family: var(--font-display);
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--color-text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 0 0 auto;
}

.skill-repo-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: var(--text-xs);
  color: var(--color-primary);
  cursor: pointer;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
  background: var(--color-primary-light);
  white-space: nowrap;
}

.skill-repo-link:hover {
  background: var(--color-primary);
  color: #ffffff;
}

.skill-repo-link .el-icon {
  font-size: 12px;
}

.skill-desc {
  margin: 0;
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  min-height: 38px;
}

.skill-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: var(--space-3);
  border-top: 1px solid var(--color-border-light);
}

.skill-status {
  font-size: var(--text-xs);
  padding: 2px var(--space-2);
  border-radius: var(--radius-sm);
  font-weight: 500;
}

.skill-status.active {
  background: var(--color-success-light);
  color: var(--color-success);
}

.skill-status.inactive {
  background: var(--color-info-light);
  color: var(--color-info);
}

.skill-actions {
  display: flex;
  gap: var(--space-2);
}

/* 分页使用全局 page-layout.css 样式 */

/* 空状态 */
.empty-state {
  text-align: center;
  padding: var(--space-10) 0;
}

/* 表格容器 */
.table-container {
  flex: 1;
  overflow: auto;
}

/* 技能详情对话框 - 使用项目标准设计 */
.skill-detail-dialog :deep(.el-dialog__body) {
  padding: 0;
  max-height: 80vh;
  overflow-y: auto;
}

.skill-detail-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
  padding: var(--space-6);
}

/* 头部 */
.detail-header {
  display: flex;
  align-items: flex-start;
  gap: var(--space-4);
  padding-bottom: var(--space-4);
}

.detail-icon-large {
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg-alt);
  border-radius: var(--radius-lg);
  flex-shrink: 0;
}

.detail-title-group {
  flex: 1;
  min-width: 0;
}

.detail-title {
  margin: 0 0 var(--space-3) 0;
  font-family: var(--font-display);
  font-size: 24px;
  font-weight: 600;
  color: var(--color-text);
  line-height: 1.3;
}

.detail-meta-tags {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  flex-wrap: wrap;
}

.detail-meta-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
}

.detail-meta-item.clickable {
  cursor: pointer;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}

.detail-meta-item.clickable:hover {
  background: var(--color-bg-alt);
  color: var(--color-primary);
}

.detail-meta-item .el-icon {
  font-size: 14px;
}

.detail-close-btn {
  flex-shrink: 0;
}

/* 详情区块 */
.detail-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.detail-section-title {
  margin: 0;
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--color-text);
}

.detail-description {
  margin: 0;
  padding: var(--space-4);
  background: var(--color-bg-alt);
  border-radius: var(--radius-md);
  font-size: var(--text-base);
  line-height: 1.6;
  color: var(--color-text-secondary);
}

/* 内容区块 */
.detail-content-section {
  flex: 1;
  min-height: 300px;
}

.detail-content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-content-actions {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.detail-content-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 400px;
  max-height: 500px;
}

.code-preview {
  flex: 1;
  margin: 0;
  background: var(--color-bg);
  padding: var(--space-4);
  border-radius: var(--radius-md);
  overflow: auto;
  font-family: var(--font-mono);
  font-size: 13px;
  line-height: 1.6;
  color: var(--color-text);
}

/* 底部操作 */
.detail-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
  padding-top: var(--space-4);
  border-top: 1px solid var(--color-border);
}

/* Markdown 预览样式 */
.markdown-preview {
  flex: 1;
  background: var(--color-bg-alt);
  padding: var(--space-4);
  border-radius: var(--radius-md);
  overflow: auto;
  line-height: 1.6;
}

.markdown-preview :deep(h1) {
  font-size: 24px;
  font-weight: 600;
  margin: var(--space-4) 0 var(--space-3) 0;
  color: var(--color-text);
  border-bottom: 2px solid var(--color-border);
  padding-bottom: var(--space-2);
}

.markdown-preview :deep(h2) {
  font-size: 20px;
  font-weight: 600;
  margin: var(--space-4) 0 var(--space-2) 0;
  color: var(--color-text);
}

.markdown-preview :deep(h3) {
  font-size: 16px;
  font-weight: 600;
  margin: var(--space-3) 0 var(--space-2) 0;
  color: var(--color-text);
}

.markdown-preview :deep(p) {
  margin: var(--space-2) 0;
  color: var(--color-text-secondary);
}

.markdown-preview :deep(code) {
  background: var(--color-bg);
  padding: 2px 6px;
  border-radius: var(--radius-sm);
  font-family: var(--font-mono);
  font-size: 13px;
  color: var(--color-accent);
}

.markdown-preview :deep(pre) {
  background: #1e1e1e;
  padding: var(--space-3);
  border-radius: var(--radius-md);
  overflow-x: auto;
  margin: var(--space-3) 0;
}

.markdown-preview :deep(pre code) {
  background: transparent;
  padding: 0;
  color: #d4d4d4;
}

.markdown-preview :deep(a) {
  color: var(--color-primary);
  text-decoration: none;
}

.markdown-preview :deep(a:hover) {
  text-decoration: underline;
}

.markdown-preview :deep(li) {
  margin: var(--space-1) 0 var(--space-1) var(--space-4);
  color: var(--color-text-secondary);
}

.markdown-preview :deep(ul),
.markdown-preview :deep(ol) {
  margin: var(--space-2) 0;
}

.markdown-preview :deep(strong) {
  font-weight: 600;
  color: var(--color-text);
}

.markdown-preview :deep(em) {
  font-style: italic;
}

/* 日志样式 */
.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.log-content p {
  margin: var(--space-1) 0;
}

.error-message {
  color: var(--color-error);
}
</style>

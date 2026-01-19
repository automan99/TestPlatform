<template>
  <div class="projects-container">
    <!-- Page Header -->
    <div class="page-section animate-fade-in-up">
      <div class="section-header">
        <div class="header-main">
          <h1 class="page-title">{{ t('project.title') }}</h1>
          <p class="page-subtitle">{{ t('project.title') }}</p>
        </div>
        <div class="header-actions">
          <el-button type="primary" :icon="Plus" @click="showCreateDialog">
            {{ t('common.create') }}
          </el-button>
        </div>
      </div>
    </div>

    <!-- Projects Grid -->
    <div v-if="projectList.length > 0" class="projects-grid">
      <div
        v-for="(project, index) in projectList"
        :key="project.id"
        class="project-card animate-fade-in-up"
        :class="`animate-delay-${(index % 6) + 1}`"
        @click="handleEdit(project)"
      >
        <!-- Card Header -->
        <div class="card-header">
          <div class="header-left">
            <div class="project-badge" :style="{ backgroundColor: project.color || 'var(--color-accent)' }">
              <span v-if="project.icon">{{ project.icon }}</span>
              <span v-else>{{ project.name.charAt(0) }}</span>
            </div>
            <div class="header-info">
              <h3 class="card-title">{{ project.name }}</h3>
              <div class="card-meta-row">
                <span class="meta-tag" :class="`type-${project.project_type}`">
                  {{ getProjectTypeText(project.project_type) }}
                </span>
                <span class="meta-tag" :class="`status-${project.status}`">
                  {{ getProjectStatusText(project.status) }}
                </span>
              </div>
            </div>
          </div>
          <el-dropdown trigger="click" @click.stop>
            <el-icon class="card-more"><MoreFilled /></el-icon>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item :icon="Edit" @click.stop="handleEdit(project)">
                  {{ t('common.edit') }}
                </el-dropdown-item>
                <el-dropdown-item :icon="Delete" @click.stop="handleDelete(project)">
                  {{ t('common.delete') }}
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>

        <!-- Card Body -->
        <div class="card-body">
          <p class="card-code">{{ project.code }}</p>

          <!-- Stats -->
          <div class="card-stats">
            <div class="stat-group">
              <div class="stat-indicator stat-primary">
                <el-icon><Document /></el-icon>
              </div>
              <div class="stat-content">
                <span class="stat-number">{{ project.test_case_count || 0 }}</span>
                <span class="stat-label">{{ t('testCase.title') }}</span>
              </div>
            </div>
            <div class="stat-group">
              <div class="stat-indicator stat-success">
                <el-icon><Calendar /></el-icon>
              </div>
              <div class="stat-content">
                <span class="stat-number">{{ project.test_plan_count || 0 }}</span>
                <span class="stat-label">{{ t('testPlan.title') }}</span>
              </div>
            </div>
            <div class="stat-group">
              <div class="stat-indicator stat-error">
                <el-icon><CircleClose /></el-icon>
              </div>
              <div class="stat-content">
                <span class="stat-number">{{ project.defect_count || 0 }}</span>
                <span class="stat-label">{{ t('defect.title') }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="!loading" class="empty-state animate-fade-in">
      <div class="empty-illustration">
        <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
          <rect x="4" y="4" width="56" height="56" rx="8" stroke="currentColor" stroke-width="1.5" stroke-dasharray="4 4"/>
          <path d="M22 32L32 22L42 32M22 42L32 32L42 42" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      <h3 class="empty-title">{{ t('common.noData') }}</h3>
      <p class="empty-description">{{ t('project.title') }}</p>
      <el-button type="primary" :icon="Plus" @click="showCreateDialog">
        {{ t('project.create') }}
      </el-button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p class="loading-text">{{ t('common.loading') }}</p>
    </div>

    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'create' ? t('project.create') : t('project.edit')"
      width="540px"
      destroy-on-close
      @close="handleDialogClose"
    >
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="90px">
        <el-form-item :label="t('project.name')" prop="name">
          <el-input v-model="formData.name" :placeholder="t('project.name')" />
        </el-form-item>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item :label="t('project.code')" prop="code">
              <el-input
                v-model="formData.code"
                :placeholder="t('project.code')"
                :disabled="dialogMode === 'edit'"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('project.key')" prop="key">
              <el-input
                v-model="formData.key"
                :placeholder="t('project.key')"
                maxlength="10"
                show-word-limit
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item :label="t('project.projectType')" prop="project_type">
              <el-select v-model="formData.project_type" :placeholder="t('project.projectType')" style="width: 100%">
                <el-option :label="t('project.typeWeb')" value="web" />
                <el-option :label="t('project.typeMobile')" value="mobile" />
                <el-option :label="t('project.typeApi')" value="api" />
                <el-option :label="t('project.typeDesktop')" value="desktop" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('project.status')" prop="status">
              <el-select v-model="formData.status" :placeholder="t('project.status')" style="width: 100%">
                <el-option :label="t('project.statusActive')" value="active" />
                <el-option :label="t('project.statusArchived')" value="archived" />
                <el-option :label="t('project.statusCompleted')" value="completed" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item :label="t('common.description')">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            :placeholder="t('project.description')"
          />
        </el-form-item>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item :label="t('project.url')">
              <el-input v-model="formData.url" :placeholder="t('project.url')" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('project.repository')">
              <el-input v-model="formData.repository" :placeholder="t('project.repository')" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item :label="t('project.owner')">
              <el-input v-model="formData.owner" :placeholder="t('project.owner')" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('project.lead')">
              <el-input v-model="formData.lead" :placeholder="t('project.lead')" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item :label="t('project.color')">
              <div class="color-input">
                <el-color-picker v-model="formData.color" show-alpha />
                <span class="color-value">{{ formData.color || '#228be6' }}</span>
              </div>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('project.icon')">
              <el-input v-model="formData.icon" :placeholder="t('project.icon')" maxlength="2" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          {{ dialogMode === 'create' ? t('common.create') : t('common.save') }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, MoreFilled, Document, Calendar, CircleClose } from '@element-plus/icons-vue'
import { projectApi } from '@/api/project'
import { useI18n } from '@/i18n'

const { t } = useI18n()

const loading = ref(false)
const submitting = ref(false)
const projectList = ref([])
const dialogVisible = ref(false)
const dialogMode = ref('create')
const formRef = ref(null)
const currentProjectId = ref(null)

const searchForm = reactive({
  keyword: '',
  status: ''
})

const showAdvancedSearch = ref(false)
const advancedSearchForm = reactive({
  code: '',
  name: '',
  key: '',
  project_type: '',
  status: '',
  keyword: '',
  created_at: null,
  updated_at: null
})

const pagination = reactive({
  page: 1,
  per_page: 10,
  total: 0
})

const formData = reactive({
  name: '',
  code: '',
  key: '',
  description: '',
  project_type: 'web',
  url: '',
  repository: '',
  status: 'active',
  owner: '',
  lead: '',
  color: '#228be6',
  icon: ''
})

const formRules = {
  name: [{ required: true, message: t('project.name') + ' ' + t('common.required'), trigger: 'blur' }],
  code: [{ required: true, message: t('project.code') + ' ' + t('common.required'), trigger: 'blur' }],
  project_type: [{ required: true, message: t('project.projectType') + ' ' + t('common.required'), trigger: 'change' }],
  status: [{ required: true, message: t('project.status') + ' ' + t('common.required'), trigger: 'change' }]
}

function getProjectTypeText(type) {
  const map = {
    web: t('project.typeWeb'),
    mobile: t('project.typeMobile'),
    api: t('project.typeApi'),
    desktop: t('project.typeDesktop')
  }
  return map[type] || type
}

function getProjectStatusText(status) {
  const map = {
    active: t('project.statusActive'),
    archived: t('project.statusArchived'),
    completed: t('project.statusCompleted')
  }
  return map[status] || status
}

const fetchProjects = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      per_page: pagination.per_page
    }

    if (searchForm.keyword) {
      params.name = searchForm.keyword
    }
    if (searchForm.status) {
      params.status = searchForm.status
    }

    const res = await projectApi.getList(params)
    if (res.code === 200) {
      projectList.value = res.data.items
      pagination.total = res.data.total
    }
  } catch (error) {
    ElMessage.error(t('common.error') || 'Error')
  } finally {
    loading.value = false
  }
}

const showCreateDialog = () => {
  dialogMode.value = 'create'
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogMode.value = 'edit'
  currentProjectId.value = row.id
  Object.assign(formData, {
    name: row.name,
    code: row.code,
    key: row.key,
    description: row.description,
    project_type: row.project_type,
    url: row.url,
    repository: row.repository,
    status: row.status,
    owner: row.owner,
    lead: row.lead,
    color: row.color,
    icon: row.icon
  })
  dialogVisible.value = true
}

const handleDelete = (row) => {
  ElMessageBox.confirm(t('project.deleteConfirm'), t('common.confirm'), {
    confirmButtonText: t('common.confirm'),
    cancelButtonText: t('common.cancel'),
    type: 'warning'
  }).then(async () => {
    try {
      const res = await projectApi.delete(row.id)
      if (res.code === 200) {
        ElMessage.success(t('project.deleteSuccess'))
        fetchProjects()
      }
    } catch (error) {
      ElMessage.error(t('common.error') || 'Error')
    }
  })
}

const handleSubmit = async () => {
  await formRef.value.validate()
  submitting.value = true
  try {
    const data = { ...formData }
    if (dialogMode.value === 'create') {
      const res = await projectApi.create(data)
      if (res.code === 200) {
        ElMessage.success(t('project.createSuccess'))
        dialogVisible.value = false
        fetchProjects()
      }
    } else {
      const res = await projectApi.update(currentProjectId.value, data)
      if (res.code === 200) {
        ElMessage.success(t('project.updateSuccess'))
        dialogVisible.value = false
        fetchProjects()
      }
    }
  } catch (error) {
    ElMessage.error(t('common.error') || 'Error')
  } finally {
    submitting.value = false
  }
}

const handleDialogClose = () => {
  resetForm()
  formRef.value?.clearValidate()
}

const resetForm = () => {
  Object.assign(formData, {
    name: '',
    code: '',
    key: '',
    description: '',
    project_type: 'web',
    url: '',
    repository: '',
    status: 'active',
    owner: '',
    lead: '',
    color: '#228be6',
    icon: ''
  })
  currentProjectId.value = null
}

onMounted(() => {
  fetchProjects()
})
</script>

<style scoped>
/* ========================================
   CONTAINER
   ======================================== */
.projects-container {
  width: 100%;
}

/* ========================================
   PAGE SECTION
   ======================================== */
.page-section {
  margin-bottom: var(--space-6);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.header-main {
  flex: 1;
}

.page-title {
  font-family: var(--font-display);
  font-size: var(--text-3xl);
  font-weight: 600;
  color: var(--color-text);
  margin: 0 0 var(--space-1) 0;
  line-height: 1.2;
}

.page-subtitle {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: var(--space-3);
}

/* ========================================
   PROJECTS GRID - FLAT NO BORDER
   ======================================== */
.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--space-5);
}

.project-card {
  position: relative;
  background: var(--color-surface);
  border: none;
  border-radius: var(--radius-md);
  overflow: hidden;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.project-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

/* Card Header */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: var(--space-4);
  border-bottom: 1px solid var(--color-border-light);
  gap: var(--space-3);
}

.header-left {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  flex: 1;
  min-width: 0;
}

.header-info {
  flex: 1;
  min-width: 0;
}

.project-badge {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-accent);
  border-radius: var(--radius-sm);
  color: #ffffff;
  font-family: var(--font-display);
  font-size: var(--text-lg);
  font-weight: 600;
}

.card-more {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  color: var(--color-text-muted);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.card-more:hover {
  background: var(--color-bg-alt);
  color: var(--color-text);
}

/* Card Body */
.card-body {
  padding: var(--space-4);
  padding-top: var(--space-3);
}

.card-title {
  font-family: var(--font-display);
  font-size: var(--text-md);
  font-weight: 600;
  color: var(--color-text);
  margin: 0 0 var(--space-2) 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-meta-row {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.card-code {
  font-family: var(--font-display);
  font-size: var(--text-xs);
  font-weight: 500;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0 0 var(--space-4) 0;
}

.meta-tag {
  font-family: var(--font-display);
  font-size: var(--text-xs);
  font-weight: 500;
  padding: 2px var(--space-2);
  border-radius: var(--radius-sm);
}

.meta-tag.type-web {
  background: var(--color-accent-light);
  color: var(--color-accent);
}

.meta-tag.type-mobile {
  background: var(--color-success-light);
  color: var(--color-success);
}

.meta-tag.type-api {
  background: var(--color-warning-light);
  color: var(--color-warning);
}

.meta-tag.type-desktop {
  background: var(--color-bg-alt);
  color: var(--color-text-secondary);
}

.meta-tag.status-active {
  background: var(--color-success-light);
  color: var(--color-success);
}

.meta-tag.status-archived {
  background: var(--color-bg-alt);
  color: var(--color-text-secondary);
}

.meta-tag.status-completed {
  background: var(--color-warning-light);
  color: var(--color-warning);
}

/* Stats */
.card-stats {
  display: flex;
  gap: var(--space-4);
}

.stat-group {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  flex: 1;
}

.stat-indicator {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  font-size: var(--text-md);
  flex-shrink: 0;
}

.stat-primary {
  background: var(--color-accent-light);
  color: var(--color-accent);
}

.stat-success {
  background: var(--color-success-light);
  color: var(--color-success);
}

.stat-error {
  background: var(--color-error-light);
  color: var(--color-error);
}

.stat-content {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.stat-number {
  font-family: var(--font-display);
  font-size: var(--text-md);
  font-weight: 600;
  color: var(--color-text);
  line-height: 1;
}

.stat-label {
  font-family: var(--font-body);
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  font-weight: 500;
}

/* ========================================
   EMPTY STATE
   ======================================== */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-10) var(--space-4);
  text-align: center;
}

.empty-illustration {
  width: 64px;
  height: 64px;
  color: var(--color-text-muted);
  opacity: 0.4;
  margin-bottom: var(--space-5);
}

.empty-title {
  font-family: var(--font-display);
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--color-text);
  margin: 0 0 var(--space-2) 0;
}

.empty-description {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  margin: 0 0 var(--space-5) 0;
  max-width: 320px;
}

/* ========================================
   LOADING STATE
   ======================================== */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-10) var(--space-4);
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: var(--space-4);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  font-family: var(--font-display);
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  font-weight: 500;
}

/* ========================================
   COLOR INPUT
   ======================================== */
.color-input {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.color-value {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  font-weight: 500;
  color: var(--color-text-secondary);
}

/* ========================================
   RESPONSIVE
   ======================================== */
@media (max-width: 768px) {
  .page-title {
    font-size: var(--text-2xl);
  }

  .projects-grid {
    grid-template-columns: 1fr;
  }

  .section-header {
    flex-direction: column;
    gap: var(--space-4);
  }

  .card-stats {
    flex-wrap: wrap;
  }
}
</style>

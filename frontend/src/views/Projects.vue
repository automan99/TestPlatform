<template>
  <div class="page-container">
    <div class="main-content animate-fade-in-up">
      <!-- Toolbar -->
      <div class="toolbar">
        <div class="toolbar-left">
          <el-input
            v-model="searchForm.keyword"
            :placeholder="t('project.searchPlaceholder', '搜索项目名称...')"
            clearable
            class="search-input"
            @change="loadProjects"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button :icon="Search" @click="showAdvancedSearch = true">{{ t('common.advanced', '高级搜索') }}</el-button>
        </div>
        <div class="toolbar-right">
          <el-button type="primary" :icon="Plus" @click="handleCreate">{{ t('project.create', '新建项目') }}</el-button>
        </div>
      </div>

      <!-- Projects Grid -->
      <div v-if="projectList.length > 0" class="projects-grid">
        <div
          v-for="(project, index) in projectList"
          :key="project.id"
          class="project-card animate-fade-in-up"
          :class="`animate-delay-${(index % 6) + 1}`"
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
                <p class="card-code">{{ project.code }}</p>
                <!-- Meta Tags -->
                <div class="header-meta">
                  <span class="meta-tag" :class="`type-${project.project_type}`">
                    {{ getProjectTypeText(project.project_type) }}
                  </span>
                  <span class="meta-tag" :class="`status-${project.status}`">
                    {{ getProjectStatusText(project.status) }}
                  </span>
                </div>
              </div>
            </div>
            <el-dropdown trigger="click">
              <el-icon class="card-more"><MoreFilled /></el-icon>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item :icon="Edit" @click="handleEdit(project)">
                    {{ t('common.edit', '编辑') }}
                  </el-dropdown-item>
                  <el-dropdown-item :icon="Delete" @click="handleDelete(project)">
                    {{ t('common.delete', '删除') }}
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>

          <!-- Card Body -->
          <div class="card-body">
            <!-- Stats -->
            <div class="card-stats">
              <div class="stat-item">
                <el-icon class="stat-icon stat-primary"><Document /></el-icon>
                <span class="stat-number">{{ project.test_case_count || 0 }}</span>
                <span class="stat-label">{{ t('testCase.title', '用例') }}</span>
              </div>
              <div class="stat-item">
                <el-icon class="stat-icon stat-success"><Calendar /></el-icon>
                <span class="stat-number">{{ project.test_plan_count || 0 }}</span>
                <span class="stat-label">{{ t('testPlan.title', '计划') }}</span>
              </div>
              <div class="stat-item">
                <el-icon class="stat-icon stat-error"><CircleClose /></el-icon>
                <span class="stat-number">{{ project.defect_count || 0 }}</span>
                <span class="stat-label">{{ t('defect.title', '缺陷') }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else-if="!loading" class="empty-state animate-fade-in">
        <el-icon class="empty-icon"><FolderOpened /></el-icon>
        <h3 class="empty-title">{{ t('project.noProjects', '暂无项目') }}</h3>
        <p class="empty-description">{{ t('project.noProjectsDesc', '点击下方按钮创建您的第一个项目') }}</p>
        <el-button type="primary" :icon="Plus" @click="handleCreate">
          {{ t('project.create', '新建项目') }}
        </el-button>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p class="loading-text">{{ t('common.loading', '加载中...') }}</p>
      </div>

      <!-- Pagination -->
      <div v-if="projectList.length > 0" class="table-pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[12, 24, 48, 96]"
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="loadProjects"
          @size-change="loadProjects"
        />
      </div>
    </div>

    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'create' ? t('project.create', '新建项目') : t('project.edit', '编辑项目')"
      width="600px"
      destroy-on-close
      @close="handleDialogClose"
    >
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="100px">
        <el-form-item :label="t('project.name', '项目名称')" prop="name">
          <el-input v-model="formData.name" :placeholder="t('project.enterName', '请输入项目名称')" />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item :label="t('project.code', '项目编码')" prop="code">
              <el-input
                v-model="formData.code"
                :placeholder="t('project.enterCode', '请输入项目编码')"
                :disabled="dialogMode === 'edit'"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('project.key', '项目标识')" prop="key">
              <el-input
                v-model="formData.key"
                :placeholder="t('project.enterKey', '请输入项目标识')"
                maxlength="10"
                show-word-limit
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item :label="t('project.projectType', '项目类型')" prop="project_type">
              <el-select v-model="formData.project_type" :placeholder="t('project.selectType', '请选择项目类型')" style="width: 100%">
                <el-option :label="t('project.typeWeb', 'Web应用')" value="web" />
                <el-option :label="t('project.typeMobile', '移动应用')" value="mobile" />
                <el-option :label="t('project.typeApi', 'API服务')" value="api" />
                <el-option :label="t('project.typeDesktop', '桌面应用')" value="desktop" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('project.status', '项目状态')" prop="status">
              <el-select v-model="formData.status" :placeholder="t('project.selectStatus', '请选择状态')" style="width: 100%">
                <el-option :label="t('project.statusActive', '进行中')" value="active" />
                <el-option :label="t('project.statusArchived', '已归档')" value="archived" />
                <el-option :label="t('project.statusCompleted', '已完成')" value="completed" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item :label="t('common.description', '描述')">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            :placeholder="t('project.enterDescription', '请输入项目描述')"
          />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item :label="t('project.url', '项目地址')">
              <el-input v-model="formData.url" :placeholder="t('project.enterUrl', '请输入项目地址')" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('project.repository', '代码仓库')">
              <el-input v-model="formData.repository" :placeholder="t('project.enterRepository', '请输入代码仓库地址')" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item :label="t('project.owner', '项目经理')">
              <el-input v-model="formData.owner" :placeholder="t('project.enterOwner', '请输入项目经理')" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('project.lead', '技术负责人')">
              <el-input v-model="formData.lead" :placeholder="t('project.enterLead', '请输入技术负责人')" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item :label="t('project.color', '主题颜色')">
              <div class="color-input">
                <el-color-picker v-model="formData.color" show-alpha />
                <span class="color-value">{{ formData.color || '#228be6' }}</span>
              </div>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('project.icon', '图标')">
              <el-input v-model="formData.icon" :placeholder="t('project.enterIcon', '请输入图标')" maxlength="2" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">{{ t('common.cancel', '取消') }}</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          {{ dialogMode === 'create' ? t('common.create', '创建') : t('common.save', '保存') }}
        </el-button>
      </template>
    </el-dialog>

    <!-- Advanced Search Dialog -->
    <el-dialog v-model="showAdvancedSearch" :title="t('common.advanced', '高级搜索')" width="600px" destroy-on-close>
      <el-form :model="advancedSearchForm" label-width="100px">
        <el-form-item :label="t('project.code', '项目编码')">
          <el-input v-model="advancedSearchForm.code" :placeholder="t('project.searchCode', '搜索项目编码')" clearable />
        </el-form-item>
        <el-form-item :label="t('project.name', '项目名称')">
          <el-input v-model="advancedSearchForm.name" :placeholder="t('project.searchName', '搜索项目名称')" clearable />
        </el-form-item>
        <el-form-item :label="t('project.key', '项目标识')">
          <el-input v-model="advancedSearchForm.key" :placeholder="t('project.searchKey', '搜索项目标识')" clearable />
        </el-form-item>
        <el-form-item :label="t('project.projectType', '项目类型')">
          <el-select v-model="advancedSearchForm.project_type" :placeholder="t('project.selectType', '请选择项目类型')" clearable style="width: 100%">
            <el-option :label="t('project.typeWeb', 'Web应用')" value="web" />
            <el-option :label="t('project.typeMobile', '移动应用')" value="mobile" />
            <el-option :label="t('project.typeApi', 'API服务')" value="api" />
            <el-option :label="t('project.typeDesktop', '桌面应用')" value="desktop" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('project.status', '项目状态')">
          <el-select v-model="advancedSearchForm.status" :placeholder="t('project.selectStatus', '请选择状态')" clearable style="width: 100%">
            <el-option :label="t('project.statusActive', '进行中')" value="active" />
            <el-option :label="t('project.statusArchived', '已归档')" value="archived" />
            <el-option :label="t('project.statusCompleted', '已完成')" value="completed" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('common.keyword', '关键词')">
          <el-input v-model="advancedSearchForm.keyword" :placeholder="t('project.searchAll', '搜索所有字段')" clearable />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="handleResetAdvancedSearch">{{ t('common.reset', '重置') }}</el-button>
        <el-button @click="showAdvancedSearch = false">{{ t('common.cancel', '取消') }}</el-button>
        <el-button type="primary" @click="handleAdvancedSearch">{{ t('common.search', '搜索') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Search, MoreFilled, Document, Calendar, CircleClose, FolderOpened } from '@element-plus/icons-vue'
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
const showAdvancedSearch = ref(false)

const searchForm = reactive({
  keyword: '',
  status: ''
})

const advancedSearchForm = reactive({
  code: '',
  name: '',
  key: '',
  project_type: '',
  status: '',
  keyword: ''
})

const pagination = reactive({
  page: 1,
  per_page: 12,
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
  name: [{ required: true, message: t('project.nameRequired', '请输入项目名称'), trigger: 'blur' }],
  code: [{ required: true, message: t('project.codeRequired', '请输入项目编码'), trigger: 'blur' }],
  project_type: [{ required: true, message: t('project.typeRequired', '请选择项目类型'), trigger: 'change' }],
  status: [{ required: true, message: t('project.statusRequired', '请选择状态'), trigger: 'change' }]
}

function getProjectTypeText(type) {
  const map = {
    web: t('project.typeWeb', 'Web'),
    mobile: t('project.typeMobile', '移动'),
    api: t('project.typeApi', 'API'),
    desktop: t('project.typeDesktop', '桌面')
  }
  return map[type] || type
}

function getProjectStatusText(status) {
  const map = {
    active: t('project.statusActive', '进行中'),
    archived: t('project.statusArchived', '已归档'),
    completed: t('project.statusCompleted', '已完成')
  }
  return map[status] || status
}

async function loadProjects() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      per_page: pagination.per_page
    }

    // Basic search: only search name
    if (searchForm.keyword) {
      params.name = searchForm.keyword
    }
    if (searchForm.status) {
      params.status = searchForm.status
    }

    const res = await projectApi.getList(params)
    if (res.code === 200) {
      projectList.value = res.data.items || []
      pagination.total = res.data.total || 0
    }
  } catch (error) {
    ElMessage.error(t('common.error', '操作失败'))
  } finally {
    loading.value = false
  }
}

// Advanced search
function handleAdvancedSearch() {
  const params = {
    page: 1,
    per_page: pagination.per_page
  }

  // Add advanced search conditions
  if (advancedSearchForm.code) params.code = advancedSearchForm.code
  if (advancedSearchForm.name) params.name = advancedSearchForm.name
  if (advancedSearchForm.key) params.key = advancedSearchForm.key
  if (advancedSearchForm.project_type) params.project_type = advancedSearchForm.project_type
  if (advancedSearchForm.status) params.status = advancedSearchForm.status
  if (advancedSearchForm.keyword) params.keyword = advancedSearchForm.keyword

  // Sync to basic search display
  searchForm.keyword = advancedSearchForm.name || advancedSearchForm.keyword || ''
  searchForm.status = advancedSearchForm.status || ''

  projectApi.getList(params).then(res => {
    if (res.code === 200) {
      projectList.value = res.data.items || []
      pagination.total = res.data.total || 0
      showAdvancedSearch.value = false
    }
  })
}

// Reset advanced search
function handleResetAdvancedSearch() {
  Object.assign(advancedSearchForm, {
    code: '',
    name: '',
    key: '',
    project_type: '',
    status: '',
    keyword: ''
  })
  searchForm.keyword = ''
  searchForm.status = ''
  pagination.page = 1
  loadProjects()
}

function handleCreate() {
  dialogMode.value = 'create'
  resetForm()
  dialogVisible.value = true
}

function handleEdit(row) {
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

function handleDelete(row) {
  ElMessageBox.confirm(t('project.deleteConfirm', '确定要删除这个项目吗？'), t('common.confirm', '提示'), {
    confirmButtonText: t('common.confirm', '确定'),
    cancelButtonText: t('common.cancel', '取消'),
    type: 'warning'
  }).then(async () => {
    try {
      const res = await projectApi.delete(row.id)
      if (res.code === 200) {
        ElMessage.success(t('project.deleteSuccess', '删除成功'))
        loadProjects()
      }
    } catch (error) {
      ElMessage.error(t('common.error', '操作失败'))
    }
  })
}

async function handleSubmit() {
  await formRef.value.validate()
  submitting.value = true
  try {
    const data = { ...formData }
    if (dialogMode.value === 'create') {
      const res = await projectApi.create(data)
      if (res.code === 200) {
        ElMessage.success(t('project.createSuccess', '创建成功'))
        dialogVisible.value = false
        loadProjects()
      }
    } else {
      const res = await projectApi.update(currentProjectId.value, data)
      if (res.code === 200) {
        ElMessage.success(t('project.updateSuccess', '更新成功'))
        dialogVisible.value = false
        loadProjects()
      }
    }
  } catch (error) {
    ElMessage.error(t('common.error', '操作失败'))
  } finally {
    submitting.value = false
  }
}

function handleDialogClose() {
  resetForm()
  formRef.value?.clearValidate()
}

function resetForm() {
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
  loadProjects()
})
</script>

<style scoped>
/* ========================================
   MAIN CONTENT
   ======================================== */
.main-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  overflow: hidden;
  padding: var(--space-5);
}

/* Override toolbar padding for inside main-content */
.main-content .toolbar {
  padding: 0 0 var(--space-4) 0;
}

/* ========================================
   TOOLBAR
   ======================================== */
.toolbar {
  display: flex;
  gap: var(--space-3);
  justify-content: space-between;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

/* ========================================
   PROJECTS GRID
   ======================================== */
.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--space-5);
}

.project-card {
  background: var(--color-bg-alt);
  border: none;
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition: all var(--transition-fast);
  cursor: pointer;
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
  padding: var(--space-4) var(--space-4) var(--space-3) var(--space-4);
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
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-accent);
  border-radius: var(--radius-md);
  color: #ffffff;
  font-family: var(--font-display);
  font-size: var(--text-xl);
  font-weight: 600;
  flex-shrink: 0;
}

.card-title {
  font-family: var(--font-display);
  font-size: var(--text-md);
  font-weight: 600;
  color: var(--color-text);
  margin: 0 0 var(--space-1) 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-code {
  font-family: var(--font-display);
  font-size: var(--text-xs);
  font-weight: 500;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0 0 var(--space-2) 0;
}

.header-meta {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
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
  flex-shrink: 0;
}

.card-more:hover {
  background: var(--color-bg-alt);
  color: var(--color-text);
}

/* Card Body */
.card-body {
  padding: var(--space-4) var(--space-4) var(--space-4) var(--space-4);
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

/* Card Stats */
.card-stats {
  display: flex;
  gap: var(--space-4);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-1);
  flex: 1;
}

.stat-icon {
  font-size: 20px;
}

.stat-primary {
  color: var(--color-accent);
}

.stat-success {
  color: var(--color-success);
}

.stat-error {
  color: var(--color-error);
}

.stat-number {
  font-family: var(--font-display);
  font-size: var(--text-lg);
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

/* Override pagination padding for inside main-content */
.main-content .table-pagination {
  padding: var(--space-4) 0 0 0;
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

.empty-icon {
  font-size: 64px;
  color: var(--color-text-muted);
  opacity: 0.3;
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
  .main-content {
    padding: var(--space-3);
  }

  .toolbar {
    flex-wrap: wrap;
  }

  .projects-grid {
    grid-template-columns: 1fr;
  }

  .card-stats {
    flex-wrap: wrap;
  }
}
/* ========================================
   RESPONSIVE
   ======================================== */
@media (max-width: 768px) {
  .main-content {
    padding: var(--space-3);
  }

  .toolbar {
    flex-wrap: wrap;
  }

  .projects-grid {
    grid-template-columns: 1fr;
  }

  .card-stats {
    flex-wrap: wrap;
  }
}
</style>

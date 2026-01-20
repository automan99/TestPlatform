<template>
  <div class="page-container">
    <div class="page-layout animate-fade-in-up" ref="layoutRef">
      <!-- Sidebar with Module Tree -->
      <div class="page-sidebar module-sidebar" :style="{ width: sidebarWidth + 'px' }">
        <div class="sidebar-header">
          <span class="sidebar-title">{{ t('defect.modules') }}</span>
          <el-dropdown trigger="click" @command="handleModuleCommand">
            <el-button type="primary" link size="small">
              <el-icon><Plus /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="add">{{ t('defect.newModule') }}</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
        <el-tree
          ref="treeRef"
          :data="moduleTree"
          :props="treeProps"
          :highlight-current="true"
          node-key="id"
          default-expand-all
          @node-click="handleNodeClick"
          class="module-tree"
        >
          <template #default="{ node, data }">
            <div class="tree-node">
              <div class="node-content">
                <el-icon class="folder-icon"><Folder /></el-icon>
                <span class="node-label">{{ node.label }}</span>
                <span class="node-count">({{ data.defect_count || 0 }})</span>
              </div>
              <el-dropdown trigger="click" @command="(cmd) => handleModuleAction(cmd, data)">
                <el-icon class="node-more" @click.stop><MoreFilled /></el-icon>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="addSub">{{ t('defect.addSubModule') }}</el-dropdown-item>
                    <el-dropdown-item command="edit">{{ t('common.edit') }}</el-dropdown-item>
                    <el-dropdown-item command="delete" v-if="!data.children || data.children.length === 0">{{ t('common.delete') }}</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </template>
        </el-tree>
      </div>

      <!-- Resize Handle -->
      <div
        class="resize-handle"
        @mousedown="handleMouseDown"
      ></div>

      <!-- Content Area -->
      <div class="content-area">
        <div class="content-body">
          <!-- Toolbar -->
          <div class="toolbar">
            <div class="toolbar-left">
              <el-input
                v-model="searchForm.keyword"
                :placeholder="t('defect.searchDefects')"
                clearable
                class="search-input"
                @change="loadDefects"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
              <el-button :icon="Search" @click="showAdvancedSearch = true">{{ t('defect.advancedSearch') }}</el-button>
            </div>
            <div class="toolbar-right">
              <el-button type="primary" :icon="Plus" @click="handleCreate">{{ t('defect.newDefect') }}</el-button>
            </div>
          </div>

          <!-- Table -->
          <div class="page-table">
            <el-table :data="defectList" class="page-table">
              <el-table-column prop="defect_no" :label="t('defect.defectNo')" width="120" show-overflow-tooltip />
              <el-table-column prop="title" :label="t('defect.title')" min-width="150" show-overflow-tooltip />
              <el-table-column prop="severity" :label="t('defect.severity')" width="100">
                <template #default="{ row }">
                  <el-tag :type="getSeverityType(row.severity)">{{ getSeverityText(row.severity) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="priority" :label="t('defect.priority')" width="100">
                <template #default="{ row }">
                  <el-tag :type="getPriorityType(row.priority)">{{ getPriorityText(row.priority) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="status" :label="t('defect.status')" width="100">
                <template #default="{ row }">
                  <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="assigned_to" :label="t('defect.assignedTo')" width="120" show-overflow-tooltip />
              <el-table-column prop="reported_date" :label="t('defect.reportedDate')" width="160" show-overflow-tooltip />
              <el-table-column :label="t('defect.actions')" width="140" fixed="right">
                <template #default="{ row }">
                  <el-button type="info" link size="small" @click="handleView(row)">
                    <el-icon><View /></el-icon>
                  </el-button>
                  <el-button type="primary" link size="small" @click="handleEdit(row)">
                    <el-icon><Edit /></el-icon>
                  </el-button>
                  <el-button type="danger" link size="small" @click="handleDelete(row)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <!-- Pagination -->
          <div class="table-pagination">
            <el-pagination
              v-model:current-page="pagination.page"
              v-model:page-size="pagination.pageSize"
              :total="pagination.total"
              :page-sizes="[10, 20, 50, 100]"
              layout="total, sizes, prev, pager, next, jumper"
              @current-change="loadDefects"
              @size-change="loadDefects"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Module Form Dialog -->
    <el-dialog v-model="moduleDialogVisible" :title="moduleDialogTitle" width="500px" destroy-on-close>
      <el-form :model="moduleForm" :rules="moduleRules" ref="moduleFormRef" label-width="100px">
        <el-form-item :label="t('defect.moduleName')" prop="name">
          <el-input v-model="moduleForm.name" :placeholder="t('defect.enterModuleName')" />
        </el-form-item>
        <el-form-item :label="t('defect.parentModule')" prop="parent_id">
          <el-tree-select
            v-model="moduleForm.parent_id"
            :data="moduleOptions"
            :props="{ value: 'id', label: 'name', children: 'children' }"
            :placeholder="t('defect.selectParentModule')"
            clearable
            check-strictly
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="moduleDialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" @click="handleModuleSubmit">{{ t('common.submit') }}</el-button>
      </template>
    </el-dialog>

    <!-- Defect Form Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="800px" destroy-on-close>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item :label="t('defect.title')" prop="title">
          <el-input v-model="form.title" :placeholder="t('defect.titlePlaceholder')" />
        </el-form-item>
        <el-form-item :label="t('defect.module')" prop="module_id">
          <el-tree-select
            v-model="form.module_id"
            :data="moduleOptions"
            :props="{ value: 'id', label: 'name', children: 'children' }"
            :placeholder="t('defect.selectModule', '选择模块')"
            clearable
            check-strictly
            style="width: 100%"
          />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item :label="t('defect.severity')" prop="severity">
              <el-select v-model="form.severity" style="width: 100%">
                <el-option :label="t('defect.critical')" value="critical" />
                <el-option :label="t('defect.high')" value="high" />
                <el-option :label="t('defect.medium')" value="medium" />
                <el-option :label="t('defect.low')" value="low" />
                <el-option :label="t('defect.trivial')" value="trivial" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item :label="t('defect.priority')" prop="priority">
              <el-select v-model="form.priority" style="width: 100%">
                <el-option :label="t('defect.urgent')" value="urgent" />
                <el-option :label="t('defect.high')" value="high" />
                <el-option :label="t('defect.medium')" value="medium" />
                <el-option :label="t('defect.low')" value="low" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item :label="t('defect.status')" prop="status">
              <el-select v-model="form.status" style="width: 100%">
                <el-option :label="t('defect.new')" value="new" />
                <el-option :label="t('defect.assigned')" value="assigned" />
                <el-option :label="t('defect.inProgress')" value="in_progress" />
                <el-option :label="t('defect.resolved')" value="resolved" />
                <el-option :label="t('defect.closed')" value="closed" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item :label="t('defect.type')" prop="defect_type">
              <el-select v-model="form.defect_type" style="width: 100%">
                <el-option :label="t('defect.bug')" value="bug" />
                <el-option :label="t('defect.feature')" value="feature" />
                <el-option :label="t('defect.improvement')" value="improvement" />
                <el-option :label="t('defect.task')" value="task" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('defect.assignedTo')" prop="assigned_to">
              <el-select v-model="form.assigned_to" :placeholder="t('defect.selectMember')" clearable filterable style="width: 100%">
                <el-option
                  v-for="member in memberList"
                  :key="member.id"
                  :label="member.name"
                  :value="member.name"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item :label="t('defect.description')" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" :placeholder="t('defect.descriptionPlaceholder')" />
        </el-form-item>
        <el-form-item :label="t('defect.stepsToReproduce')" prop="reproduction_steps">
          <el-input v-model="form.reproduction_steps" type="textarea" :rows="4" :placeholder="t('defect.stepsPlaceholder')" />
        </el-form-item>
        <el-form-item :label="t('defect.expectedBehavior')" prop="expected_behavior">
          <el-input v-model="form.expected_behavior" type="textarea" :rows="2" :placeholder="t('defect.expectedPlaceholder')" />
        </el-form-item>
        <el-form-item :label="t('defect.actualBehavior')" prop="actual_behavior">
          <el-input v-model="form.actual_behavior" type="textarea" :rows="2" :placeholder="t('defect.actualPlaceholder')" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item :label="t('defect.environment')" prop="environment">
              <el-input v-model="form.environment" :placeholder="t('defect.environmentPlaceholder')" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item :label="t('defect.browser')" prop="browser">
              <el-input v-model="form.browser" :placeholder="t('defect.browserPlaceholder')" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item :label="t('defect.os')" prop="os">
              <el-input v-model="form.os" :placeholder="t('defect.osPlaceholder')" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" @click="handleSubmit">{{ t('common.submit') }}</el-button>
      </template>
    </el-dialog>

    <!-- Advanced Search Dialog -->
    <el-dialog v-model="showAdvancedSearch" :title="t('defect.advancedSearch')" width="600px" destroy-on-close>
      <el-form :model="advancedSearchForm" label-width="100px">
        <el-form-item :label="t('defect.defectNo')">
          <el-input v-model="advancedSearchForm.defect_no" :placeholder="t('defect.defectNoPlaceholder')" clearable />
        </el-form-item>
        <el-form-item :label="t('defect.title')">
          <el-input v-model="advancedSearchForm.title" :placeholder="t('defect.searchTitle')" clearable />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item :label="t('defect.severity')">
              <el-select v-model="advancedSearchForm.severity" :placeholder="t('defect.selectSeverity')" clearable style="width: 100%">
                <el-option :label="t('defect.critical')" value="critical" />
                <el-option :label="t('defect.high')" value="high" />
                <el-option :label="t('defect.medium')" value="medium" />
                <el-option :label="t('defect.low')" value="low" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('defect.priority')">
              <el-select v-model="advancedSearchForm.priority" :placeholder="t('defect.selectPriority')" clearable style="width: 100%">
                <el-option :label="t('defect.urgent')" value="urgent" />
                <el-option :label="t('defect.high')" value="high" />
                <el-option :label="t('defect.medium')" value="medium" />
                <el-option :label="t('defect.low')" value="low" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item :label="t('defect.status')">
              <el-select v-model="advancedSearchForm.status" :placeholder="t('defect.selectStatus')" clearable style="width: 100%">
                <el-option :label="t('defect.new')" value="new" />
                <el-option :label="t('defect.assigned')" value="assigned" />
                <el-option :label="t('defect.inProgress')" value="in_progress" />
                <el-option :label="t('defect.resolved')" value="resolved" />
                <el-option :label="t('defect.closed')" value="closed" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('defect.type')">
              <el-select v-model="advancedSearchForm.defect_type" :placeholder="t('defect.selectType')" clearable style="width: 100%">
                <el-option :label="t('defect.bug')" value="bug" />
                <el-option :label="t('defect.feature')" value="feature" />
                <el-option :label="t('defect.improvement')" value="improvement" />
                <el-option :label="t('defect.task')" value="task" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item :label="t('defect.assignedTo')">
          <el-input v-model="advancedSearchForm.assigned_to" :placeholder="t('defect.enterAssigneeName')" clearable />
        </el-form-item>
        <el-form-item :label="t('defect.keyword')">
          <el-input v-model="advancedSearchForm.keyword" :placeholder="t('defect.keywordPlaceholder')" clearable />
        </el-form-item>
        <el-form-item :label="t('defect.created')">
          <el-date-picker
            v-model="advancedSearchForm.created_at"
            type="daterange"
            range-separator="to"
            :start-placeholder="t('defect.startPlaceholder')"
            :end-placeholder="t('defect.endPlaceholder')"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item :label="t('defect.updated')">
          <el-date-picker
            v-model="advancedSearchForm.updated_at"
            type="daterange"
            range-separator="to"
            :start-placeholder="t('defect.startPlaceholder')"
            :end-placeholder="t('defect.endPlaceholder')"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="handleResetAdvancedSearch">{{ t('common.reset') }}</el-button>
        <el-button @click="showAdvancedSearch = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" @click="handleAdvancedSearch">{{ t('common.search') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { View, Edit, Delete, Plus, Folder, MoreFilled, Search } from '@element-plus/icons-vue'
import { defectApi } from '@/api/defect'
import { projectApi } from '@/api/project'
import { useProjectStore } from '@/store/project'
import { useI18n } from '@/i18n'

const { t } = useI18n()

const router = useRouter()
const projectStore = useProjectStore()
const formRef = ref()
const treeRef = ref()
const moduleFormRef = ref()
const layoutRef = ref()

// Sidebar width related
const sidebarWidth = ref(250)
const minWidth = 180
const maxWidth = 500
const isResizing = ref(false)

// Restore width from localStorage
const savedWidth = localStorage.getItem('defect-sidebar-width')
if (savedWidth) {
  sidebarWidth.value = parseInt(savedWidth)
}

// Watch width changes and save
watch(sidebarWidth, (newWidth) => {
  localStorage.setItem('defect-sidebar-width', newWidth.toString())
})

// Mouse down start dragging
function handleMouseDown(e) {
  isResizing.value = true
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
  document.body.style.cursor = 'col-resize'
  document.body.style.userSelect = 'none'
}

// Mouse move
function handleMouseMove(e) {
  if (!isResizing.value || !layoutRef.value) return

  const rect = layoutRef.value.getBoundingClientRect()
  const newWidth = e.clientX - rect.left

  // Limit width range
  if (newWidth >= minWidth && newWidth <= maxWidth) {
    sidebarWidth.value = newWidth
  }
}

// Mouse up
function handleMouseUp() {
  isResizing.value = false
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
  document.body.style.cursor = ''
  document.body.style.userSelect = ''
}

// Module tree related
const moduleTree = ref([])
const moduleOptions = ref([])
const moduleDialogVisible = ref(false)
const moduleDialogTitle = ref('')
const isModuleEdit = ref(false)
const selectedModuleId = ref(null)
const currentModuleIds = ref([])

const treeProps = {
  children: 'children',
  label: 'name',
  value: 'id'
}

const moduleForm = reactive({
  id: null,
  name: '',
  parent_id: null
})

const moduleRules = {
  name: [{ required: true, message: t('defect.enterModuleName'), trigger: 'blur' }]
}

// Current module name
const currentModuleName = computed(() => {
  if (selectedModuleId.value === null) return t('defect.allDefects')
  const findName = (tree, id) => {
    for (const item of tree) {
      if (item.id === id) return item.name
      if (item.children) {
        const found = findName(item.children, id)
        if (found) return found
      }
    }
    return ''
  }
  return findName(moduleTree.value, selectedModuleId.value) || t('defect.currentModule')
})

// Current project ID
const currentProjectId = computed(() => projectStore.currentProject?.id)

const dialogVisible = ref(false)
const dialogTitle = ref('')
const isEdit = ref(false)

// Project member list
const memberList = ref([])

const defectList = ref([])

const searchForm = reactive({
  keyword: '',
  severity: '',
  priority: '',
  status: '',
  module_id: null
})

const showAdvancedSearch = ref(false)
const advancedSearchForm = reactive({
  defect_no: '',
  title: '',
  severity: '',
  priority: '',
  status: '',
  defect_type: '',
  assigned_to: '',
  keyword: '',
  created_at: null,
  updated_at: null
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const form = reactive({
  id: null,
  title: '',
  description: '',
  severity: 'medium',
  priority: 'medium',
  status: 'new',
  defect_type: 'bug',
  assigned_to: '',
  environment: '',
  browser: '',
  os: '',
  reproduction_steps: '',
  expected_behavior: '',
  actual_behavior: '',
  module_id: null
})

const rules = {
  title: [{ required: true, message: t('defect.titlePlaceholder'), trigger: 'blur' }]
}

function getSeverityType(severity) {
  const map = { critical: 'danger', high: 'warning', medium: 'primary', low: 'info', trivial: 'info' }
  return map[severity] || 'info'
}

function getSeverityText(severity) {
  return t(`defect.${severity}`)
}

function getPriorityType(priority) {
  const map = { urgent: 'danger', high: 'warning', medium: 'primary', low: 'info' }
  return map[priority] || 'info'
}

function getPriorityText(priority) {
  return t(`defect.${priority}`)
}

function getStatusType(status) {
  const map = { new: 'info', assigned: 'warning', in_progress: 'primary', resolved: 'success', closed: 'info' }
  return map[status] || 'info'
}

function getStatusText(status) {
  const map = { new: 'new', assigned: 'assigned', in_progress: 'inProgress', resolved: 'resolved', closed: 'closed' }
  return t(`defect.${map[status] || status}`)
}

function buildOptions(tree) {
  const options = []
  for (const node of tree) {
    options.push({
      id: node.id,
      name: node.name,
      children: node.children?.length ? buildOptions(node.children) : undefined
    })
  }
  return options
}

// Module operation commands
function handleModuleCommand(command) {
  if (command === 'add') {
    handleAddModule()
  }
}

function handleModuleAction(command, data) {
  if (command === 'addSub') {
    handleAddModule(data.id)
  } else if (command === 'edit') {
    handleEditModule(data)
  } else if (command === 'delete') {
    handleDeleteModule(data)
  }
}

// Add module
function handleAddModule(parentId = null) {
  isModuleEdit.value = false
  moduleDialogTitle.value = parentId ? t('defect.newSubModule') : t('defect.newModule')
  Object.assign(moduleForm, {
    id: null,
    name: '',
    parent_id: parentId
  })
  moduleDialogVisible.value = true
}

// Module related methods
async function loadModules() {
  if (!currentProjectId.value) return
  const res = await defectApi.getModules(currentProjectId.value)
  moduleTree.value = res.data || []
  // Calculate cumulative counts for parent nodes
  calculateCumulativeCounts(moduleTree.value)
  moduleOptions.value = buildOptions(moduleTree.value)
}

// Calculate cumulative counts for parent nodes (including all children)
function calculateCumulativeCounts(tree) {
  for (const node of tree) {
    if (node.children && node.children.length > 0) {
      // First recursively calculate children counts
      calculateCumulativeCounts(node.children)
      // Sum up all children counts
      node.defect_count = node.children.reduce((sum, child) => sum + (child.defect_count || 0), 0)
    }
  }
}

// Get all module IDs including children
function getAllModuleIds(tree, targetId) {
  const ids = []
  const findAndCollect = (nodes, id) => {
    for (const node of nodes) {
      if (node.id === id) {
        // Found target, collect this node and all children
        collectAllIds(node, ids)
        return true
      }
      if (node.children && node.children.length > 0) {
        if (findAndCollect(node.children, id)) {
          return true
        }
      }
    }
    return false
  }

  const collectAllIds = (node, collection) => {
    collection.push(node.id)
    if (node.children && node.children.length > 0) {
      for (const child of node.children) {
        collectAllIds(child, collection)
      }
    }
  }

  findAndCollect(tree, targetId)
  return ids
}

function handleNodeClick(data) {
  selectedModuleId.value = data.id
  // Store all module IDs including children for loading defects
  const allIds = getAllModuleIds(moduleTree.value, data.id)
  // Only use multiple IDs if this node has children (more than 1 ID collected)
  currentModuleIds.value = allIds.length > 1 ? allIds : []
  // Also update searchForm.module_id for single selection
  searchForm.module_id = data.id
  console.log('Clicked module ID:', data.id, 'All module IDs:', allIds, 'Will use:', currentModuleIds.value.length > 0 ? currentModuleIds.value : [data.id])
  pagination.page = 1
  loadDefects()
}

function handleEditModule(data) {
  isModuleEdit.value = true
  moduleDialogTitle.value = t('defect.editModule')
  Object.assign(moduleForm, {
    id: data.id,
    name: data.name,
    parent_id: data.parent_id
  })
  moduleDialogVisible.value = true
}

function handleDeleteModule(data) {
  ElMessageBox.confirm(t('defect.deleteModuleConfirm'), t('common.confirm'), { type: 'warning' })
    .then(() => defectApi.deleteModule(data.id))
    .then(() => {
      ElMessage.success(t('defect.deleteSuccess'))
      loadModules()
      if (selectedModuleId.value === data.id) {
        selectedModuleId.value = null
      }
    })
}

function handleModuleSubmit() {
  moduleFormRef.value.validate((valid) => {
    if (valid) {
      const data = {
        ...moduleForm,
        project_id: currentProjectId.value
      }
      const api = isModuleEdit.value ? defectApi.updateModule : defectApi.createModule
      const params = isModuleEdit.value ? moduleForm.id : data
      api(params, isModuleEdit.value ? data : null).then(() => {
        ElMessage.success(isModuleEdit.value ? t('defect.updatedSuccess') : t('defect.createdSuccess'))
        moduleDialogVisible.value = false
        loadModules()
      })
    }
  })
}

async function loadDefects() {
  const params = {
    page: pagination.page,
    per_page: pagination.pageSize,
    project_id: currentProjectId.value
  }

  // Use all module IDs if a parent is selected (includes children)
  if (currentModuleIds.value.length > 0) {
    // Try passing as array - axios will serialize it
    params.module_ids = currentModuleIds.value
    console.log('Loading defects with module_ids:', currentModuleIds.value)
  } else if (searchForm.module_id !== null) {
    // Single module selected
    params.module_id = searchForm.module_id
    console.log('Loading defects with module_id:', searchForm.module_id)
  } else {
    console.log('Loading all defects (no module filter)')
  }

  // Basic search: only search title
  if (searchForm.keyword) {
    params.title = searchForm.keyword
  }
  // Severity, priority and status filter
  if (searchForm.severity) {
    params.severity = searchForm.severity
  }
  if (searchForm.priority) {
    params.priority = searchForm.priority
  }
  if (searchForm.status) {
    params.status = searchForm.status
  }

  const res = await defectApi.getList(params)
  defectList.value = res.data?.items || []
  pagination.total = res.data?.total || 0
}

// Advanced search
function handleAdvancedSearch() {
  const params = {
    page: 1,
    per_page: pagination.pageSize,
    project_id: currentProjectId.value
  }

  // Use all module IDs if a parent is selected (includes children)
  if (currentModuleIds.value.length > 0) {
    params.module_ids = currentModuleIds.value
  } else if (searchForm.module_id !== null) {
    params.module_id = searchForm.module_id
  }

  // Add advanced search conditions
  if (advancedSearchForm.defect_no) params.defect_no = advancedSearchForm.defect_no
  if (advancedSearchForm.title) params.title = advancedSearchForm.title
  if (advancedSearchForm.severity) params.severity = advancedSearchForm.severity
  if (advancedSearchForm.priority) params.priority = advancedSearchForm.priority
  if (advancedSearchForm.status) params.status = advancedSearchForm.status
  if (advancedSearchForm.defect_type) params.defect_type = advancedSearchForm.defect_type
  if (advancedSearchForm.assigned_to) params.assigned_to = advancedSearchForm.assigned_to
  if (advancedSearchForm.keyword) params.keyword = advancedSearchForm.keyword
  if (advancedSearchForm.created_at && advancedSearchForm.created_at.length === 2) {
    params.created_after = advancedSearchForm.created_at[0]
    params.created_before = advancedSearchForm.created_at[1]
  }
  if (advancedSearchForm.updated_at && advancedSearchForm.updated_at.length === 2) {
    params.updated_after = advancedSearchForm.updated_at[0]
    params.updated_before = advancedSearchForm.updated_at[1]
  }

  // Sync to basic search display
  searchForm.keyword = advancedSearchForm.title || advancedSearchForm.keyword || ''
  searchForm.severity = advancedSearchForm.severity || ''
  searchForm.priority = advancedSearchForm.priority || ''
  searchForm.status = advancedSearchForm.status || ''

  pagination.page = 1
  defectApi.getList(params).then(res => {
    defectList.value = res.data?.items || []
    pagination.total = res.data?.total || 0
    showAdvancedSearch.value = false
  })
}

// Reset advanced search
function handleResetAdvancedSearch() {
  Object.assign(advancedSearchForm, {
    defect_no: '',
    title: '',
    severity: '',
    priority: '',
    status: '',
    defect_type: '',
    assigned_to: '',
    keyword: '',
    created_at: null,
    updated_at: null
  })
}

async function loadMembers() {
  if (!currentProjectId.value) return
  const res = await projectApi.getMembers(currentProjectId.value)
  memberList.value = res.data?.items || []
}

function handleCreate() {
  isEdit.value = false
  dialogTitle.value = t('defect.newDefect')
  Object.assign(form, {
    id: null,
    title: '',
    description: '',
    severity: 'medium',
    priority: 'medium',
    status: 'new',
    defect_type: 'bug',
    assigned_to: '',
    environment: '',
    browser: '',
    os: '',
    reproduction_steps: '',
    expected_behavior: '',
    actual_behavior: '',
    module_id: selectedModuleId.value,
    project_id: currentProjectId.value
  })
  loadMembers()
  dialogVisible.value = true
}

function handleEdit(row) {
  isEdit.value = true
  dialogTitle.value = t('defect.editDefect')
  Object.assign(form, row)
  loadMembers()
  dialogVisible.value = true
}

function handleView(row) {
  router.push(`/defects/${row.id}`)
}

function handleDelete(row) {
  ElMessageBox.confirm(t('defect.deleteConfirm'), t('common.confirm'), { type: 'warning' })
    .then(() => defectApi.delete(row.id))
    .then(() => {
      ElMessage.success(t('defect.deletedSuccess'))
      loadDefects()
    })
}

function handleSubmit() {
  formRef.value.validate((valid) => {
    if (valid) {
      const api = isEdit.value ? defectApi.update : defectApi.create
      const params = isEdit.value ? form.id : form
      api(params, isEdit.value ? form : null).then(() => {
        ElMessage.success(isEdit.value ? t('defect.updatedSuccess') : t('defect.createdSuccess'))
        dialogVisible.value = false
        loadDefects()
      })
    }
  })
}

onMounted(() => {
  if (currentProjectId.value) {
    loadDefects()
    loadMembers()
    loadModules()
  }
})

// Watch project changes, reload data
watch(currentProjectId, (newVal, oldVal) => {
  if (newVal && newVal !== oldVal) {
    selectedModuleId.value = null
    loadDefects()
    loadMembers()
    loadModules()
  }
})
</script>

<style scoped>
/* Page-specific styles only - general layout styles are in page-layout.css */
</style>

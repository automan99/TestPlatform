<template>
  <div class="defect-page">
    <div class="page-layout" ref="layoutRef">
      <!-- 左侧模块树 -->
      <div class="module-sidebar" :style="{ width: sidebarWidth + 'px' }">
        <div class="module-header">
          <span>模块分类</span>
          <el-dropdown trigger="click" @command="handleModuleCommand">
            <el-button type="primary" link size="small">
              <el-icon><Plus /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="add">新建模块</el-dropdown-item>
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
        >
          <template #default="{ node, data }">
            <div class="tree-node">
              <div class="node-content">
                <el-icon class="folder-icon"><Folder /></el-icon>
                <span class="node-label">{{ node.label }}</span>
              </div>
              <el-dropdown trigger="click" @command="(cmd) => handleModuleAction(cmd, data)">
                <el-icon class="node-more" @click.stop><MoreFilled /></el-icon>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="addSub">添加子模块</el-dropdown-item>
                    <el-dropdown-item command="edit">编辑</el-dropdown-item>
                    <el-dropdown-item command="delete" v-if="!data.children || data.children.length === 0">删除</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </template>
        </el-tree>
      </div>

      <!-- 拖拽分隔条 -->
      <div
        class="resize-handle"
        @mousedown="handleMouseDown"
      ></div>

      <!-- 右侧内容区 -->
      <div class="content-area">
        <el-card>
          <template #header>
            <div class="page-header">
              <span>{{ currentModuleName }}</span>
              <div class="header-actions">
                <el-button type="primary" :icon="Plus" @click="handleCreate">新建缺陷</el-button>
              </div>
            </div>
          </template>

          <div class="toolbar">
            <el-input v-model="searchForm.keyword" placeholder="搜索缺陷" clearable style="width: 200px" @change="loadDefects" />
            <el-select v-model="searchForm.severity" placeholder="严重程度" clearable @change="loadDefects">
              <el-option label="紧急" value="critical" />
              <el-option label="高" value="high" />
              <el-option label="中" value="medium" />
              <el-option label="低" value="low" />
            </el-select>
            <el-select v-model="searchForm.priority" placeholder="优先级" clearable @change="loadDefects">
              <el-option label="紧急" value="urgent" />
              <el-option label="高" value="high" />
              <el-option label="中" value="medium" />
              <el-option label="低" value="low" />
            </el-select>
            <el-select v-model="searchForm.status" placeholder="状态" clearable @change="loadDefects">
              <el-option label="新建" value="new" />
              <el-option label="已分配" value="assigned" />
              <el-option label="进行中" value="in_progress" />
              <el-option label="已解决" value="resolved" />
              <el-option label="已关闭" value="closed" />
            </el-select>
            <div style="flex: 1"></div>
          </div>

          <el-table :data="defectList" style="width: 100%">
            <el-table-column prop="defect_no" label="编号" width="120" />
            <el-table-column prop="title" label="标题" show-overflow-tooltip />
            <el-table-column prop="severity" label="严重程度" width="100">
              <template #default="{ row }">
                <el-tag :type="getSeverityType(row.severity)">{{ getSeverityText(row.severity) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="priority" label="优先级" width="100">
              <template #default="{ row }">
                <el-tag :type="getPriorityType(row.priority)">{{ getPriorityText(row.priority) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="assigned_to" label="分配给" width="120" />
            <el-table-column prop="reported_date" label="报告日期" width="120" />
            <el-table-column label="操作" width="140" fixed="right">
              <template #default="{ row }">
                <el-tooltip content="查看" placement="top">
                  <el-button type="info" link size="small" @click="handleView(row)">
                    <el-icon><View /></el-icon>
                  </el-button>
                </el-tooltip>
                <el-tooltip content="编辑" placement="top">
                  <el-button type="primary" link size="small" @click="handleEdit(row)">
                    <el-icon><Edit /></el-icon>
                  </el-button>
                </el-tooltip>
                <el-tooltip content="删除" placement="top">
                  <el-button type="danger" link size="small" @click="handleDelete(row)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </el-tooltip>
              </template>
            </el-table-column>
          </el-table>

          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.pageSize"
            :total="pagination.total"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @current-change="loadDefects"
            @size-change="loadDefects"
            style="margin-top: 20px; justify-content: flex-end"
          />
        </el-card>
      </div>
    </div>

    <!-- 模块表单对话框 -->
    <el-dialog v-model="moduleDialogVisible" :title="moduleDialogTitle" width="500px" destroy-on-close>
      <el-form :model="moduleForm" :rules="moduleRules" ref="moduleFormRef" label-width="100px">
        <el-form-item label="模块名称" prop="name">
          <el-input v-model="moduleForm.name" />
        </el-form-item>
        <el-form-item label="父模块" prop="parent_id">
          <el-tree-select
            v-model="moduleForm.parent_id"
            :data="moduleOptions"
            :props="{ value: 'id', label: 'name', children: 'children' }"
            placeholder="选择父模块"
            clearable
            check-strictly
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="moduleDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleModuleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 缺陷表单对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="800px" destroy-on-close>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="缺陷标题" prop="title">
          <el-input v-model="form.title" />
        </el-form-item>
        <el-form-item label="所属模块" prop="module_id">
          <el-tree-select
            v-model="form.module_id"
            :data="moduleOptions"
            :props="{ value: 'id', label: 'name', children: 'children' }"
            placeholder="选择模块"
            clearable
            check-strictly
            style="width: 100%"
          />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="严重程度" prop="severity">
              <el-select v-model="form.severity" style="width: 100%">
                <el-option label="紧急" value="critical" />
                <el-option label="高" value="high" />
                <el-option label="中" value="medium" />
                <el-option label="低" value="low" />
                <el-option label="轻微" value="trivial" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="优先级" prop="priority">
              <el-select v-model="form.priority" style="width: 100%">
                <el-option label="紧急" value="urgent" />
                <el-option label="高" value="high" />
                <el-option label="中" value="medium" />
                <el-option label="低" value="low" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="状态" prop="status">
              <el-select v-model="form.status" style="width: 100%">
                <el-option label="新建" value="new" />
                <el-option label="已分配" value="assigned" />
                <el-option label="进行中" value="in_progress" />
                <el-option label="已解决" value="resolved" />
                <el-option label="已关闭" value="closed" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="缺陷类型" prop="defect_type">
              <el-select v-model="form.defect_type" style="width: 100%">
                <el-option label="缺陷" value="bug" />
                <el-option label="功能" value="feature" />
                <el-option label="改进" value="improvement" />
                <el-option label="任务" value="task" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="分配给" prop="assigned_to">
              <el-select v-model="form.assigned_to" placeholder="选择成员" clearable filterable style="width: 100%">
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
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="复现步骤" prop="reproduction_steps">
          <el-input v-model="form.reproduction_steps" type="textarea" :rows="4" />
        </el-form-item>
        <el-form-item label="期望行为" prop="expected_behavior">
          <el-input v-model="form.expected_behavior" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="实际行为" prop="actual_behavior">
          <el-input v-model="form.actual_behavior" type="textarea" :rows="2" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="环境" prop="environment">
              <el-input v-model="form.environment" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="浏览器" prop="browser">
              <el-input v-model="form.browser" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="操作系统" prop="os">
              <el-input v-model="form.os" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { View, Edit, Delete, Plus, Folder, MoreFilled } from '@element-plus/icons-vue'
import { defectApi } from '@/api/defect'
import { projectApi } from '@/api/project'
import { useProjectStore } from '@/store/project'

const router = useRouter()
const projectStore = useProjectStore()
const formRef = ref()
const treeRef = ref()
const moduleFormRef = ref()
const layoutRef = ref()

// 侧边栏宽度相关
const sidebarWidth = ref(250)
const minWidth = 180
const maxWidth = 500
const isResizing = ref(false)

// 从 localStorage 恢复宽度
const savedWidth = localStorage.getItem('defect-sidebar-width')
if (savedWidth) {
  sidebarWidth.value = parseInt(savedWidth)
}

// 监听宽度变化并保存
watch(sidebarWidth, (newWidth) => {
  localStorage.setItem('defect-sidebar-width', newWidth.toString())
})

// 鼠标按下开始拖拽
function handleMouseDown(e) {
  isResizing.value = true
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
  document.body.style.cursor = 'col-resize'
  document.body.style.userSelect = 'none'
}

// 鼠标移动
function handleMouseMove(e) {
  if (!isResizing.value || !layoutRef.value) return

  const rect = layoutRef.value.getBoundingClientRect()
  const newWidth = e.clientX - rect.left

  // 限制宽度范围
  if (newWidth >= minWidth && newWidth <= maxWidth) {
    sidebarWidth.value = newWidth
  }
}

// 鼠标释放
function handleMouseUp() {
  isResizing.value = false
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
  document.body.style.cursor = ''
  document.body.style.userSelect = ''
}

// 模块树相关
const moduleTree = ref([])
const moduleOptions = ref([])
const moduleDialogVisible = ref(false)
const moduleDialogTitle = ref('')
const isModuleEdit = ref(false)
const selectedModuleId = ref(null)

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
  name: [{ required: true, message: '请输入模块名称', trigger: 'blur' }]
}

// 当前模块名称
const currentModuleName = computed(() => {
  if (selectedModuleId.value === null) return '全部缺陷'
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
  return findName(moduleTree.value, selectedModuleId.value) || '当前模块'
})

// 当前项目ID
const currentProjectId = computed(() => projectStore.currentProject?.id)

const dialogVisible = ref(false)
const dialogTitle = ref('')
const isEdit = ref(false)

// 项目成员列表
const memberList = ref([])

const defectList = ref([])

const searchForm = reactive({
  keyword: '',
  severity: '',
  priority: '',
  status: '',
  module_id: null
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
  title: [{ required: true, message: '请输入缺陷标题', trigger: 'blur' }]
}

function getSeverityType(severity) {
  const map = { critical: 'danger', high: 'warning', medium: 'primary', low: 'info', trivial: 'info' }
  return map[severity] || 'info'
}

function getSeverityText(severity) {
  const map = { critical: '紧急', high: '高', medium: '中', low: '低', trivial: '轻微' }
  return map[severity] || severity
}

function getPriorityType(priority) {
  const map = { urgent: 'danger', high: 'warning', medium: 'primary', low: 'info' }
  return map[priority] || 'info'
}

function getPriorityText(priority) {
  const map = { urgent: '紧急', high: '高', medium: '中', low: '低' }
  return map[priority] || priority
}

function getStatusType(status) {
  const map = { new: 'info', assigned: 'warning', in_progress: 'primary', resolved: 'success', closed: 'info' }
  return map[status] || 'info'
}

function getStatusText(status) {
  const map = { new: '新建', assigned: '已分配', in_progress: '进行中', resolved: '已解决', closed: '已关闭' }
  return map[status] || status
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

// 模块操作命令
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

// 添加模块
function handleAddModule(parentId = null) {
  isModuleEdit.value = false
  moduleDialogTitle.value = parentId ? '新建子模块' : '新建模块'
  Object.assign(moduleForm, {
    id: null,
    name: '',
    parent_id: parentId
  })
  moduleDialogVisible.value = true
}

// 模块相关方法
async function loadModules() {
  if (!currentProjectId.value) return
  const res = await defectApi.getModules(currentProjectId.value)
  moduleTree.value = res.data || []
  moduleOptions.value = buildOptions(moduleTree.value)
}

function handleNodeClick(data) {
  selectedModuleId.value = data.id
  searchForm.module_id = data.id
  loadDefects()
}

function handleEditModule(data) {
  isModuleEdit.value = true
  moduleDialogTitle.value = '编辑模块'
  Object.assign(moduleForm, {
    id: data.id,
    name: data.name,
    parent_id: data.parent_id
  })
  moduleDialogVisible.value = true
}

function handleDeleteModule(data) {
  ElMessageBox.confirm('确定要删除这个模块吗？', '提示', { type: 'warning' })
    .then(() => defectApi.deleteModule(data.id))
    .then(() => {
      ElMessage.success('删除成功')
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
        ElMessage.success(isModuleEdit.value ? '更新成功' : '创建成功')
        moduleDialogVisible.value = false
        loadModules()
      })
    }
  })
}

async function loadDefects() {
  const res = await defectApi.getList({
    page: pagination.page,
    per_page: pagination.pageSize,
    project_id: currentProjectId.value,
    ...searchForm
  })
  defectList.value = res.data?.items || []
  pagination.total = res.data?.total || 0
}

async function loadMembers() {
  if (!currentProjectId.value) return
  const res = await projectApi.getMembers(currentProjectId.value)
  memberList.value = res.data?.items || []
}

function handleCreate() {
  isEdit.value = false
  dialogTitle.value = '新建缺陷'
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
  dialogTitle.value = '编辑缺陷'
  Object.assign(form, row)
  loadMembers()
  dialogVisible.value = true
}

function handleView(row) {
  router.push(`/defects/${row.id}`)
}

function handleDelete(row) {
  ElMessageBox.confirm('确定要删除这个缺陷吗？', '提示', { type: 'warning' })
    .then(() => defectApi.delete(row.id))
    .then(() => {
      ElMessage.success('删除成功')
      loadDefects()
    })
}

function handleSubmit() {
  formRef.value.validate((valid) => {
    if (valid) {
      const api = isEdit.value ? defectApi.update : defectApi.create
      const params = isEdit.value ? form.id : form
      api(params, isEdit.value ? form : null).then(() => {
        ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
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

// 监听项目变化，重新加载数据
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
.defect-page {
  height: 100%;
}

.page-layout {
  display: flex;
  height: calc(100vh - 120px);
  overflow: hidden;
}

.module-sidebar {
  flex-shrink: 0;
  background: #fff;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.resize-handle {
  width: 6px;
  flex-shrink: 0;
  background: #f0f2f5;
  cursor: col-resize;
  transition: background-color 0.2s;
  position: relative;
  z-index: 10;
}

.resize-handle:hover {
  background: #dcdfe6;
}

.resize-handle:active {
  background: #c0c4cc;
}

.module-header {
  padding: 12px 16px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 500;
}

.module-sidebar :deep(.el-tree) {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.tree-node {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-right: 8px;
  width: 100%;
}

.node-content {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 6px;
  overflow: hidden;
}

.folder-icon {
  color: #409eff;
  font-size: 16px;
  flex-shrink: 0;
}

.node-label {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
}

.node-more {
  opacity: 0;
  transition: opacity 0.2s;
}

.tree-node:hover .node-more {
  opacity: 1;
}

.content-area {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.content-area :deep(.el-card) {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.content-area :deep(.el-card__body) {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}
</style>

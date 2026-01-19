<template>
  <div class="page-container">
    <div class="page-layout" ref="layoutRef">
      <!-- 左侧目录树 -->
      <div class="page-sidebar folder-sidebar" :style="{ width: sidebarWidth + 'px' }">
        <div class="sidebar-header">
          <span class="sidebar-title">目录</span>
          <el-dropdown trigger="click" @command="handleFolderCommand">
            <el-button type="primary" link size="small">
              <el-icon><Plus /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="add">新建目录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
        <el-tree
          ref="folderTreeRef"
          :data="folderTree"
          :props="treeProps"
          :highlight-current="true"
          node-key="id"
          default-expand-all
          @node-click="handleFolderClick"
        >
          <template #default="{ node, data }">
            <div class="tree-node">
              <div class="node-content">
                <el-icon class="folder-icon"><Folder /></el-icon>
                <span class="node-label">{{ node.label }}</span>
                <span class="node-count">({{ data.plan_count || 0 }})</span>
              </div>
              <el-dropdown trigger="click" @command="(cmd) => handleFolderAction(cmd, data)">
                <el-icon class="node-more" @click.stop><MoreFilled /></el-icon>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="addSub">添加子目录</el-dropdown-item>
                    <el-dropdown-item command="edit">编辑</el-dropdown-item>
                    <el-dropdown-item command="delete">删除</el-dropdown-item>
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
          <div class="toolbar">
            <el-input
              v-model="searchForm.keyword"
              placeholder="搜索计划名称"
              clearable
              style="width: 200px"
              @change="loadPlans"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-select v-model="searchForm.status" placeholder="状态" clearable @change="loadPlans">
              <el-option label="草稿" value="draft" />
              <el-option label="进行中" value="active" />
              <el-option label="已完成" value="completed" />
              <el-option label="已取消" value="cancelled" />
            </el-select>
            <el-button :icon="Search" @click="showAdvancedSearch = true">高级搜索</el-button>
            <div style="flex: 1"></div>
            <el-button type="primary" :icon="Plus" @click="handleCreate">新建计划</el-button>
          </div>

          <el-table :data="planList" style="width: 100%">
            <el-table-column prop="plan_no" label="编号" width="120" />
            <el-table-column prop="name" label="计划名称" show-overflow-tooltip />
            <el-table-column prop="start_date" label="开始日期" width="120" />
            <el-table-column prop="end_date" label="结束日期" width="120" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="progress" label="执行进度" width="180">
              <template #default="{ row }">
                <el-progress
                  :percentage="row.progress?.progress || 0"
                  :color="getProgressColor(row.progress?.progress || 0)"
                />
              </template>
            </el-table-column>
            <el-table-column prop="progress" label="用例数" width="100">
              <template #default="{ row }">
                {{ row.progress?.total || 0 }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="260" fixed="right">
              <template #default="{ row }">
                <el-tooltip content="添加用例" placement="top">
                  <el-button type="primary" link size="small" @click="handleView(row)">
                    <el-icon><Plus /></el-icon>
                  </el-button>
                </el-tooltip>
                <el-tooltip content="编辑" placement="top">
                  <el-button type="primary" link size="small" @click="handleEdit(row)">
                    <el-icon><Edit /></el-icon>
                  </el-button>
                </el-tooltip>
                <el-tooltip content="手工执行" placement="top">
                  <el-button type="success" link size="small" @click="handleManualExecute(row)">
                    <el-icon><VideoPlay /></el-icon>
                  </el-button>
                </el-tooltip>
                <el-tooltip content="AI执行" placement="top">
                  <el-button type="warning" link size="small" @click="handleAIExecute(row)">
                    <el-icon><MagicStick /></el-icon>
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
            @current-change="loadPlans"
            @size-change="loadPlans"
            style="margin-top: 20px; justify-content: flex-end"
          />
        </el-card>
      </div>
    </div>

    <!-- 计划表单对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px" destroy-on-close @open="loadUsers">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="计划名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入计划名称" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="计划编号" prop="plan_no">
              <el-input v-model="form.plan_no" placeholder="自动生成" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="测试版本" prop="build_version">
              <el-input v-model="form.build_version" placeholder="如: v1.0.0" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="所属目录" prop="folder_id">
              <el-tree-select
                v-model="form.folder_id"
                :data="folderTreeForSelect"
                :props="treeProps"
                check-strictly
                clearable
                placeholder="请选择目录"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="优先级" prop="priority">
              <el-select v-model="form.priority" style="width: 100%">
                <el-option label="高" value="high" />
                <el-option label="中" value="medium" />
                <el-option label="低" value="low" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="开始日期" prop="start_date">
              <el-date-picker v-model="form.start_date" type="date" placeholder="选择日期" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束日期" prop="end_date">
              <el-date-picker v-model="form.end_date" type="date" placeholder="选择日期" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="状态" prop="status">
              <el-select v-model="form.status" style="width: 100%">
                <el-option label="草稿" value="draft" />
                <el-option label="进行中" value="active" />
                <el-option label="已完成" value="completed" />
                <el-option label="已取消" value="cancelled" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="指派给" prop="assigned_to">
              <el-select v-model="form.assigned_to" placeholder="选择成员" filterable clearable style="width: 100%">
                <el-option
                  v-for="user in userList"
                  :key="user.id"
                  :label="user.real_name || user.username"
                  :value="user.username"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 目录表单对话框 -->
    <el-dialog v-model="folderDialogVisible" :title="folderDialogTitle" width="500px">
      <el-form :model="folderForm" :rules="folderRules" ref="folderFormRef" label-width="100px">
        <el-form-item label="目录名称" prop="name">
          <el-input v-model="folderForm.name" placeholder="请输入目录名称" />
        </el-form-item>
        <el-form-item label="父目录" prop="parent_id">
          <el-tree-select
            v-model="folderForm.parent_id"
            :data="folderTreeForSelect"
            :props="treeProps"
            check-strictly
            clearable
            placeholder="请选择父目录"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="folderForm.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="folderDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleFolderSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 选择执行环境对话框 -->
    <el-dialog v-model="envDialogVisible" title="选择执行环境" width="500px" destroy-on-close>
      <el-form label-width="100px">
        <el-form-item label="执行环境" required>
          <el-select v-model="selectedEnvironmentId" placeholder="请选择执行环境" style="width: 100%">
            <el-option
              v-for="env in environmentList"
              :key="env.id"
              :label="`${env.name} (${env.url || env.base_url})`"
              :value="env.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="envDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmAIExecute">确定</el-button>
      </template>
    </el-dialog>

    <!-- 高级搜索对话框 -->
    <el-dialog v-model="showAdvancedSearch" title="高级搜索" width="600px" destroy-on-close>
      <el-form :model="advancedSearchForm" label-width="100px">
        <el-form-item label="计划编号">
          <el-input v-model="advancedSearchForm.plan_no" placeholder="例如: TP-0001" clearable />
        </el-form-item>
        <el-form-item label="计划名称">
          <el-input v-model="advancedSearchForm.name" placeholder="搜索计划名称" clearable />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="状态">
              <el-select v-model="advancedSearchForm.status" placeholder="选择状态" clearable style="width: 100%">
                <el-option label="草稿" value="draft" />
                <el-option label="进行中" value="active" />
                <el-option label="已完成" value="completed" />
                <el-option label="已取消" value="cancelled" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="优先级">
              <el-select v-model="advancedSearchForm.priority" placeholder="选择优先级" clearable style="width: 100%">
                <el-option label="高" value="high" />
                <el-option label="中" value="medium" />
                <el-option label="低" value="low" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="指派给">
          <el-input v-model="advancedSearchForm.assigned_to" placeholder="输入指派人用户名" clearable />
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="advancedSearchForm.keyword" placeholder="搜索所有字段" clearable />
        </el-form-item>
        <el-form-item label="创建时间">
          <el-date-picker
            v-model="advancedSearchForm.created_at"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="更新时间">
          <el-date-picker
            v-model="advancedSearchForm.updated_at"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="handleResetAdvancedSearch">重置</el-button>
        <el-button @click="showAdvancedSearch = false">取消</el-button>
        <el-button type="primary" @click="handleAdvancedSearch">搜索</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, List, Edit, VideoPlay, MagicStick, Delete, MoreFilled, Folder, Search } from '@element-plus/icons-vue'
import { testPlanApi, testPlanFolderApi } from '@/api/test-plan'
import { environmentApi } from '@/api/environment'
import { userApi } from '@/api/user'
import { useProjectStore } from '@/store/project'

const router = useRouter()
const projectStore = useProjectStore()
const formRef = ref()
const folderFormRef = ref()
const folderTreeRef = ref()
const layoutRef = ref()

// 侧边栏宽度相关
const sidebarWidth = ref(250)
const minWidth = 180
const maxWidth = 500
const isResizing = ref(false)

// 从 localStorage 恢复宽度
const savedWidth = localStorage.getItem('test-plan-sidebar-width')
if (savedWidth) {
  sidebarWidth.value = parseInt(savedWidth)
}

// 监听宽度变化并保存
watch(sidebarWidth, (newWidth) => {
  localStorage.setItem('test-plan-sidebar-width', newWidth.toString())
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

// 当前项目ID
const currentProjectId = computed(() => projectStore.currentProject?.id)

const dialogVisible = ref(false)
const dialogTitle = ref('')
const folderDialogVisible = ref(false)
const folderDialogTitle = ref('')
const isEdit = ref(false)
const isFolderEdit = ref(false)
const envDialogVisible = ref(false)
const currentPlanId = ref(null)
const currentFolderId = ref(null)

const planList = ref([])
const folderTree = ref([])
const folderTreeForSelect = computed(() => {
  // 添加一个"无目录"选项
  return [{ id: 0, name: '无目录', children: [] }, ...folderTree.value]
})
const environmentList = ref([])
const userList = ref([])
const selectedEnvironmentId = ref(null)

const searchForm = reactive({
  keyword: '',
  status: ''
})

const showAdvancedSearch = ref(false)
const advancedSearchForm = reactive({
  plan_no: '',
  name: '',
  status: '',
  priority: '',
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
  name: '',
  plan_no: '',
  build_version: '',
  folder_id: null,
  start_date: '',
  end_date: '',
  priority: 'medium',
  status: 'draft',
  assigned_to: "",
  description: ''
})

const folderForm = reactive({
  id: null,
  name: '',
  parent_id: null,
  description: ''
})

const rules = {
  name: [{ required: true, message: '请输入计划名称', trigger: 'blur' }]
}

const folderRules = {
  name: [{ required: true, message: '请输入目录名称', trigger: 'blur' }]
}

const treeProps = {
  children: 'children',
  label: 'name',
  value: 'id'
}

const currentFolderName = computed(() => {
  if (currentFolderId.value === null) return '全部测试计划'
  if (currentFolderId.value === 0) return '无目录'
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
  return findName(folderTree.value, currentFolderId.value) || '当前目录'
})

function getStatusType(status) {
  const map = { draft: 'info', active: 'success', completed: 'success', cancelled: 'danger' }
  return map[status] || 'info'
}

function getStatusText(status) {
  const map = { draft: '草稿', active: '进行中', completed: '已完成', cancelled: '已取消' }
  return map[status] || status
}

function getProgressColor(percentage) {
  if (percentage < 30) return 'var(--color-error)'
  if (percentage < 70) return 'var(--color-warning)'
  return 'var(--color-success)'
}

async function loadPlans() {
  const params = {
    page: pagination.page,
    per_page: pagination.pageSize,
    project_id: currentProjectId.value,
    folder_id: currentFolderId.value === 0 ? null : currentFolderId.value
  }

  // 基本搜索：只搜索名称
  if (searchForm.keyword) {
    params.name = searchForm.keyword
  }
  // 状态筛选
  if (searchForm.status) {
    params.status = searchForm.status
  }

  const res = await testPlanApi.getList(params)
  planList.value = res.data?.items || []
  pagination.total = res.data?.total || 0
}

// 高级搜索
function handleAdvancedSearch() {
  const params = {
    page: 1,
    per_page: pagination.pageSize,
    project_id: currentProjectId.value,
    folder_id: currentFolderId.value === 0 ? null : currentFolderId.value
  }

  // 添加高级搜索条件
  if (advancedSearchForm.plan_no) params.plan_no = advancedSearchForm.plan_no
  if (advancedSearchForm.name) params.name = advancedSearchForm.name
  if (advancedSearchForm.status) params.status = advancedSearchForm.status
  if (advancedSearchForm.priority) params.priority = advancedSearchForm.priority
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

  // 同步到基本搜索的显示
  searchForm.keyword = advancedSearchForm.name || advancedSearchForm.keyword || ''
  searchForm.status = advancedSearchForm.status || ''

  pagination.page = 1
  testPlanApi.getList(params).then(res => {
    planList.value = res.data?.items || []
    pagination.total = res.data?.total || 0
    showAdvancedSearch.value = false
  })
}

// 重置高级搜索
function handleResetAdvancedSearch() {
  Object.assign(advancedSearchForm, {
    plan_no: '',
    name: '',
    status: '',
    priority: '',
    assigned_to: '',
    keyword: '',
    created_at: null,
    updated_at: null
  })
}

async function loadFolderTree() {
  try {
    const res = await testPlanFolderApi.getTree({
      project_id: currentProjectId.value
    })
    folderTree.value = res.data || []
  } catch (error) {
    console.error('加载目录树失败:', error)
  }
}

// 加载用户列表
async function loadUsers() {
  try {
    const res = await userApi.getList({ per_page: 1000 })
    userList.value = res.data?.items || []
  } catch (error) {
    console.error('加载用户列表失败:', error)
  }
}

// 目录点击事件
function handleFolderClick(data) {
  currentFolderId.value = data.id === 'all' ? null : data.id
  pagination.page = 1
  loadPlans()
}

// 目录操作命令
function handleFolderCommand(command) {
  if (command === 'add') {
    handleAddFolder()
  }
}

function handleFolderAction(command, data) {
  if (command === 'addSub') {
    handleAddFolder(data.id)
  } else if (command === 'edit') {
    handleEditFolder(data)
  } else if (command === 'delete') {
    handleDeleteFolder(data)
  }
}

// 添加目录
function handleAddFolder(parentId = null) {
  isFolderEdit.value = false
  folderDialogTitle.value = parentId ? '新建子目录' : '新建目录'
  Object.assign(folderForm, {
    id: null,
    name: '',
    parent_id: parentId,
    description: ''
  })
  folderDialogVisible.value = true
}

// 编辑目录
function handleEditFolder(data) {
  isFolderEdit.value = true
  folderDialogTitle.value = '编辑目录'
  Object.assign(folderForm, {
    id: data.id,
    name: data.name,
    parent_id: data.parent_id,
    description: data.description
  })
  folderDialogVisible.value = true
}

// 删除目录
function handleDeleteFolder(data) {
  ElMessageBox.confirm('确定要删除这个目录吗？删除后目录下的测试计划将变为无目录状态。', '提示', {
    type: 'warning'
  }).then(() => {
    testPlanFolderApi.delete(data.id).then(() => {
      ElMessage.success('删除成功')
      loadFolderTree()
      if (currentFolderId.value === data.id) {
        currentFolderId.value = null
      }
    })
  })
}

// 提交目录表单
function handleFolderSubmit() {
  folderFormRef.value.validate((valid) => {
    if (valid) {
      const data = {
        ...folderForm,
        project_id: currentProjectId.value
      }
      const api = isFolderEdit.value ? testPlanFolderApi.update : testPlanFolderApi.create
      const params = isFolderEdit.value ? folderForm.id : data
      api(params, isFolderEdit.value ? data : null).then(() => {
        ElMessage.success(isFolderEdit.value ? '更新成功' : '创建成功')
        folderDialogVisible.value = false
        loadFolderTree()
      })
    }
  })
}

function handleCreate() {
  isEdit.value = false
  dialogTitle.value = '新建测试计划'
  Object.assign(form, {
    id: null,
    name: '',
    plan_no: '',
    build_version: '',
    folder_id: currentFolderId.value === 0 ? null : currentFolderId.value,
    start_date: '',
    end_date: '',
    priority: 'medium',
    assigned_to: "",
    description: '',
    project_id: currentProjectId.value
  })
  dialogVisible.value = true
}

function handleEdit(row) {
  isEdit.value = true
  dialogTitle.value = '编辑测试计划'
  Object.assign(form, {
    ...row,
    start_date: row.start_date || '',
    end_date: row.end_date || '',
    status: row.status || 'draft'
  })
  dialogVisible.value = true
}

function handleView(row) {
  router.push(`/test-executions/${row.id}`)
}

// 手工执行 - 跳转到测试计划执行页面
function handleManualExecute(row) {
  router.push(`/test-executions/${row.id}`)
}

// 加载环境列表
async function loadEnvironments() {
  try {
    const res = await environmentApi.getList({
      per_page: 100
    })
    environmentList.value = res.data?.items || []
  } catch (error) {
    console.error('加载环境列表失败:', error)
  }
}

// AI执行 - 选择环境后跳转到AI执行页面
function handleAIExecute(row) {
  currentPlanId.value = row.id
  selectedEnvironmentId.value = null
  loadEnvironments()
  envDialogVisible.value = true
}

// 确认AI执行
async function handleConfirmAIExecute() {
  if (!selectedEnvironmentId.value) {
    ElMessage.warning('请选择执行环境')
    return
  }

  // 获取测试计划详情，获取所有用例
  try {
    const res = await testPlanApi.getDetail(currentPlanId.value)
    const testCases = res.data?.test_cases || []
    if (testCases.length === 0) {
      ElMessage.warning('当前计划没有用例，请先添加用例')
      envDialogVisible.value = false
      return
    }

    // 获取所有用例ID
    const caseIds = testCases.map(tc => tc.test_case_id).join(',')

    envDialogVisible.value = false

    // 跳转到AI执行页面
    router.push({
      path: '/test-cases/ai-execution',
      query: {
        caseIds: caseIds,
        environmentId: selectedEnvironmentId.value,
        planId: currentPlanId.value
      }
    })
  } catch (error) {
    console.error('获取计划详情失败:', error)
    ElMessage.error('获取计划详情失败')
  }
}

function handleDelete(row) {
  ElMessageBox.confirm('确定要删除这个计划吗？', '提示', {
    type: 'warning'
  }).then(() => {
    testPlanApi.delete(row.id).then(() => {
      ElMessage.success('删除成功')
      loadPlans()
    })
  })
}

function handleSubmit() {
  formRef.value.validate((valid) => {
    if (valid) {
      // 处理空字符串字段，转换为 null
      const data = {
        name: form.name,
        plan_no: form.plan_no || null,
        build_version: form.build_version || null,
        folder_id: form.folder_id || null,
        start_date: form.start_date ? new Date(form.start_date).toISOString().split('T')[0] : null,
        end_date: form.end_date ? new Date(form.end_date).toISOString().split('T')[0] : null,
        priority: form.priority,
        status: form.status,
        assigned_to: form.assigned_to || null,
        description: form.description || null,
        project_id: form.project_id
      }
      const api = isEdit.value ? testPlanApi.update : testPlanApi.create
      const params = isEdit.value ? form.id : data
      api(params, isEdit.value ? data : null).then(() => {
        ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
        dialogVisible.value = false
        loadPlans()
      })
    }
  })
}

onMounted(() => {
  if (currentProjectId.value) {
    loadPlans()
    loadFolderTree()
  }
})

// 监听项目变化，重新加载数据
watch(currentProjectId, (newVal, oldVal) => {
  if (newVal && newVal !== oldVal) {
    currentFolderId.value = null
    loadPlans()
    loadFolderTree()
  }
})
</script>

<style scoped>
/* Page-specific styles only - general layout styles are in page-layout.css */
</style>

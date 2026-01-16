<template>
  <div class="defect-page">
    <el-card>
      <template #header>
        <div class="page-header">
          <span>缺陷管理</span>
          <el-button type="primary" :icon="'Plus'" @click="handleCreate">新建缺陷</el-button>
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
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleView(row)">查看</el-button>
            <el-button type="primary" link size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
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

    <!-- 缺陷表单对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="800px" destroy-on-close>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="缺陷标题" prop="title">
          <el-input v-model="form.title" />
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
              <el-input v-model="form.assigned_to" />
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
import { defectApi } from '@/api/defect'
import { useProjectStore } from '@/store/project'

const router = useRouter()
const projectStore = useProjectStore()
const formRef = ref()

// 当前项目ID
const currentProjectId = computed(() => projectStore.currentProject?.id)

const dialogVisible = ref(false)
const dialogTitle = ref('')
const isEdit = ref(false)

const defectList = ref([])

const searchForm = reactive({
  keyword: '',
  severity: '',
  priority: '',
  status: ''
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
  actual_behavior: ''
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
    project_id: currentProjectId.value
  })
  dialogVisible.value = true
}

function handleEdit(row) {
  isEdit.value = true
  dialogTitle.value = '编辑缺陷'
  Object.assign(form, row)
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
  }
})

// 监听项目变化，重新加载数据
watch(currentProjectId, (newVal, oldVal) => {
  if (newVal && newVal !== oldVal) {
    loadDefects()
  }
})
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}
</style>

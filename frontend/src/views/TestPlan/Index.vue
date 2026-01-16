<template>
  <div class="test-plan-page">
    <el-card>
      <template #header>
        <div class="page-header">
          <span>测试计划管理</span>
          <el-button type="primary" @click="handleCreate">新建计划</el-button>
        </div>
      </template>

      <div class="toolbar">
        <el-input
          v-model="searchForm.keyword"
          placeholder="搜索计划"
          clearable
          style="width: 200px"
          @change="loadPlans"
        />
        <el-select v-model="searchForm.status" placeholder="状态" clearable @change="loadPlans">
          <el-option label="草稿" value="draft" />
          <el-option label="进行中" value="active" />
          <el-option label="已完成" value="completed" />
          <el-option label="已取消" value="cancelled" />
        </el-select>
        <div style="flex: 1"></div>
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
        <el-table-column label="操作" width="320" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleView(row)">用例管理</el-button>
            <el-button type="primary" link size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="success" link size="small" @click="handleExecute(row)">执行</el-button>
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
        @current-change="loadPlans"
        @size-change="loadPlans"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <!-- 计划表单对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px" destroy-on-close>
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
            <el-form-item label="优先级" prop="priority">
              <el-select v-model="form.priority" style="width: 100%">
                <el-option label="高" value="high" />
                <el-option label="中" value="medium" />
                <el-option label="低" value="low" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="启用自动化" prop="automation_enabled">
              <el-switch v-model="form.automation_enabled" />
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
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { testPlanApi } from '@/api/test-plan'
import { useProjectStore } from '@/store/project'

const router = useRouter()
const projectStore = useProjectStore()
const formRef = ref()

// 当前项目ID
const currentProjectId = computed(() => projectStore.currentProject?.id)

const dialogVisible = ref(false)
const dialogTitle = ref('')
const isEdit = ref(false)

const planList = ref([])

const searchForm = reactive({
  keyword: '',
  status: ''
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
  start_date: '',
  end_date: '',
  priority: 'medium',
  automation_enabled: false,
  description: ''
})

const rules = {
  name: [{ required: true, message: '请输入计划名称', trigger: 'blur' }]
}

function getStatusType(status) {
  const map = { draft: 'info', active: 'success', completed: 'success', cancelled: 'danger' }
  return map[status] || 'info'
}

function getStatusText(status) {
  const map = { draft: '草稿', active: '进行中', completed: '已完成', cancelled: '已取消' }
  return map[status] || status
}

function getProgressColor(percentage) {
  if (percentage < 30) return '#f56c6c'
  if (percentage < 70) return '#e6a23c'
  return '#67c23a'
}

async function loadPlans() {
  const res = await testPlanApi.getList({
    page: pagination.page,
    per_page: pagination.pageSize,
    project_id: currentProjectId.value,
    ...searchForm
  })
  planList.value = res.data?.items || []
  pagination.total = res.data?.total || 0
}

function handleCreate() {
  isEdit.value = false
  dialogTitle.value = '新建测试计划'
  Object.assign(form, {
    id: null,
    name: '',
    plan_no: '',
    build_version: '',
    start_date: '',
    end_date: '',
    priority: 'medium',
    automation_enabled: false,
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
    end_date: row.end_date || ''
  })
  dialogVisible.value = true
}

function handleView(row) {
  router.push(`/test-executions/${row.id}`)
}

function handleExecute(row) {
  router.push(`/test-executions/${row.id}`)
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
      const data = {
        ...form,
        start_date: form.start_date ? new Date(form.start_date).toISOString().split('T')[0] : null,
        end_date: form.end_date ? new Date(form.end_date).toISOString().split('T')[0] : null
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
  }
})

// 监听项目变化，重新加载数据
watch(currentProjectId, (newVal, oldVal) => {
  if (newVal && newVal !== oldVal) {
    loadPlans()
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

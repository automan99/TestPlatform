<template>
  <div class="execution-page">
    <el-page-header @back="goBack" title="返回">
      <template #content>
        <span class="page-title">{{ planName }}</span>
      </template>
    </el-page-header>

    <el-card style="margin-top: 20px">
      <template #header>
        <div class="page-header">
          <span>用例列表</span>
          <div class="header-actions">
            <el-button type="primary" @click="showAddCaseDialog">添加用例</el-button>
            <el-button type="success" @click="handleRunAll">批量执行</el-button>
          </div>
        </div>
      </template>

      <el-table :data="caseList" style="width: 100%" @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55" />
        <el-table-column label="编号" width="120">
          <template #default="{ row }">
            {{ row.case_no || `CASE-${row.test_case_id}` }}
          </template>
        </el-table-column>
        <el-table-column prop="name" label="用例名称" show-overflow-tooltip />
        <el-table-column prop="priority" label="优先级" width="100">
          <template #default="{ row }">
            <el-tag :type="getPriorityType(row.priority)">{{ row.priority }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_status" label="执行状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getExecutionStatusType(row.last_status)">
              {{ getExecutionStatusText(row.last_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="assignee" label="执行人" width="120" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleExecute(row)">执行</el-button>
            <el-button type="danger" link size="small" @click="handleRemove(row)">移除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="selectedCases.length > 0" style="margin-top: 16px">
        <el-button type="danger" @click="handleBatchRemove">批量移除 ({{ selectedCases.length }})</el-button>
        <el-button type="success" @click="handleBatchExecute">批量执行 ({{ selectedCases.length }})</el-button>
      </div>
    </el-card>

    <!-- 添加用例对话框 -->
    <el-dialog v-model="addCaseDialogVisible" title="添加测试用例" width="900px" destroy-on-close>
      <div class="toolbar">
        <el-input v-model="caseSearchForm.keyword" placeholder="搜索用例" clearable style="width: 200px" @change="loadAvailableCases" />
        <el-select v-model="caseSearchForm.suite_id" placeholder="选择文件夹" clearable @change="loadAvailableCases">
          <el-option v-for="suite in suiteOptions" :key="suite.id" :label="suite.name" :value="suite.id" />
        </el-select>
        <div style="flex: 1"></div>
        <span>已选择: {{ selectedCasesToAdd.length }}</span>
      </div>

      <el-table
        :data="availableCases"
        @selection-change="handleAddCaseSelectionChange"
        style="width: 100%; max-height: 400px; overflow-y: auto"
      >
        <el-table-column type="selection" width="55" :selectable="checkCaseSelectable" />
        <el-table-column prop="case_no" label="编号" width="120" />
        <el-table-column prop="name" label="用例名称" show-overflow-tooltip />
        <el-table-column prop="priority" label="优先级" width="100">
          <template #default="{ row }">
            <el-tag :type="getPriorityType(row.priority)">{{ row.priority }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="case_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag type="info">{{ row.case_type }}</el-tag>
          </template>
        </el-table-column>
      </el-table>

      <template #footer>
        <el-button @click="addCaseDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleAddCases" :disabled="selectedCasesToAdd.length === 0">
          添加 ({{ selectedCasesToAdd.length }})
        </el-button>
      </template>
    </el-dialog>

    <!-- 执行结果对话框 -->
    <el-dialog v-model="executeDialogVisible" title="执行测试用例" width="700px" destroy-on-close>
      <el-form :model="executeForm" label-width="100px">
        <el-form-item label="用例名称">
          <span>{{ currentCase?.name }}</span>
        </el-form-item>
        <el-form-item label="执行结果">
          <el-radio-group v-model="executeForm.status">
            <el-radio label="passed">通过</el-radio>
            <el-radio label="failed">失败</el-radio>
            <el-radio label="blocked">阻塞</el-radio>
            <el-radio label="skipped">跳过</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="实际结果">
          <el-input v-model="executeForm.actual_result" type="textarea" :rows="4" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="executeForm.notes" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="关联缺陷">
          <el-button v-if="!executeForm.defect_ids" @click="handleCreateDefect">
            新建缺陷
          </el-button>
          <el-tag v-else closable @close="executeForm.defect_ids = null">
            已关联缺陷
          </el-tag>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="executeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitExecution">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { testPlanApi, testExecutionApi } from '@/api/test-plan'
import { testCaseApi } from '@/api/test-case'

const route = useRoute()
const router = useRouter()

const planId = ref(parseInt(route.params.planId))
const planName = ref('')
const caseList = ref([])
const selectedCases = ref([])

const addCaseDialogVisible = ref(false)
const executeDialogVisible = ref(false)
const currentCase = ref(null)

const availableCases = ref([])
const selectedCasesToAdd = ref([])
const suiteOptions = ref([])

const caseSearchForm = reactive({
  keyword: '',
  suite_id: null
})

const executeForm = reactive({
  status: 'passed',
  actual_result: '',
  notes: '',
  defect_ids: null
})

function goBack() {
  router.push('/test-plans')
}

function getPriorityType(priority) {
  const map = { critical: 'danger', high: 'warning', medium: 'primary', low: 'info' }
  return map[priority] || 'info'
}

function getExecutionStatusType(status) {
  const map = {
    not_executed: 'info',
    passed: 'success',
    failed: 'danger',
    blocked: 'warning',
    skipped: 'info'
  }
  return map[status] || 'info'
}

function getExecutionStatusText(status) {
  const map = {
    not_executed: '未执行',
    passed: '通过',
    failed: '失败',
    blocked: '阻塞',
    skipped: '跳过'
  }
  return map[status] || status
}

async function loadPlanDetail() {
  try {
    const res = await testPlanApi.getDetail(planId.value)
    planName.value = res.data?.name || ''
    caseList.value = res.data?.test_cases || []
  } catch (error) {
    console.error('加载测试计划失败:', error)
  }
}

async function loadAvailableCases() {
  try {
    const res = await testCaseApi.getList({
      per_page: 100,
      ...caseSearchForm
    })
    availableCases.value = res.data?.items || []
  } catch (error) {
    console.error('加载可用用例失败:', error)
  }
}

async function loadSuites() {
  try {
    const res = await testCaseApi.testSuite.getTree()
    const flattenSuites = (suites) => {
      let result = []
      for (const suite of suites) {
        result.push(suite)
        if (suite.children) {
          result = result.concat(flattenSuites(suite.children))
        }
      }
      return result
    }
    suiteOptions.value = flattenSuites(res.data || [])
  } catch (error) {
    console.error('加载文件夹失败:', error)
  }
}

function handleSelectionChange(selection) {
  selectedCases.value = selection
}

function checkCaseSelectable(row) {
  // 检查用例是否已经在计划中
  return !caseList.value.some(c => c.test_case_id === row.id)
}

function handleAddCaseSelectionChange(selection) {
  selectedCasesToAdd.value = selection
}

function showAddCaseDialog() {
  addCaseDialogVisible.value = true
  selectedCasesToAdd.value = []
  loadAvailableCases()
  loadSuites()
}

async function handleAddCases() {
  try {
    const caseIds = selectedCasesToAdd.value.map(c => c.id)
    await testPlanApi.addCases(planId.value, { case_ids: caseIds })
    ElMessage.success(`成功添加 ${caseIds.length} 条用例`)
    addCaseDialogVisible.value = false
    loadPlanDetail()
  } catch (error) {
    ElMessage.error('添加用例失败')
  }
}

function handleRemove(row) {
  ElMessageBox.confirm('确定要从计划中移除这条用例吗？', '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      await testPlanApi.removeCases(planId.value, { case_ids: [row.test_case_id] })
      ElMessage.success('移除成功')
      loadPlanDetail()
    } catch (error) {
      ElMessage.error('移除失败')
    }
  })
}

function handleBatchRemove() {
  ElMessageBox.confirm(`确定要移除选中的 ${selectedCases.value.length} 条用例吗？`, '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      const caseIds = selectedCases.value.map(c => c.test_case_id)
      await testPlanApi.removeCases(planId.value, { case_ids: caseIds })
      ElMessage.success('移除成功')
      loadPlanDetail()
    } catch (error) {
      ElMessage.error('移除失败')
    }
  })
}

function handleExecute(row) {
  currentCase.value = row
  executeForm.status = 'passed'
  executeForm.actual_result = ''
  executeForm.notes = ''
  executeForm.defect_ids = null
  executeDialogVisible.value = true
}

function handleBatchExecute() {
  ElMessage.info('批量执行功能开发中...')
}

function handleCreateDefect() {
  ElMessage.info('跳转到缺陷创建页面')
}

async function handleSubmitExecution() {
  try {
    await testExecutionApi.create({
      test_plan_id: planId.value,
      test_case_id: currentCase.value.test_case_id,
      test_plan_case_id: currentCase.value.id,
      status: executeForm.status,
      actual_result: executeForm.actual_result,
      notes: executeForm.notes,
      executed_by: 'current_user'
    })
    ElMessage.success('提交成功')
    executeDialogVisible.value = false
    loadPlanDetail()
  } catch (error) {
    ElMessage.error('提交失败')
  }
}

function handleRunAll() {
  ElMessage.info('批量执行功能开发中...')
}

onMounted(() => {
  loadPlanDetail()
})
</script>

<style scoped>
.page-title {
  font-size: 16px;
  font-weight: 500;
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

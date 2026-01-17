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
            <el-button type="success" @click="handleBatchManualExecute">批量手工执行</el-button>
            <el-button type="warning" @click="handleBatchAIExecute">批量AI执行</el-button>
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
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-tooltip content="手工执行" placement="top">
              <el-button type="primary" link size="small" @click="handleManualExecute(row)">
                <el-icon><VideoPlay /></el-icon>
              </el-button>
            </el-tooltip>
            <el-tooltip content="AI执行" placement="top">
              <el-button type="warning" link size="small" @click="handleAIExecute(row)">
                <el-icon><MagicStick /></el-icon>
              </el-button>
            </el-tooltip>
            <el-tooltip content="移除" placement="top">
              <el-button type="danger" link size="small" @click="handleRemove(row)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </el-tooltip>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="selectedCases.length > 0" style="margin-top: 16px">
        <el-button type="danger" @click="handleBatchRemove">批量移除 ({{ selectedCases.length }})</el-button>
        <el-button type="success" @click="handleBatchManualExecute">批量手工执行 ({{ selectedCases.length }})</el-button>
        <el-button type="warning" @click="handleBatchAIExecuteSelected">批量AI执行 ({{ selectedCases.length }})</el-button>
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

    <!-- 手工执行结果对话框 -->
    <el-dialog v-model="executeDialogVisible" title="手工执行测试用例" width="800px" destroy-on-close>
      <el-form :model="executeForm" label-width="100px">
        <el-form-item label="用例名称">
          <span>{{ currentCase?.name }}</span>
        </el-form-item>
        <el-form-item label="前置条件">
          <div class="condition-text">{{ currentCase?.preconditions || '无' }}</div>
        </el-form-item>
        <el-form-item label="测试步骤">
          <el-table :data="getStepList(currentCase?.steps)" border style="width: 100%">
            <el-table-column label="序号" width="60" align="center">
              <template #default="{ $index }">
                <span>{{ $index + 1 }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="step" label="步骤描述" />
            <el-table-column prop="expected" label="期望结果" />
          </el-table>
        </el-form-item>
        <el-form-item label="执行状态" required>
          <el-radio-group v-model="executeForm.status">
            <el-radio value="passed">通过</el-radio>
            <el-radio value="failed">失败</el-radio>
            <el-radio value="blocked">阻塞</el-radio>
            <el-radio value="skipped">跳过</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="实际结果">
          <el-input v-model="executeForm.actual_result" type="textarea" :rows="4" placeholder="请输入实际执行结果..." />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="executeForm.notes" type="textarea" :rows="2" placeholder="其他备注信息..." />
        </el-form-item>
        <el-form-item label="执行时长(秒)">
          <el-input-number v-model="executeForm.duration" :min="0" :max="99999" placeholder="执行时长" />
        </el-form-item>
        <el-form-item label="关联缺陷">
          <div style="display: flex; gap: 8px; width: 100%">
            <el-select
              v-model="executeForm.defect_ids"
              multiple
              filterable
              placeholder="选择已有缺陷"
              style="flex: 1"
            >
              <el-option
                v-for="defect in defectList"
                :key="defect.id"
                :label="`${defect.defect_no || `DEF-${defect.id}`} - ${defect.title}`"
                :value="defect.id"
              />
            </el-select>
            <el-button type="primary" @click="handleCreateDefect">创建缺陷</el-button>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="executeDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="executing" @click="handleSubmitExecution">提交执行结果</el-button>
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
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { VideoPlay, MagicStick, Delete } from '@element-plus/icons-vue'
import { testPlanApi, testExecutionApi } from '@/api/test-plan'
import { testCaseApi } from '@/api/test-case'
import { environmentApi } from '@/api/environment'
import { defectApi } from '@/api/defect'

const route = useRoute()
const router = useRouter()

const planId = ref(parseInt(route.params.planId))
const planName = ref('')
const caseList = ref([])
const selectedCases = ref([])

const addCaseDialogVisible = ref(false)
const executeDialogVisible = ref(false)
const envDialogVisible = ref(false)
const executing = ref(false)
const currentCase = ref(null)
const pendingAIExecuteCases = ref([]) // 待AI执行的用例

const availableCases = ref([])
const selectedCasesToAdd = ref([])
const suiteOptions = ref([])
const environmentList = ref([])
const defectList = ref([])
const selectedEnvironmentId = ref(null)

const caseSearchForm = reactive({
  keyword: '',
  suite_id: null
})

const executeForm = reactive({
  status: 'passed',
  actual_result: '',
  notes: '',
  duration: 0,
  defect_ids: []
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

// 解析步骤列表
function getStepList(steps) {
  if (!steps) return [{ step: '无', expected: '无' }]

  // 尝试解析 JSON
  try {
    let parsed = steps
    // 如果是字符串，尝试解析
    if (typeof steps === 'string') {
      // 尝试直接解析
      try {
        parsed = JSON.parse(steps)
      } catch {
        // 如果失败，尝试去除转义字符后再解析
        try {
          // 处理被双重转义的情况
          const unescaped = steps.replace(/\\"/g, '"').replace(/\\\\/g, '\\')
          parsed = JSON.parse(unescaped)
        } catch {
          // 仍然失败，返回提示
          return [{ step: '步骤格式错误', expected: '请检查数据格式' }]
        }
      }
    }

    // 确保是数组
    if (Array.isArray(parsed)) {
      return parsed.length > 0 ? parsed : [{ step: '无', expected: '无' }]
    }
  } catch (e) {
    console.error('解析步骤失败:', e, steps)
  }

  return [{ step: '无', expected: '无' }]
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

// 手工执行单个用例
function handleManualExecute(row) {
  currentCase.value = row
  executeForm.status = 'passed'
  executeForm.actual_result = ''
  executeForm.notes = ''
  executeForm.duration = 0
  executeForm.defect_ids = []
  executeDialogVisible.value = true
  loadDefects()
}

// 加载缺陷列表
async function loadDefects() {
  try {
    const res = await defectApi.getList({
      per_page: 100
    })
    defectList.value = res.data?.items || []
  } catch (error) {
    console.error('加载缺陷列表失败:', error)
  }
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

// AI执行单个用例
function handleAIExecute(row) {
  pendingAIExecuteCases.value = [row]
  envDialogVisible.value = true
  loadEnvironments()
}

// 批量手工执行
function handleBatchManualExecute() {
  if (selectedCases.value.length === 0) {
    ElMessage.warning('请先选择要执行的用例')
    return
  }
  // 打开第一个用例的执行对话框
  handleManualExecute(selectedCases.value[0])
}

// 批量AI执行
function handleBatchAIExecute() {
  // AI执行所有用例
  if (caseList.value.length === 0) {
    ElMessage.warning('当前计划没有用例')
    return
  }
  pendingAIExecuteCases.value = [...caseList.value]
  envDialogVisible.value = true
  loadEnvironments()
}

// 批量AI执行选中的用例
function handleBatchAIExecuteSelected() {
  if (selectedCases.value.length === 0) {
    ElMessage.warning('请先选择要执行的用例')
    return
  }
  pendingAIExecuteCases.value = [...selectedCases.value]
  envDialogVisible.value = true
  loadEnvironments()
}

// 确认AI执行
function handleConfirmAIExecute() {
  if (!selectedEnvironmentId.value) {
    ElMessage.warning('请选择执行环境')
    return
  }

  envDialogVisible.value = false

  const caseIds = pendingAIExecuteCases.value.map(c => c.test_case_id).join(',')

  // 跳转到AI执行页面
  router.push({
    path: '/test-cases/ai-execution',
    query: {
      caseIds: caseIds,
      environmentId: selectedEnvironmentId.value,
      planId: planId.value
    }
  })
}

function handleCreateDefect() {
  router.push({
    path: '/defects',
    query: {
      action: 'create',
      test_case_id: currentCase.value?.test_case_id,
      test_result: executeForm.status === 'failed' ? executeForm.actual_result : ''
    }
  })
}

// 提交手工执行结果
async function handleSubmitExecution() {
  if (!executeForm.status) {
    ElMessage.warning('请选择执行状态')
    return
  }

  executing.value = true
  try {
    await testExecutionApi.create({
      test_plan_id: planId.value,
      test_case_id: currentCase.value.test_case_id,
      test_plan_case_id: currentCase.value.id,
      status: executeForm.status,
      actual_result: executeForm.actual_result,
      notes: executeForm.notes,
      duration: executeForm.duration,
      defect_ids: executeForm.defect_ids,
      executed_by: 'current_user'
    })
    ElMessage.success('提交成功')
    executeDialogVisible.value = false
    loadPlanDetail()
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error('提交失败: ' + (error.response?.data?.message || error.message))
  } finally {
    executing.value = false
  }
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

.condition-text {
  padding: 12px;
  background-color: #f5f7fa;
  border-radius: 4px;
  min-height: 40px;
  white-space: pre-wrap;
  word-break: break-word;
}
</style>

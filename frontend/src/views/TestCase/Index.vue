<template>
  <div class="test-case-page">
    <el-card>
      <template #header>
        <div class="page-header">
          <span>测试用例管理</span>
          <div class="header-actions">
            <el-button type="primary" :icon="Plus" @click="handleCreateSuite">新建文件夹</el-button>
            <el-button type="primary" :icon="Plus" @click="handleCreateCase">新建用例</el-button>
          </div>
        </div>
      </template>

      <el-container>
        <el-aside width="250px" class="suite-tree">
          <el-input
            v-model="filterText"
            placeholder="搜索文件夹"
            :prefix-icon="Search"
            clearable
            style="margin-bottom: 12px"
          />
          <el-tree
            ref="treeRef"
            :data="suiteTree"
            :props="{ children: 'children', label: 'name' }"
            :filter-node-method="filterNode"
            node-key="id"
            highlight-current
            @node-click="handleNodeClick"
          >
            <template #default="{ node, data }">
              <span class="tree-node">
                <el-icon><Folder /></el-icon>
                <span>{{ node.label }}</span>
                <span class="node-count">({{ data.case_count || 0 }})</span>
              </span>
            </template>
          </el-tree>
        </el-aside>

        <el-main class="case-list">
          <div class="toolbar">
            <el-input
              v-model="searchForm.keyword"
              placeholder="搜索用例"
              clearable
              style="width: 200px"
              @change="loadCases"
            />
            <el-select v-model="searchForm.priority" placeholder="优先级" clearable @change="loadCases">
              <el-option label="高" value="high" />
              <el-option label="中" value="medium" />
              <el-option label="低" value="low" />
            </el-select>
            <el-select v-model="searchForm.status" placeholder="状态" clearable @change="loadCases">
              <el-option label="草稿" value="draft" />
              <el-option label="激活" value="active" />
              <el-option label="归档" value="archived" />
            </el-select>
            <div style="flex: 1"></div>
            <el-button
              v-if="selectedCases.length > 0"
              type="danger"
              @click="handleBatchDelete"
            >
              批量删除 ({{ selectedCases.length }})
            </el-button>
            <el-button
              v-if="selectedCases.length > 0"
              @click="handleBatchMove"
            >
              批量移动
            </el-button>
          </div>

          <el-table
            :data="caseList"
            @selection-change="handleSelectionChange"
            style="width: 100%"
          >
            <el-table-column type="selection" width="55" />
            <el-table-column label="编号" width="120">
              <template #default="{ row }">
                {{ row.case_no || `CASE-${row.id}` }}
              </template>
            </el-table-column>
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
            <el-table-column prop="automation_status" label="自动化" width="100">
              <template #default="{ row }">
                <el-tag :type="row.automation_status === 'automated' ? 'success' : 'info'">
                  {{ row.automation_status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="320" fixed="right">
              <template #default="{ row }">
                <el-button type="info" link size="small" @click="handleView(row)">查看</el-button>
                <el-button type="success" link size="small" @click="handleExecute(row)">执行</el-button>
                <el-button type="warning" link size="small" @click="handleAIExecute(row)">AI执行</el-button>
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
            @current-change="loadCases"
            @size-change="loadCases"
            style="margin-top: 20px; justify-content: flex-end"
          />
        </el-main>
      </el-container>
    </el-card>

    <!-- 用例表单对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="900px"
      destroy-on-close
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="用例名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入用例名称" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="用例编号" prop="case_no">
              <el-input v-model="form.case_no" placeholder="自动生成" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="所属文件夹" prop="suite_id">
              <el-cascader
                v-model="form.suite_id"
                :options="suiteOptions"
                :props="{ value: 'id', label: 'name', checkStrictly: true }"
                clearable
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="优先级" prop="priority">
              <el-select v-model="form.priority" style="width: 100%">
                <el-option label="紧急" value="critical" />
                <el-option label="高" value="high" />
                <el-option label="中" value="medium" />
                <el-option label="低" value="low" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="用例类型" prop="case_type">
              <el-select v-model="form.case_type" style="width: 100%">
                <el-option label="功能测试" value="functional" />
                <el-option label="性能测试" value="performance" />
                <el-option label="安全测试" value="security" />
                <el-option label="UI测试" value="ui" />
                <el-option label="API测试" value="api" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="自动化状态" prop="automation_status">
              <el-select v-model="form.automation_status" style="width: 100%">
                <el-option label="手工" value="manual" />
                <el-option label="自动化" value="automated" />
                <el-option label="半自动化" value="semi-automated" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="状态" prop="status">
              <el-select v-model="form.status" style="width: 100%">
                <el-option label="草稿" value="draft" />
                <el-option label="激活" value="active" />
                <el-option label="归档" value="archived" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="前置条件" prop="preconditions">
          <el-input v-model="form.preconditions" type="textarea" :rows="2" placeholder="测试执行前需要满足的条件..." />
        </el-form-item>

        <!-- 测试步骤表格 -->
        <el-form-item label="测试步骤" prop="stepList">
          <div class="steps-table-wrapper">
            <el-table :data="form.stepList" border style="width: 100%">
              <el-table-column label="序号" width="60" align="center">
                <template #default="{ $index }">
                  <span>{{ $index + 1 }}</span>
                </template>
              </el-table-column>
              <el-table-column label="步骤描述" min-width="200">
                <template #default="{ row }">
                  <el-input
                    v-model="row.step"
                    type="textarea"
                    :rows="2"
                    placeholder="请输入步骤描述"
                    @blur="handleStepChange"
                  />
                </template>
              </el-table-column>
              <el-table-column label="期望结果" min-width="200">
                <template #default="{ row }">
                  <el-input
                    v-model="row.expected"
                    type="textarea"
                    :rows="2"
                    placeholder="请输入期望结果"
                    @blur="handleStepChange"
                  />
                </template>
              </el-table-column>
              <el-table-column label="操作" width="80" align="center">
                <template #default="{ $index }">
                  <el-button
                    type="danger"
                    link
                    :icon="Delete"
                    @click="removeStep($index)"
                    :disabled="form.stepList.length <= 1"
                  >
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            <el-button
              type="primary"
              :icon="Plus"
              @click="addStep"
              style="margin-top: 10px"
            >
              添加步骤
            </el-button>
          </div>
        </el-form-item>

        <el-form-item label="后置条件" prop="postconditions">
          <el-input v-model="form.postconditions" type="textarea" :rows="2" placeholder="测试执行后的清理或恢复操作..." />
        </el-form-item>

        <el-form-item label="备注" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="其他说明..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 查看用例对话框 -->
    <el-dialog
      v-model="viewDialogVisible"
      title="查看用例"
      width="900px"
      destroy-on-close
    >
      <div v-if="viewCase" class="case-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="用例编号">{{ viewCase.case_no || `CASE-${viewCase.id}` }}</el-descriptions-item>
          <el-descriptions-item label="用例名称">{{ viewCase.name }}</el-descriptions-item>
          <el-descriptions-item label="优先级">
            <el-tag :type="getPriorityType(viewCase.priority)">{{ viewCase.priority }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="用例类型">
            <el-tag type="info">{{ viewCase.case_type }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="自动化状态">
            <el-tag :type="viewCase.automation_status === 'automated' ? 'success' : 'info'">
              {{ viewCase.automation_status }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(viewCase.status)">{{ viewCase.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间" :span="2">
            {{ viewCase.created_at ? new Date(viewCase.created_at).toLocaleString() : '-' }}
          </el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left">前置条件</el-divider>
        <div class="detail-content">
          {{ viewCase.preconditions || '无' }}
        </div>

        <el-divider content-position="left">测试步骤</el-divider>
        <el-table :data="getStepList(viewCase.steps)" border style="width: 100%">
          <el-table-column label="序号" width="60" align="center">
            <template #default="{ $index }">
              <span>{{ $index + 1 }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="step" label="步骤描述" />
          <el-table-column prop="expected" label="期望结果" />
        </el-table>

        <el-divider content-position="left">后置条件</el-divider>
        <div class="detail-content">
          {{ viewCase.postconditions || '无' }}
        </div>

        <el-divider content-position="left">备注</el-divider>
        <div class="detail-content">
          {{ viewCase.description || '无' }}
        </div>
      </div>
      <template #footer>
        <el-button type="primary" @click="viewDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 执行用例对话框 -->
    <el-dialog
      v-model="executeDialogVisible"
      title="执行用例"
      width="900px"
      destroy-on-close
    >
      <div v-if="executeCase" class="case-execute">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="用例编号">{{ executeCase.case_no || `CASE-${executeCase.id}` }}</el-descriptions-item>
          <el-descriptions-item label="用例名称">{{ executeCase.name }}</el-descriptions-item>
          <el-descriptions-item label="优先级">
            <el-tag :type="getPriorityType(executeCase.priority)">{{ executeCase.priority }}</el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left">前置条件</el-divider>
        <div class="detail-content">
          {{ executeCase.preconditions || '无' }}
        </div>

        <el-divider content-position="left">测试步骤</el-divider>
        <el-table :data="getStepList(executeCase.steps)" border style="width: 100%">
          <el-table-column label="序号" width="60" align="center">
            <template #default="{ $index }">
              <span>{{ $index + 1 }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="step" label="步骤描述" />
          <el-table-column prop="expected" label="期望结果" />
        </el-table>

        <el-divider content-position="left">执行结果</el-divider>
        <el-form :model="executeForm" label-width="100px">
          <el-form-item label="执行状态" prop="status" required>
            <el-radio-group v-model="executeForm.status">
              <el-radio label="passed">通过</el-radio>
              <el-radio label="failed">失败</el-radio>
              <el-radio label="blocked">阻塞</el-radio>
              <el-radio label="skipped">跳过</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="实际结果">
            <el-input
              v-model="executeForm.actual_result"
              type="textarea"
              :rows="4"
              placeholder="请输入实际执行结果..."
            />
          </el-form-item>

          <el-form-item label="备注">
            <el-input
              v-model="executeForm.notes"
              type="textarea"
              :rows="3"
              placeholder="其他备注信息..."
            />
          </el-form-item>

          <el-form-item label="执行时长(秒)">
            <el-input-number
              v-model="executeForm.duration"
              :min="0"
              :max="99999"
              placeholder="执行时长"
            />
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
      </div>
      <template #footer>
        <el-button @click="executeDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="executing" @click="handleSubmitExecution">提交执行结果</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Delete, Search, Folder
} from '@element-plus/icons-vue'
import { useTestCaseStore } from '@/store/test-case'
import { useProjectStore } from '@/store/project'
import { defectApi } from '@/api/defect'

const router = useRouter()

const testCaseStore = useTestCaseStore()
const projectStore = useProjectStore()
const treeRef = ref()
const formRef = ref()

// 当前项目ID
const currentProjectId = computed(() => projectStore.currentProject?.id)

const filterText = ref('')
const suiteTree = ref([])
const caseList = ref([])
const selectedCases = ref([])

const dialogVisible = ref(false)
const dialogTitle = ref('')
const isEdit = ref(false)

// 查看和执行相关
const viewDialogVisible = ref(false)
const viewCase = ref(null)
const executeDialogVisible = ref(false)
const executeCase = ref(null)
const executing = ref(false)

const executeForm = reactive({
  status: 'passed',
  actual_result: '',
  notes: '',
  duration: 0,
  defect_ids: []
})

// 缺陷列表
const defectList = ref([])

const searchForm = reactive({
  keyword: '',
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
  name: '',
  case_no: '',
  suite_id: null,
  preconditions: '',
  postconditions: '',
  stepList: [{ step: '', expected: '' }],
  steps: '',
  expected_result: '',
  description: '',
  priority: 'medium',
  case_type: 'functional',
  automation_status: 'manual',
  status: 'draft'
})

const rules = {
  name: [{ required: true, message: '请输入用例名称', trigger: 'blur' }]
}

const suiteOptions = ref([])

watch(filterText, (val) => {
  treeRef.value?.filter(val)
})

function filterNode(value, data) {
  if (!value) return true
  return data.name.includes(value)
}

function getPriorityType(priority) {
  const map = { critical: 'danger', high: 'warning', medium: 'primary', low: 'info' }
  return map[priority] || 'info'
}

function getStatusType(status) {
  const map = { draft: 'info', active: 'success', archived: 'warning' }
  return map[status] || 'info'
}

async function loadSuites() {
  const res = await testCaseStore.fetchSuites({
    project_id: currentProjectId.value
  })
  suiteTree.value = res.data || []
  suiteOptions.value = buildOptions(suiteTree.value)
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

function handleNodeClick(data) {
  testCaseStore.setCurrentSuite(data)
  loadCases()
}

async function loadCases() {
  const res = await testCaseStore.fetchCases({
    page: pagination.page,
    per_page: pagination.pageSize,
    suite_id: testCaseStore.currentSuite?.id,
    project_id: currentProjectId.value,
    ...searchForm
  })
  caseList.value = res.data?.items || []
  pagination.total = res.data?.total || 0
}

function handleSelectionChange(selection) {
  selectedCases.value = selection.map(item => item.id)
}

function handleCreateSuite() {
  ElMessageBox.prompt('请输入文件夹名称', '新建文件夹', {
    confirmButtonText: '确定',
    cancelButtonText: '取消'
  }).then(({ value }) => {
    testCaseStore.createSuite({
      name: value,
      parent_id: testCaseStore.currentSuite?.id,
      project_id: currentProjectId.value
    }).then(() => {
      ElMessage.success('创建成功')
      loadSuites()
    })
  })
}

function handleCreateCase() {
  isEdit.value = false
  dialogTitle.value = '新建测试用例'
  Object.assign(form, {
    id: null,
    name: '',
    case_no: '',
    suite_id: testCaseStore.currentSuite?.id,
    preconditions: '',
    postconditions: '',
    stepList: [{ step: '', expected: '' }],
    steps: '',
    expected_result: '',
    description: '',
    priority: 'medium',
    case_type: 'functional',
    automation_status: 'manual',
    status: 'draft'
  })
  dialogVisible.value = true
}

function handleEdit(row) {
  isEdit.value = true
  dialogTitle.value = '编辑测试用例'

  // 解析steps数据
  let stepList = [{ step: '', expected: '' }]
  if (row.steps) {
    try {
      const parsed = JSON.parse(row.steps)
      if (Array.isArray(parsed)) {
        stepList = parsed.map(item => ({
          step: item.step || '',
          expected: item.expected || ''
        }))
      }
    } catch {
      stepList = [{ step: row.steps || '', expected: row.expected_result || '' }]
    }
  }

  Object.assign(form, {
    id: row.id,
    name: row.name,
    case_no: row.case_no,
    suite_id: row.suite_id,
    preconditions: row.preconditions || '',
    postconditions: row.postconditions || '',
    stepList: stepList,
    steps: row.steps,
    expected_result: row.expected_result || '',
    description: row.description || '',
    priority: row.priority,
    case_type: row.case_type,
    automation_status: row.automation_status,
    status: row.status
  })
  dialogVisible.value = true
}

function handleDelete(row) {
  ElMessageBox.confirm('确定要删除这条用例吗？', '提示', {
    type: 'warning'
  }).then(() => {
    testCaseStore.deleteCase(row.id).then(() => {
      ElMessage.success('删除成功')
      loadCases()
    })
  })
}

function handleBatchDelete() {
  ElMessageBox.confirm(`确定要删除选中的 ${selectedCases.value.length} 条用例吗？`, '提示', {
    type: 'warning'
  }).then(() => {
    testCaseStore.batchDeleteCases(selectedCases.value).then(() => {
      ElMessage.success('删除成功')
      loadCases()
    })
  })
}

function handleBatchMove() {
  ElMessageBox.prompt('请输入目标文件夹ID', '批量移动', {
    confirmButtonText: '确定',
    cancelButtonText: '取消'
  }).then(({ value }) => {
    testCaseStore.batchMoveCases(selectedCases.value, parseInt(value)).then(() => {
      ElMessage.success('移动成功')
      loadCases()
    })
  })
}

function addStep() {
  form.stepList.push({ step: '', expected: '' })
}

function removeStep(index) {
  if (form.stepList.length > 1) {
    form.stepList.splice(index, 1)
  }
}

function handleStepChange() {
  // 将步骤列表转换为JSON格式
  const validSteps = form.stepList.filter(s => s.step || s.expected)
  form.steps = JSON.stringify(validSteps)
  // 兼容旧字段
  form.expected_result = validSteps.map(s => s.expected).filter(Boolean).join('\n')
}

function handleSubmit() {
  formRef.value.validate((valid) => {
    if (valid) {
      // 提交前处理步骤数据
      handleStepChange()

      const submitData = { ...form }
      delete submitData.stepList

      const api = isEdit.value ? testCaseStore.updateCase : testCaseStore.createCase
      const params = isEdit.value ? form.id : submitData
      api(params, isEdit.value ? submitData : null).then(() => {
        ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
        dialogVisible.value = false
        loadCases()
        loadSuites()
      })
    }
  })
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

// 查看用例
function handleView(row) {
  viewCase.value = row
  viewDialogVisible.value = true
}

// 执行用例
function handleExecute(row) {
  executeCase.value = row
  // 重置执行表单
  Object.assign(executeForm, {
    status: 'passed',
    actual_result: '',
    notes: '',
    duration: 0,
    defect_ids: []
  })
  // 加载缺陷列表
  loadDefects()
  executeDialogVisible.value = true
}

// AI执行用例
function handleAIExecute(row) {
  router.push({
    path: '/test-cases/ai-execution',
    query: {
      caseIds: row.id,
      environmentId: null
    }
  })
}

// 加载缺陷列表
async function loadDefects() {
  try {
    const res = await defectApi.getList({
      project_id: currentProjectId.value,
      per_page: 100
    })
    defectList.value = res.data?.items || []
  } catch (error) {
    console.error('加载缺陷列表失败:', error)
  }
}

// 创建缺陷
function handleCreateDefect() {
  router.push({
    path: '/defects',
    query: {
      action: 'create',
      test_case_id: executeCase.value?.id,
      test_result: executeForm.status === 'failed' ? executeForm.actual_result : ''
    }
  })
}

// 提交执行结果
async function handleSubmitExecution() {
  if (!executeForm.status) {
    ElMessage.warning('请选择执行状态')
    return
  }

  executing.value = true
  try {
    // 这里需要调用执行API，暂时使用模拟数据
    // TODO: 集成到测试计划执行API
    ElMessage.success('执行结果提交成功')
    executeDialogVisible.value = false

    // 可以在这里刷新数据或跳转到执行记录
  } catch (error) {
    ElMessage.error('提交失败')
  } finally {
    executing.value = false
  }
}

onMounted(() => {
  if (currentProjectId.value) {
    loadSuites()
    loadCases()
  }
})

// 监听项目变化，重新加载数据
watch(currentProjectId, (newVal, oldVal) => {
  if (newVal && newVal !== oldVal) {
    // 清空当前选择
    testCaseStore.setCurrentSuite(null)
    // 重新加载数据
    loadSuites()
    loadCases()
  }
})
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.suite-tree {
  border-right: 1px solid #e4e7ed;
  padding-right: 16px;
  overflow: auto;
}

.case-list {
  padding: 0;
}

.toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 4px;
  flex: 1;
}

.node-count {
  margin-left: auto;
  color: #909399;
  font-size: 12px;
}

.steps-table-wrapper {
  width: 100%;
}

.steps-table-wrapper :deep(.el-textarea__inner) {
  resize: none;
}

.detail-content {
  padding: 12px;
  background-color: #f5f7fa;
  border-radius: 4px;
  min-height: 40px;
  white-space: pre-wrap;
  word-break: break-word;
}

.case-detail .el-divider {
  margin: 20px 0;
}

.case-execute .el-divider {
  margin: 20px 0;
}
</style>

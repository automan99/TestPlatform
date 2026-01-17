<template>
  <div class="ai-execution-page">
    <!-- 顶部导航栏 -->
    <div class="top-header">
      <div class="header-left">
        <el-button :icon="ArrowLeft" text @click="handleBack">返回</el-button>
        <el-divider direction="vertical" />
        <span class="case-title">{{ pageTitle }}</span>
      </div>
      <div class="header-right">
        <span class="host-info">执行主机: localhost</span>
        <el-link type="primary" underline="never" @click="showLogsDialog = true">
          <el-icon><Document /></el-icon>
          查看执行日志
        </el-link>
      </div>
    </div>

    <!-- 三栏布局 -->
    <div class="three-column-layout">
      <!-- 左侧：用例执行步骤 -->
      <div class="left-panel">
        <div class="panel-header">
          <span class="panel-title">用例执行</span>
          <el-button type="primary" size="small" @click="handleExecuteAll">
            执行
          </el-button>
        </div>

        <div class="steps-container">
          <!-- 步骤组 -->
          <div v-for="group in stepGroups" :key="group.id" class="step-group">
            <div class="group-header" @click="toggleGroup(group.id)">
              <el-icon class="arrow-icon" :class="{ expanded: group.expanded }">
                <ArrowRight />
              </el-icon>
              <span class="group-name">{{ group.name }}</span>
              <el-icon v-if="group.status === 'success'" color="#67c23a" class="status-icon">
                <CircleCheck />
              </el-icon>
              <el-icon v-else-if="group.status === 'failed'" color="#f56c6c" class="status-icon">
                <CircleClose />
              </el-icon>
              <el-icon v-else-if="group.status === 'running'" color="#409eff" class="status-icon">
                <Loading />
              </el-icon>
            </div>

            <div v-show="group.expanded" class="group-steps">
              <div
                v-for="step in group.steps"
                :key="step.id"
                class="step-item"
                :class="{ active: activeStepId === step.id }"
                @click="selectStep(step)"
              >
                <div class="step-left">
                  <el-icon v-if="step.status === 'success'" color="#67c23a" :size="16">
                    <CircleCheck />
                  </el-icon>
                  <el-icon v-else-if="step.status === 'failed'" color="#f56c6c" :size="16">
                    <CircleClose />
                  </el-icon>
                  <el-icon v-else-if="step.status === 'running'" color="#409eff" :size="16">
                    <Loading />
                  </el-icon>
                  <span v-else class="step-index">{{ step.index }}</span>
                  <span class="step-desc">{{ step.description }}</span>
                </div>
                <el-button
                  v-if="step.status !== 'running'"
                  :icon="VideoPlay"
                  size="small"
                  text
                  @click.stop="executeStep(step)"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- 底部操作按钮 -->
        <div class="action-buttons">
          <el-button :icon="Refresh" @click="handleReExecute">重新执行</el-button>
          <el-button :icon="Edit" @click="handleModifyCase">修改用例</el-button>
          <el-button :icon="Delete" @click="handleClearCache">清除缓存</el-button>
        </div>
      </div>

      <!-- 中间：执行结果展示 -->
      <div class="center-panel">
        <el-tabs v-model="activeTab" class="result-tabs">
          <el-tab-pane label="屏幕截图" name="screenshot">
            <div class="screenshot-viewer">
              <div class="screenshot-nav">
                <el-button :icon="ArrowLeft" size="small" @click="prevScreenshot" />
                <span class="nav-title">{{ currentScreenshot?.title || '无' }}</span>
                <el-button :icon="ArrowRight" size="small" @click="nextScreenshot" />
              </div>
              <div class="screenshot-content">
                <div v-if="currentScreenshot?.before" class="screenshot-box">
                  <div class="screenshot-label">执行前</div>
                  <img :src="currentScreenshot.before" alt="执行前截图" />
                </div>
                <div v-if="currentScreenshot?.after" class="screenshot-box">
                  <div class="screenshot-label">执行后</div>
                  <img :src="currentScreenshot.after" alt="执行后截图" />
                </div>
                <el-empty v-if="!currentScreenshot" description="暂无截图" />
              </div>
            </div>
          </el-tab-pane>

          <el-tab-pane label="DOM快照" name="dom">
            <div class="dom-viewer">
              <pre class="dom-content">{{ domSnapshot || '暂无DOM快照数据' }}</pre>
            </div>
          </el-tab-pane>

          <el-tab-pane label="测试用例" name="testcase">
            <div class="testcase-view">
              <div class="info-row">
                <span class="label">用例名称:</span>
                <span class="value">{{ caseInfo.name || '-' }}</span>
              </div>
              <div class="info-row">
                <span class="label">用例编号:</span>
                <span class="value">{{ caseInfo.caseNo || '-' }}</span>
              </div>
              <div class="info-row">
                <span class="label">前置条件:</span>
                <span class="value">{{ caseInfo.preconditions || '-' }}</span>
              </div>
              <div class="info-row">
                <span class="label">测试步骤:</span>
                <div class="steps-display">
                  <div v-for="(step, idx) in caseSteps" :key="idx" class="step-row">
                    <span class="step-num">{{ idx + 1 }}.</span>
                    <span class="step-text">{{ step.step || step.description || '-' }}</span>
                    <span class="step-expected">期望: {{ step.expected || '-' }}</span>
                  </div>
                  <div v-if="!caseSteps || caseSteps.length === 0" class="step-row">
                    <span class="step-text">暂无步骤数据</span>
                  </div>
                </div>
              </div>
              <div class="info-row">
                <span class="label">预期结果:</span>
                <span class="value">{{ caseInfo.expectedResult || '-' }}</span>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>

      <!-- 右侧：任务信息 -->
      <div class="right-panel">
        <div class="panel-header">
          <span class="panel-title">任务信息</span>
        </div>

        <div class="task-info">
          <!-- 执行状态 -->
          <div class="info-section">
            <div class="section-title">执行状态</div>
            <el-tag :type="getStatusTagType(taskInfo.status)">
              {{ getStatusText(taskInfo.status) }}
            </el-tag>
          </div>

          <!-- 时间信息 -->
          <div class="info-section">
            <div class="section-title">时间信息</div>
            <div class="info-item">
              <span>开始时间:</span>
              <span>{{ taskInfo.startTime || '-' }}</span>
            </div>
            <div class="info-item">
              <span>结束时间:</span>
              <span>{{ taskInfo.endTime || '-' }}</span>
            </div>
            <div class="info-item">
              <span>执行耗时:</span>
              <span>{{ taskInfo.duration || '-' }}</span>
            </div>
          </div>

          <!-- 执行方式 -->
          <div class="info-section">
            <div class="section-title">执行方式</div>
            <div class="info-item">
              <span>执行模式:</span>
              <span>{{ taskInfo.mode || 'AI执行' }}</span>
            </div>
            <div class="info-item">
              <span>浏览器:</span>
              <span>{{ taskInfo.browser || 'Chrome' }}</span>
            </div>
          </div>

          <!-- 工具推理 -->
          <div class="info-section">
            <div class="section-title">工具推理</div>
            <div class="tool-list">
              <div v-for="(tool, idx) in toolReasoningList" :key="idx" class="tool-item">
                <div class="tool-header">
                  <el-icon><Tools /></el-icon>
                  <span class="tool-name">{{ tool.name }}</span>
                </div>
                <div class="tool-desc">{{ tool.description }}</div>
              </div>
              <el-empty v-if="toolReasoningList.length === 0" description="暂无工具推理信息" :image-size="60" />
            </div>
          </div>

          <!-- 工具参数 -->
          <div class="info-section">
            <div class="section-title">工具参数</div>
            <pre class="code-content">{{ toolParams || '暂无参数数据' }}</pre>
          </div>

          <!-- 返回结果 -->
          <div class="info-section">
            <div class="section-title">返回结果</div>
            <pre class="code-content">{{ toolResult || '暂无结果数据' }}</pre>
          </div>
        </div>
      </div>
    </div>

    <!-- 执行日志对话框 -->
    <el-dialog v-model="showLogsDialog" title="执行日志" width="800px">
      <div class="logs-container">
        <div v-for="(log, idx) in executionLogs" :key="idx" class="log-entry">
          <span class="log-time">{{ log.time }}</span>
          <span :class="['log-level', `log-${log.level}`]">{{ log.level }}</span>
          <span class="log-message">{{ log.message }}</span>
        </div>
        <el-empty v-if="executionLogs.length === 0" description="暂无日志" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft, ArrowRight, Document, VideoPlay, Refresh, Edit, Delete,
  CircleCheck, CircleClose, Loading, Tools
} from '@element-plus/icons-vue'
import { aiExecutionApi } from '@/api/ai-execution'

const router = useRouter()
const route = useRoute()

// 页面标题
const pageTitle = ref('AI用例执行')

// 活动标签
const activeTab = ref('screenshot')
const activeStepId = ref(null)

// 对话框显示状态
const showLogsDialog = ref(false)

// 截图相关
const currentScreenshotIndex = ref(0)

// 用例信息
const caseInfo = ref({
  name: '',
  caseNo: '',
  preconditions: '',
  expectedResult: ''
})
const caseSteps = ref([])

// 步骤组数据
const stepGroups = ref([
  {
    id: 'init',
    name: '初始化',
    expanded: true,
    status: 'pending',
    steps: [
      { id: 's1', index: 1, description: '打开浏览器', status: 'pending' },
      { id: 's2', index: 2, description: '导航到页面', status: 'pending' }
    ]
  },
  {
    id: 'action',
    name: '页面操作',
    expanded: true,
    status: 'pending',
    steps: [
      { id: 's3', index: 3, description: '填写表单', status: 'pending' },
      { id: 's4', index: 4, description: '点击提交', status: 'pending' }
    ]
  },
  {
    id: 'verify',
    name: '结果验证',
    expanded: false,
    status: 'pending',
    steps: [
      { id: 's5', index: 5, description: '验证成功提示', status: 'pending' },
      { id: 's6', index: 6, description: '检查数据保存', status: 'pending' }
    ]
  }
])

// 任务信息
const taskInfo = ref({
  status: 'pending',
  startTime: '',
  endTime: '',
  duration: '',
  mode: 'AI执行',
  browser: 'Chrome'
})

// 工具推理列表
const toolReasoningList = ref([])

// 工具参数
const toolParams = ref('')

// 返回结果
const toolResult = ref('')

// DOM快照
const domSnapshot = ref('')

// 截图列表
const screenshots = ref([])

// 执行日志
const executionLogs = ref([])

// 当前选中的步骤信息
const selectedStepInfo = ref(null)

// 轮询定时器
let pollTimer = null

// 计算属性：当前截图
const currentScreenshot = computed(() => screenshots.value[currentScreenshotIndex.value])

// 获取状态标签类型
function getStatusTagType(status) {
  const map = {
    pending: 'info',
    running: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return map[status] || 'info'
}

// 获取状态文本
function getStatusText(status) {
  const map = {
    pending: '待执行',
    running: '执行中',
    completed: '已完成',
    failed: '失败'
  }
  return map[status] || status
}

// 切换步骤组展开状态
function toggleGroup(groupId) {
  const group = stepGroups.value.find(g => g.id === groupId)
  if (group) {
    group.expanded = !group.expanded
  }
}

// 选择步骤
function selectStep(step) {
  activeStepId.value = step.id
  selectedStepInfo.value = step
  updateTaskInfo(step)
}

// 更新右侧任务信息
function updateTaskInfo(step) {
  toolReasoningList.value = [
    {
      name: 'find_element',
      description: `查找页面元素: ${step.description}`
    }
  ]
  toolParams.value = JSON.stringify({
    selector: 'button[type="submit"]',
    timeout: 5000,
    wait: true
  }, null, 2)
  toolResult.value = JSON.stringify({
    success: true,
    element: '<button class="submit-btn">提交</button>',
    position: { x: 100, y: 200 },
    visible: true
  }, null, 2)
}

// 执行单个步骤
function executeStep(step) {
  step.status = 'running'
  ElMessage.info(`执行步骤: ${step.description}`)

  // 模拟执行完成
  setTimeout(() => {
    step.status = 'success'
    updateTaskInfo(step)
  }, 1000)
}

// 执行所有步骤
function handleExecuteAll() {
  taskInfo.value.status = 'running'
  taskInfo.value.startTime = new Date().toLocaleString()
  ElMessage.success('开始执行所有步骤')
}

// 重新执行
function handleReExecute() {
  ElMessageBox.confirm('确定要重新执行吗？', '提示', { type: 'warning' })
    .then(() => {
      resetSteps()
      handleExecuteAll()
    })
    .catch(() => {})
}

// 重置步骤状态
function resetSteps() {
  stepGroups.value.forEach(group => {
    group.status = 'pending'
    group.steps.forEach(step => {
      step.status = 'pending'
    })
  })
  taskInfo.value = {
    status: 'pending',
    startTime: '',
    endTime: '',
    duration: '',
    mode: 'AI执行',
    browser: 'Chrome'
  }
}

// 修改用例
function handleModifyCase() {
  router.push('/test-cases')
}

// 清除缓存
function handleClearCache() {
  ElMessageBox.confirm('确定要清除缓存吗？', '提示', { type: 'warning' })
    .then(() => {
      screenshots.value = []
      domSnapshot.value = ''
      toolParams.value = ''
      toolResult.value = ''
      executionLogs.value = []
      ElMessage.success('缓存已清除')
    })
    .catch(() => {})
}

// 返回
function handleBack() {
  stopPolling()
  router.back()
}

// 上一个截图
function prevScreenshot() {
  if (currentScreenshotIndex.value > 0) {
    currentScreenshotIndex.value--
  }
}

// 下一个截图
function nextScreenshot() {
  if (currentScreenshotIndex.value < screenshots.value.length - 1) {
    currentScreenshotIndex.value++
  }
}

// 轮询状态
async function pollStatus() {
  try {
    const executionId = route.query.executionId
    if (!executionId) return

    const res = await aiExecutionApi.getStatus(executionId)
    const data = res.data

    taskInfo.value.status = data.status

    if (data.logs) {
      executionLogs.value = data.logs
    }

    if (data.status === 'completed' || data.status === 'failed') {
      stopPolling()
      taskInfo.value.endTime = new Date().toLocaleString()
      if (taskInfo.value.startTime) {
        const start = new Date(taskInfo.value.startTime)
        const end = new Date(taskInfo.value.endTime)
        taskInfo.value.duration = `${Math.round((end - start) / 1000)}秒`
      }
    }
  } catch (error) {
    console.error('轮询状态失败:', error)
  }
}

// 开始轮询
function startPolling() {
  stopPolling()
  pollTimer = setInterval(pollStatus, 2000)
}

// 停止轮询
function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

// 组件挂载
onMounted(() => {
  // 如果有执行ID，开始轮询
  if (route.query.executionId) {
    startPolling()
  }
})

// 组件卸载
onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped>
.ai-execution-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  background: #f5f7fa;
  height: 100%;
  overflow: hidden;
}

/* 顶部导航栏 */
.top-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #fff;
  border-radius: 4px;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.case-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.host-info {
  font-size: 14px;
  color: #909399;
}

/* 三栏布局 */
.three-column-layout {
  display: flex;
  gap: 16px;
  flex: 1;
  overflow: hidden;
}

/* 左侧面板 */
.left-panel {
  width: 25%;
  min-width: 250px;
  background: #fff;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #e4e7ed;
  flex-shrink: 0;
}

.panel-title {
  font-size: 15px;
  font-weight: 500;
  color: #303133;
}

.steps-container {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}

.step-group {
  margin-bottom: 8px;
}

.group-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  cursor: pointer;
  user-select: none;
  transition: background 0.2s;
}

.group-header:hover {
  background: #f5f7fa;
}

.arrow-icon {
  transition: transform 0.2s;
  font-size: 14px;
  color: #909399;
  flex-shrink: 0;
}

.arrow-icon.expanded {
  transform: rotate(90deg);
}

.group-name {
  flex: 1;
  font-size: 14px;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.status-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.group-steps {
  padding-left: 28px;
}

.step-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  margin: 4px 0;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
}

.step-item:hover {
  background: #f5f7fa;
}

.step-item.active {
  background: #ecf5ff;
}

.step-left {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.step-index {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #e4e7ed;
  color: #909399;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.step-desc {
  font-size: 14px;
  color: #606266;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.action-buttons {
  display: flex;
  border-top: 1px solid #e4e7ed;
  padding: 12px;
  gap: 8px;
  flex-shrink: 0;
}

.action-buttons .el-button {
  flex: 1;
  font-size: 14px;
}

/* 中间面板 */
.center-panel {
  flex: 1;
  background: #fff;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
}

.result-tabs {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.result-tabs :deep(.el-tabs__content) {
  flex: 1;
  overflow: hidden;
}

.result-tabs :deep(.el-tab-pane) {
  height: 100%;
  overflow: hidden;
}

/* 截图查看器 */
.screenshot-viewer {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.screenshot-nav {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  padding: 12px 16px;
  border-bottom: 1px solid #e4e7ed;
  flex-shrink: 0;
}

.nav-title {
  font-size: 15px;
  color: #303133;
}

.screenshot-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.screenshot-box {
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
}

.screenshot-label {
  padding: 8px 12px;
  background: #f5f7fa;
  font-size: 14px;
  color: #606266;
  border-bottom: 1px solid #e4e7ed;
}

.screenshot-box img {
  width: 100%;
  height: auto;
  display: block;
}

/* DOM查看器 */
.dom-viewer {
  height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.dom-content {
  margin: 0;
  flex: 1;
  overflow: auto;
  background: #f5f7fa;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
  color: #303133;
}

/* 测试用例视图 */
.testcase-view {
  height: 100%;
  overflow-y: auto;
  padding: 16px;
}

.info-row {
  margin-bottom: 16px;
}

.info-row > .label {
  display: block;
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.info-row > .value {
  display: block;
  font-size: 15px;
  color: #303133;
}

.steps-display {
  background: #f5f7fa;
  border-radius: 4px;
  padding: 12px;
}

.step-row {
  padding: 8px 0;
  border-bottom: 1px solid #e4e7ed;
  font-size: 14px;
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.step-row:last-child {
  border-bottom: none;
}

.step-num {
  color: #409eff;
  font-weight: 500;
  flex-shrink: 0;
}

.step-text {
  color: #303133;
  flex: 1;
  word-break: break-word;
}

.step-expected {
  color: #909399;
  font-size: 13px;
  flex-shrink: 0;
}

/* 右侧面板 */
.right-panel {
  width: 25%;
  min-width: 250px;
  background: #fff;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.task-info {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.info-section {
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.info-section:last-child {
  border-bottom: none;
}

.section-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 12px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  font-size: 14px;
  word-break: break-word;
}

.info-item span:first-child {
  color: #909399;
  flex-shrink: 0;
}

.info-item span:last-child {
  color: #303133;
  text-align: right;
  margin-left: 8px;
}

.tool-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.tool-item {
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
}

.tool-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.tool-name {
  font-size: 14px;
  font-weight: 500;
  color: #409eff;
  word-break: break-word;
}

.tool-desc {
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
  word-break: break-word;
}

.code-content {
  margin: 0;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.6;
  color: #303133;
  overflow-x: auto;
  word-break: break-all;
}

/* 日志对话框 */
.logs-container {
  max-height: 500px;
  overflow-y: auto;
  background: #f5f7fa;
  border-radius: 4px;
  padding: 12px;
}

.log-entry {
  display: flex;
  gap: 12px;
  padding: 8px 0;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  border-bottom: 1px solid #e4e7ed;
}

.log-entry:last-child {
  border-bottom: none;
}

.log-time {
  color: #909399;
  min-width: 120px;
  flex-shrink: 0;
}

.log-level {
  min-width: 50px;
  font-weight: 500;
  flex-shrink: 0;
}

.log-info {
  color: #409eff;
}

.log-warn {
  color: #e6a23c;
}

.log-error {
  color: #f56c6c;
}

.log-message {
  color: #303133;
  flex: 1;
  word-break: break-word;
}
</style>

<template>
  <div class="ai-execution-page">
    <!-- 三栏布局 -->
    <div class="three-column-layout" ref="layoutRef">
      <!-- 左侧：用例执行步骤 -->
      <div class="left-panel" :style="{ width: leftPanelWidth + 'px' }">
        <div class="panel-header">
          <span class="panel-title">AI执行步骤</span>
          <div class="env-selector">
            <el-select
              v-model="selectedEnvironmentId"
              placeholder="选择环境"
              size="small"
              @change="handleEnvironmentChange"
            >
              <el-option
                v-for="env in environmentList"
                :key="env.id"
                :label="env.name"
                :value="env.id"
              />
            </el-select>
          </div>
        </div>

        <div class="steps-toolbar">
          <div class="header-actions">
            <el-tooltip content="执行" placement="top">
              <el-button type="primary" :icon="VideoPlay" size="small" circle @click="handleExecuteAll" />
            </el-tooltip>
            <el-tooltip content="重新执行" placement="top">
              <el-button :icon="Refresh" size="small" circle @click="handleReExecute" />
            </el-tooltip>
            <el-tooltip content="修改用例" placement="top">
              <el-button :icon="Edit" size="small" circle @click="handleModifyCase" />
            </el-tooltip>
            <el-tooltip content="清除缓存" placement="top">
              <el-button :icon="Delete" size="small" circle @click="handleClearCache" />
            </el-tooltip>
            <el-tooltip content="查看执行日志" placement="top">
              <el-button :icon="Document" size="small" circle @click="showLogsDialog = true" />
            </el-tooltip>
          </div>
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


      </div>

      <!-- 左侧分隔条 -->
      <div
        class="resize-handle resize-handle-left"
        @mousedown="handleLeftMouseDown"
      ></div>

      <!-- 中间：执行结果展示 -->
      <div class="center-panel">
        <div class="center-tabs-wrapper">
          <el-tabs v-model="activeTab" class="result-tabs">
            <el-tab-pane label="屏幕截图" name="screenshot">
              <div class="screenshot-viewer">
                <div class="screenshot-content">
                  <el-empty v-if="!screenshots || screenshots.length === 0" description="暂无截图" />
                  <div v-else>
                    <!-- 当前截图显示 -->
                    <div class="screenshot-box">
                      <div v-if="currentScreenshot?.before" class="screenshot-item">
                        <div class="screenshot-label">执行前</div>
                        <img :src="currentScreenshot.before" alt="执行前截图" />
                      </div>
                      <div v-if="currentScreenshot?.after" class="screenshot-item">
                        <div class="screenshot-label">执行后</div>
                        <img :src="currentScreenshot.after" alt="执行后截图" />
                      </div>
                    </div>
                    <!-- 轮播指示器 -->
                    <div v-if="screenshots.length > 1" class="carousel-indicators">
                      <span
                        v-for="(screenshot, index) in screenshots"
                        :key="index"
                        :class="['indicator', { active: index === currentScreenshotIndex }]"
                        @click="currentScreenshotIndex = index"
                      ></span>
                    </div>
                  </div>
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
      </div>

      <!-- 中间分隔条 -->
      <div
        class="resize-handle resize-handle-right"
        @mousedown="handleRightMouseDown"
      ></div>

      <!-- 右侧：任务信息 -->
      <div class="right-panel" :class="{ collapsed: rightPanelCollapsed }" :style="{ width: rightPanelCollapsed ? '32px' : (rightPanelWidth + 'px') }">
        <div class="panel-header">
          <span class="panel-title" v-show="!rightPanelCollapsed">任务信息</span>
          <el-button
            type="primary"
            link
            size="small"
            @click="toggleRightPanel"
            class="collapse-btn"
          >
            <el-icon :class="{ 'is-collapsed': rightPanelCollapsed }">
              <ArrowLeft />
            </el-icon>
          </el-button>
        </div>

        <div class="task-info" v-show="!rightPanelCollapsed">
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
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft, ArrowRight, Document, VideoPlay, Refresh, Edit, Delete,
  CircleCheck, CircleClose, Loading, Tools
} from '@element-plus/icons-vue'
import { aiExecutionApi } from '@/api/ai-execution'
import { environmentApi } from '@/api/environment'

const router = useRouter()
const route = useRoute()
const layoutRef = ref()

// 环境相关
const environmentList = ref([])
const selectedEnvironmentId = ref(null)

// 面板宽度控制
const leftPanelWidth = ref(300)
const rightPanelWidth = ref(320)
const rightPanelCollapsed = ref(false)
const minWidth = 200
const maxWidth = 600

// 从 localStorage 恢复宽度
const savedLeftWidth = localStorage.getItem('ai-exec-left-panel-width')
const savedRightWidth = localStorage.getItem('ai-exec-right-panel-width')
const savedRightCollapsed = localStorage.getItem('ai-exec-right-panel-collapsed')
if (savedLeftWidth) leftPanelWidth.value = parseInt(savedLeftWidth)
if (savedRightWidth) rightPanelWidth.value = parseInt(savedRightWidth)
if (savedRightCollapsed) rightPanelCollapsed.value = savedRightCollapsed === 'true'

// 监听宽度变化并保存
watch(leftPanelWidth, (w) => localStorage.setItem('ai-exec-left-panel-width', w.toString()))
watch(rightPanelWidth, (w) => localStorage.setItem('ai-exec-right-panel-width', w.toString()))
watch(rightPanelCollapsed, (c) => localStorage.setItem('ai-exec-right-panel-collapsed', c.toString()))

// 切换右侧面板
function toggleRightPanel() {
  rightPanelCollapsed.value = !rightPanelCollapsed.value
}

// 左侧分隔条拖拽
function handleLeftMouseDown(e) {
  const startX = e.clientX
  const startWidth = leftPanelWidth.value

  function onMouseMove(e) {
    const delta = e.clientX - startX
    const newWidth = Math.max(minWidth, Math.min(maxWidth, startWidth + delta))
    leftPanelWidth.value = newWidth
  }

  function onMouseUp() {
    document.removeEventListener('mousemove', onMouseMove)
    document.removeEventListener('mouseup', onMouseUp)
    document.body.style.cursor = ''
  }

  document.addEventListener('mousemove', onMouseMove)
  document.addEventListener('mouseup', onMouseUp)
  document.body.style.cursor = 'col-resize'
}

// 右侧分隔条拖拽
function handleRightMouseDown(e) {
  if (rightPanelCollapsed.value) return

  const startX = e.clientX
  const startWidth = rightPanelWidth.value

  function onMouseMove(e) {
    const delta = startX - e.clientX
    const newWidth = Math.max(minWidth, Math.min(maxWidth, startWidth + delta))
    rightPanelWidth.value = newWidth
  }

  function onMouseUp() {
    document.removeEventListener('mousemove', onMouseMove)
    document.removeEventListener('mouseup', onMouseUp)
    document.body.style.cursor = ''
  }

  document.addEventListener('mousemove', onMouseMove)
  document.addEventListener('mouseup', onMouseUp)
  document.body.style.cursor = 'col-resize'
}

// 页面标题
const pageTitle = ref('AI用例执行')

// 活动标签
const activeTab = ref('screenshot')
const activeStepId = ref(null)
const activeStep = ref(null)

// 对话框显示状态
const showLogsDialog = ref(false)

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

// 当前截图索引
const currentScreenshotIndex = ref(0)

// 执行日志
const executionLogs = ref([])

// 当前选中的步骤信息
const selectedStepInfo = ref(null)

// 轮询定时器
let pollTimer = null

// 轮播定时器
let carouselTimer = null

// 计算属性：当前截图
const currentScreenshot = computed(() => screenshots.value[currentScreenshotIndex.value] || null)

// 启动截图轮播
function startCarousel() {
  stopCarousel()
  if (screenshots.value.length > 1) {
    carouselTimer = setInterval(() => {
      currentScreenshotIndex.value = (currentScreenshotIndex.value + 1) % screenshots.value.length
    }, 3000) // 每3秒切换一次
  }
}

// 停止截图轮播
function stopCarousel() {
  if (carouselTimer) {
    clearInterval(carouselTimer)
    carouselTimer = null
  }
}

// 监听截图列表变化，自动启动轮播
watch(screenshots, () => {
  currentScreenshotIndex.value = 0
  startCarousel()
})

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
  activeStep.value = step
  selectedStepInfo.value = step
  activeTab.value = 'testcase'
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
  // 加载环境列表
  loadEnvironments()
  // 如果有执行ID，开始轮询
  if (route.query.executionId) {
    startPolling()
  }
})

// 加载环境列表
async function loadEnvironments() {
  try {
    const res = await environmentApi.getList({
      per_page: 100
    })
    environmentList.value = res.data?.items || []
    // 如果URL中有environmentId，设置选中的环境
    if (route.query.environmentId) {
      selectedEnvironmentId.value = parseInt(route.query.environmentId)
    } else if (environmentList.value.length > 0) {
      // 默认选择第一个环境
      selectedEnvironmentId.value = environmentList.value[0].id
    }
  } catch (error) {
    console.error('加载环境列表失败:', error)
  }
}

// 切换环境
function handleEnvironmentChange(envId) {
  console.log('切换环境:', envId)
  // 这里可以添加切换环境后的逻辑
}

// 组件卸载
onUnmounted(() => {
  stopPolling()
  stopCarousel()
})
</script>

<style scoped>
.ai-execution-page {
  display: flex;
  flex-direction: column;
  gap: 5px;
  background: #f5f7fa;
  height: 100%;
  overflow: hidden;
}

/* 三栏布局 */
.three-column-layout {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* 分隔条 */
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

/* 左侧面板 */
.left-panel {
  flex-shrink: 0;
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

.collapse-btn {
  padding: 4px;
}

.collapse-btn .el-icon {
  transition: transform 0.3s;
}

.collapse-btn .el-icon.is-collapsed {
  transform: rotate(180deg);
}

.panel-title {
  font-size: 15px;
  font-weight: 500;
  color: #303133;
  flex-shrink: 0;
}

.env-selector {
  flex: 1;
  margin-left: 16px;
  max-width: 180px;
}

.header-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.host-info {
  font-size: 12px;
  color: #909399;
}

.steps-toolbar {
  display: flex;
  justify-content: center;
  gap: 8px;
  padding: 8px 16px;
  border-bottom: 1px solid #e4e7ed;
  flex-shrink: 0;
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

.center-tabs-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
}

.result-tabs {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.result-tabs :deep(.el-tabs__header) {
  margin: 0;
  border-bottom: none;
}

.result-tabs :deep(.el-tabs__nav-wrap) {
  padding: 0 16px;
}

.result-tabs :deep(.el-tabs__item) {
  padding: 0 16px;
  border: none;
}

.result-tabs :deep(.el-tabs__item.is-active) {
  color: #409eff;
}

.result-tabs :deep(.el-tabs__active-bar) {
  display: none;
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
  gap: 5px;
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
}

.screenshot-content > :not(:last-child) {
  border-bottom: 1px solid #e4e7ed;
  padding-bottom: 16px;
  margin-bottom: 16px;
}

.screenshot-box {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.screenshot-item {
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

.screenshot-item img {
  width: 100%;
  height: auto;
  display: block;
}

/* 轮播指示器 */
.carousel-indicators {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
}

.indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #d9d9d9;
  cursor: pointer;
  transition: all 0.3s;
}

.indicator.active {
  background: #409eff;
  transform: scale(1.2);
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
  flex-shrink: 0;
  background: #fff;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: width 0.3s ease;
}

.right-panel.collapsed .panel-header {
  padding: 12px 8px;
}

.right-panel.collapsed .collapse-btn {
  margin: 0 auto;
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
}

.tool-list > :not(:last-child) {
  border-bottom: 1px solid #e4e7ed;
  padding-bottom: 10px;
  margin-bottom: 10px;
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

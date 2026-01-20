<template>
  <div class="dashboard">
    <!-- 顶部欢迎区 -->
    <div class="welcome-section animate-fade-in-up">
      <div class="welcome-content">
        <h1 class="welcome-title">
          {{ greeting }}，{{ appStore.user?.username || '用户' }}
        </h1>
        <p class="welcome-subtitle">{{ projectStore.currentProject?.name || '未选择项目' }} · 概览</p>
      </div>
      <div class="welcome-actions">
        <el-button type="primary" @click="refreshData" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新数据
        </el-button>
      </div>
    </div>

    <!-- 统计卡片区域 -->
    <div class="stats-grid">
      <div
        v-for="(stat, index) in statCards"
        :key="stat.key"
        class="stat-card animate-fade-in-up"
        :class="`animate-delay-${index + 1}`"
        :style="{ '--accent-color': stat.color }"
        @click="handleStatClick(stat.key)"
      >
        <div class="stat-card-bg"></div>
        <div class="stat-card-content">
          <div class="stat-header">
            <div class="stat-icon" :style="{ background: stat.color }">
              <component :is="stat.icon" :size="20" />
            </div>
            <div class="stat-trend" :class="stat.trendClass">
              <el-icon><component :is="stat.trendIcon" /></el-icon>
              <span>{{ stat.trend }}</span>
            </div>
          </div>
          <div class="stat-value-section">
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
          <div class="stat-footer">
            <div class="stat-progress">
              <div class="stat-progress-bar" :style="{ width: stat.progress + '%', background: stat.color }"></div>
            </div>
            <span class="stat-hint">{{ stat.hint }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 图表和列表区域 -->
    <div class="content-grid">
      <!-- 测试趋势图表 -->
      <div class="chart-card animate-fade-in-up animate-delay-1">
        <div class="card-header">
          <h3 class="card-title">测试执行趋势</h3>
          <div class="card-actions">
            <el-radio-group v-model="trendPeriod" size="small">
              <el-radio-button value="week">本周</el-radio-button>
              <el-radio-button value="month">本月</el-radio-button>
              <el-radio-button value="quarter">季度</el-radio-button>
            </el-radio-group>
          </div>
        </div>
        <div class="chart-container" ref="trendChartRef"></div>
      </div>

      <!-- 用例执行分布 -->
      <div class="chart-card animate-fade-in-up animate-delay-2">
        <div class="card-header">
          <h3 class="card-title">用例执行分布</h3>
        </div>
        <div class="chart-container" ref="distributionChartRef"></div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, nextTick, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { projectApi } from '@/api/project'
import { useProjectStore } from '@/store/project'
import { useAppStore } from '@/store/index'
import * as echarts from 'echarts'
import {
  Document,
  CircleCheck,
  CircleClose,
  Calendar,
  Refresh,
  ArrowUp,
  ArrowDown,
  Minus
} from '@element-plus/icons-vue'

const router = useRouter()
const projectStore = useProjectStore()
const appStore = useAppStore()
const currentProjectId = computed(() => projectStore.currentProject?.id)

const loading = ref(false)
const trendPeriod = ref('week')
const trendChartRef = ref(null)
const distributionChartRef = ref(null)
let trendChart = null
let distributionChart = null

const stats = ref({
  totalCases: 0,
  passedCases: 0,
  defects: 0,
  runningPlans: 0,
  passRate: 0,
  totalPlans: 0
})

// 问候语
const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return '早上好'
  if (hour < 18) return '下午好'
  return '晚上好'
})

// 统计卡片配置
const statCards = computed(() => [
  {
    key: 'cases',
    label: '测试用例总数',
    value: stats.value.totalCases,
    color: 'var(--color-accent)',
    icon: Document,
    trend: '+12%',
    trendIcon: ArrowUp,
    trendClass: 'trend-up',
    progress: 75,
    hint: '较上月',
    route: '/test-cases'
  },
  {
    key: 'passed',
    label: '已通过用例',
    value: stats.value.passedCases,
    color: 'var(--color-success)',
    icon: CircleCheck,
    trend: '+8%',
    trendIcon: ArrowUp,
    trendClass: 'trend-up',
    progress: stats.value.passedCases > 0 ? Math.round((stats.value.passedCases / stats.value.totalCases) * 100) : 0,
    hint: `${stats.value.passedCases > 0 ? Math.round((stats.value.passedCases / stats.value.totalCases) * 100) : 0}% 通过率`,
    route: '/test-cases?status=passed'
  },
  {
    key: 'defects',
    label: '缺陷总数',
    value: stats.value.defects,
    color: 'var(--color-error)',
    icon: CircleClose,
    trend: '-5%',
    trendIcon: ArrowDown,
    trendClass: 'trend-down',
    progress: 30,
    hint: '较上月',
    route: '/defects'
  },
  {
    key: 'running',
    label: '执行中计划',
    value: stats.value.runningPlans,
    color: 'var(--color-warning)',
    icon: Calendar,
    trend: '0%',
    trendIcon: Minus,
    trendClass: 'trend-neutral',
    progress: 60,
    hint: `共 ${stats.value.totalPlans} 个计划`,
    route: '/test-plans?status=active'
  }
])

function handleStatClick(key) {
  const card = statCards.value.find(c => c.key === key)
  if (card?.route) {
    router.push(card.route)
  }
}

// 初始化趋势图表
function initTrendChart() {
  if (!trendChartRef.value) return

  if (trendChart) {
    trendChart.dispose()
  }

  trendChart = echarts.init(trendChartRef.value)

  const root = document.documentElement
  const computedStyle = getComputedStyle(root)
  const colorAccent = computedStyle.getPropertyValue('--color-accent').trim()
  const colorSuccess = computedStyle.getPropertyValue('--color-success').trim()
  const colorText = computedStyle.getPropertyValue('--color-text-muted').trim()

  const option = {
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '10%',
      containLabel: true
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'var(--color-surface)',
      borderColor: 'var(--color-border)',
      textStyle: { color: 'var(--color-text)' }
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
      axisLine: { lineStyle: { color: 'var(--color-border)' } },
      axisLabel: { color: colorText, fontSize: 11 }
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: colorText, fontSize: 11 },
      splitLine: { lineStyle: { color: 'var(--color-border-light)', type: 'dashed' } }
    },
    series: [
      {
        name: '执行用例',
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        data: [120, 132, 101, 134, 90, 230, 210],
        itemStyle: { color: colorAccent },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: colorAccent + '40' },
              { offset: 1, color: colorAccent + '05' }
            ]
          }
        }
      },
      {
        name: '通过用例',
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        data: [100, 110, 90, 120, 80, 200, 190],
        itemStyle: { color: colorSuccess },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: colorSuccess + '40' },
              { offset: 1, color: colorSuccess + '05' }
            ]
          }
        }
      }
    ]
  }

  trendChart.setOption(option)
}

// 初始化分布图表
function initDistributionChart() {
  if (!distributionChartRef.value) return

  if (distributionChart) {
    distributionChart.dispose()
  }

  distributionChart = echarts.init(distributionChartRef.value)

  const root = document.documentElement
  const computedStyle = getComputedStyle(root)
  const colorSuccess = computedStyle.getPropertyValue('--color-success').trim()
  const colorError = computedStyle.getPropertyValue('--color-error').trim()
  const colorWarning = computedStyle.getPropertyValue('--color-warning').trim()
  const colorInfo = computedStyle.getPropertyValue('--color-info').trim()
  const colorText = computedStyle.getPropertyValue('--color-text').trim()

  const option = {
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '5%',
      containLabel: true
    },
    tooltip: {
      trigger: 'item',
      backgroundColor: 'var(--color-surface)',
      borderColor: 'var(--color-border)',
      textStyle: { color: 'var(--color-text)' }
    },
    series: [
      {
        name: '执行状态',
        type: 'pie',
        radius: ['45%', '70%'],
        center: ['50%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 6,
          borderColor: 'var(--color-surface)',
          borderWidth: 2
        },
        label: {
          show: true,
          position: 'outside',
          formatter: '{b}: {c}',
          color: colorText,
          fontSize: 11
        },
        labelLine: {
          length: 10,
          length2: 10,
          show: true
        },
        data: [
          { value: stats.value.passedCases, name: '已通过', itemStyle: { color: colorSuccess } },
          { value: Math.floor(stats.value.totalCases * 0.15), name: '已失败', itemStyle: { color: colorError } },
          { value: Math.floor(stats.value.totalCases * 0.08), name: '阻塞', itemStyle: { color: colorWarning } },
          { value: Math.floor(stats.value.totalCases * 0.1), name: '未执行', itemStyle: { color: colorInfo } }
        ]
      }
    ]
  }

  distributionChart.setOption(option)
}

// 响应式图表
function handleResize() {
  trendChart?.resize()
  distributionChart?.resize()
}

// 加载统计数据
async function loadStats() {
  try {
    loading.value = true
    if (!currentProjectId.value) {
      console.log('未选择项目，跳过加载统计数据')
      return
    }

    // 尝试加载统计数据，如果失败则使用默认值
    let statistics = {}
    try {
      const statsRes = await projectApi.getStatistics(currentProjectId.value)
      statistics = statsRes.data?.data || {}
    } catch (statsError) {
      console.warn('统计数据API调用失败，使用默认值:', statsError)
    }

    stats.value = {
      totalCases: statistics.test_cases || 0,
      passedCases: statistics.passed_executions || 0,
      defects: statistics.defects || 0,
      runningPlans: statistics.test_plans || 0,
      passRate: statistics.test_cases > 0 ? Math.round((statistics.passed_executions / statistics.test_cases) * 100) : 0,
      totalPlans: statistics.test_plans || 0
    }

    await nextTick()
    initTrendChart()
    initDistributionChart()
  } catch (error) {
    console.error('加载统计数据失败:', error)
  } finally {
    loading.value = false
  }
}

async function refreshData() {
  await loadStats()
}

onMounted(async () => {
  window.addEventListener('resize', handleResize)
  if (currentProjectId.value) {
    await loadStats()
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  distributionChart?.dispose()
})

watch(currentProjectId, (newVal) => {
  if (newVal) {
    loadStats()
  }
})

watch(trendPeriod, () => {
  // 根据时间段更新图表数据
  initTrendChart()
})
</script>

<style scoped>
.dashboard {
  height: 100%;
  padding: var(--space-6);
  overflow-y: auto;
}

/* 欢迎区域 */
.welcome-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-6);
  padding: var(--space-6);
  background: var(--color-surface);
  border-radius: var(--radius-lg);
}

.welcome-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.welcome-title {
  font-size: var(--text-3xl);
  font-weight: 700;
  color: var(--color-text);
  margin: 0;
}

.welcome-subtitle {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  margin: 0;
}

.welcome-actions {
  display: flex;
  gap: var(--space-3);
}

/* 统计卡片网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

/* 统计卡片 */
.stat-card {
  position: relative;
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  cursor: pointer;
  overflow: hidden;
  transition: all var(--transition-base);
}

.stat-card:hover {
  transform: translateY(-4px);
}

.stat-card-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--accent-color);
  opacity: 0;
  transition: opacity var(--transition-base);
}

.stat-card:hover .stat-card-bg {
  opacity: 0.05;
}

.stat-card-content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  font-size: var(--text-xs);
  font-weight: 600;
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
}

.trend-up {
  color: var(--color-success);
  background: var(--color-success-light);
}

.trend-down {
  color: var(--color-error);
  background: var(--color-error-light);
}

.trend-neutral {
  color: var(--color-text-muted);
  background: var(--color-bg-alt);
}

.stat-value-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.stat-value {
  font-size: var(--text-4xl);
  font-weight: 700;
  color: var(--color-text);
  line-height: 1;
}

.stat-label {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
}

.stat-footer {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.stat-progress {
  height: 4px;
  background: var(--color-bg-alt);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.stat-progress-bar {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width var(--transition-slow);
}

.stat-hint {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

/* 内容网格 */
.content-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-4);
}

/* 图表卡片 */
.chart-card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
}

.card-title {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
}

.card-actions {
  display: flex;
  gap: var(--space-2);
}

.chart-container {
  height: 280px;
}

/* 响应式 */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .content-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .dashboard {
    padding: var(--space-4);
  }

  .welcome-section {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-4);
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>

<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #409eff">
              <el-icon :size="24"><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalCases }}</div>
              <div class="stat-label">测试用例</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #67c23a">
              <el-icon :size="24"><CircleCheck /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.passedCases }}</div>
              <div class="stat-label">已通过</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #f56c6c">
              <el-icon :size="24"><CircleClose /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.defects }}</div>
              <div class="stat-label">缺陷数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #e6a23c">
              <el-icon :size="24"><Calendar /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.runningPlans }}</div>
              <div class="stat-label">执行中</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>最近测试计划</span>
          </template>
          <el-table :data="recentPlans" style="width: 100%">
            <el-table-column prop="name" label="计划名称" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="progress" label="进度" width="120">
              <template #default="{ row }">
                <el-progress :percentage="row.progress" />
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>最近缺陷</span>
          </template>
          <el-table :data="recentDefects" style="width: 100%">
            <el-table-column prop="title" label="缺陷标题" />
            <el-table-column prop="severity" label="严重程度" width="100">
              <template #default="{ row }">
                <el-tag :type="getSeverityType(row.severity)">{{ row.severity }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag type="info">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { testPlanApi } from '@/api/test-plan'
import { defectApi } from '@/api/defect'
import { projectApi } from '@/api/project'
import { useProjectStore } from '@/store/project'

const projectStore = useProjectStore()
const currentProjectId = computed(() => projectStore.currentProject?.id)

const stats = ref({
  totalCases: 0,
  passedCases: 0,
  defects: 0,
  runningPlans: 0
})

const recentPlans = ref([])
const recentDefects = ref([])

function getStatusType(status) {
  const map = {
    draft: 'info',
    active: 'success',
    completed: 'success',
    cancelled: 'danger'
  }
  return map[status] || 'info'
}

function getSeverityType(severity) {
  const map = {
    critical: 'danger',
    high: 'warning',
    medium: 'primary',
    low: 'info',
    trivial: 'info'
  }
  return map[severity] || 'info'
}

// 加载统计数据
async function loadStats() {
  try {
    if (!currentProjectId.value) return

    // 并行加载统计数据
    const [plansRes, defectsRes, statsRes] = await Promise.all([
      testPlanApi.getList({
        project_id: currentProjectId.value,
        per_page: 100
      }),
      defectApi.getList({
        project_id: currentProjectId.value,
        per_page: 10
      }),
      projectApi.getStatistics(currentProjectId.value)
    ])

    // 计算统计数据
    const plans = plansRes.data?.items || []
    const defects = defectsRes.data?.items || []
    const statistics = statsRes.data?.data || {}

    stats.value = {
      totalCases: statistics.test_cases || 0,
      passedCases: statistics.passed_executions || 0,
      defects: defects.length,
      runningPlans: plans.filter(p => p.status === 'active').length
    }

    // 获取最近测试计划
    recentPlans.value = plans.slice(0, 5).map(p => ({
      name: p.name,
      status: p.status,
      progress: p.progress?.progress || 0
    }))

    // 获取最近缺陷
    recentDefects.value = defects.slice(0, 5).map(d => ({
      title: d.title,
      severity: d.severity,
      status: d.status
    }))
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

onMounted(() => {
  if (currentProjectId.value) {
    loadStats()
  }
})

// 监听项目变化
watch(currentProjectId, (newVal) => {
  if (newVal) {
    loadStats()
  }
})
</script>

<style scoped>
.dashboard {
  height: 100%;
}

.stat-card {
  cursor: pointer;
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}
</style>

<template>
  <div class="report-page">
    <div class="main-content animate-fade-in-up">
      <el-tabs v-model="activeTab" class="report-tabs">
      <el-tab-pane label="报告列表" name="list">
        <div class="toolbar">
          <el-input v-model="searchForm.keyword" placeholder="搜索报告..." clearable class="search-input" @change="loadReports">
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button :icon="Search" @click="showAdvancedSearch = true">高级搜索</el-button>
          <div style="flex: 1"></div>
          <el-button type="primary" :icon="Plus" @click="handleCreate">生成报告</el-button>
        </div>

        <div class="page-table">
          <el-table :data="reportList" class="page-table">
            <el-table-column prop="report_no" label="编号" width="120" show-overflow-tooltip />
            <el-table-column prop="name" label="报告名称" min-width="150" show-overflow-tooltip />
            <el-table-column prop="report_type" label="类型" width="100">
              <template #default="{ row }">
                <el-tag>{{ getReportTypeText(row.report_type) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="start_time" label="开始时间" width="160" show-overflow-tooltip />
            <el-table-column prop="end_time" label="结束时间" width="160" show-overflow-tooltip />
            <el-table-column prop="total_cases" label="用例数" width="100" show-overflow-tooltip />
            <el-table-column prop="pass_rate" label="通过率" width="120">
              <template #default="{ row }">
                <el-progress :percentage="row.pass_rate || 0" :color="getPassRateColor(row.pass_rate)" />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="140" fixed="right">
              <template #default="{ row }">
                <el-tooltip content="查看" placement="top">
                  <el-button type="primary" link size="small" @click="handleView(row)">
                    <el-icon><View /></el-icon>
                  </el-button>
                </el-tooltip>
                <el-tooltip content="导出" placement="top">
                  <el-button type="success" link size="small" @click="handleExport(row)">
                    <el-icon><Download /></el-icon>
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
        </div>

        <div class="table-pagination">
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.pageSize"
            :total="pagination.total"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @current-change="loadReports"
            @size-change="loadReports"
          />
        </div>
      </el-tab-pane>

      <el-tab-pane label="统计概览" name="statistics">
        <div class="charts-grid">
          <div class="chart-card">
            <div class="card-header">
              <h3 class="card-title">用例执行分布</h3>
            </div>
            <div class="chart-container">
              <div ref="pieChartRef"></div>
            </div>
          </div>
          <div class="chart-card">
            <div class="card-header">
              <h3 class="card-title">缺陷严重程度分布</h3>
            </div>
            <div class="chart-container">
              <div ref="barChartRef"></div>
            </div>
          </div>
        </div>
        <div class="chart-card chart-card-full">
          <div class="card-header">
            <h3 class="card-title">测试趋势</h3>
          </div>
          <div class="chart-container">
            <div ref="lineChartRef"></div>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="报告模板" name="templates">
        <div class="toolbar">
          <div style="flex: 1"></div>
          <el-button type="primary" :icon="Plus" @click="handleCreateTemplate">新建模板</el-button>
        </div>
        <div class="page-table">
          <el-table :data="templateList" class="page-table">
            <el-table-column prop="name" label="模板名称" min-width="150" show-overflow-tooltip />
            <el-table-column prop="report_type" label="类型" width="100">
              <template #default="{ row }">
                <el-tag>{{ getReportTypeText(row.report_type) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="180" show-overflow-tooltip />
            <el-table-column label="操作" width="100" fixed="right">
              <template #default="{ row }">
                <el-tooltip content="编辑" placement="top">
                  <el-button type="primary" link size="small" @click="handleEditTemplate(row)">
                    <el-icon><Edit /></el-icon>
                  </el-button>
                </el-tooltip>
                <el-tooltip content="删除" placement="top">
                  <el-button type="danger" link size="small" @click="handleDeleteTemplate(row)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </el-tooltip>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>
    </el-tabs>
    </div>

    <!-- 创建报告对话框 -->
    <el-dialog v-model="dialogVisible" title="生成测试报告" width="600px" destroy-on-close>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="报告名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="报告类型" prop="report_type">
          <el-select v-model="form.report_type" style="width: 100%">
            <el-option label="执行报告" value="execution" />
            <el-option label="汇总报告" value="summary" />
            <el-option label="趋势报告" value="trend" />
            <el-option label="覆盖率报告" value="coverage" />
          </el-select>
        </el-form-item>
        <el-form-item label="关联计划" prop="test_plan_id">
          <el-select v-model="form.test_plan_id" placeholder="选择测试计划" clearable style="width: 100%">
            <el-option v-for="plan in planList" :key="plan.id" :label="plan.name" :value="plan.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">生成</el-button>
      </template>
    </el-dialog>

    <!-- 报告详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="报告详情" width="900px" destroy-on-close>
      <div v-if="currentReport">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="报告名称">{{ currentReport.name }}</el-descriptions-item>
          <el-descriptions-item label="报告类型">{{ getReportTypeText(currentReport.report_type) }}</el-descriptions-item>
          <el-descriptions-item label="开始时间">{{ currentReport.start_time }}</el-descriptions-item>
          <el-descriptions-item label="结束时间">{{ currentReport.end_time }}</el-descriptions-item>
          <el-descriptions-item label="总用例数">{{ currentReport.total_cases }}</el-descriptions-item>
          <el-descriptions-item label="通过率">{{ currentReport.pass_rate }}%</el-descriptions-item>
        </el-descriptions>

        <el-divider />

        <el-row :gutter="20">
          <el-col :span="6">
            <el-statistic title="总数" :value="currentReport.total_cases" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="通过" :value="currentReport.passed_cases">
              <template #suffix><span style="color: var(--color-success)">▼</span></template>
            </el-statistic>
          </el-col>
          <el-col :span="6">
            <el-statistic title="失败" :value="currentReport.failed_cases">
              <template #suffix><span style="color: var(--color-error)">▼</span></template>
            </el-statistic>
          </el-col>
          <el-col :span="6">
            <el-statistic title="缺陷" :value="currentReport.total_defects">
              <template #suffix><span style="color: var(--color-warning)">▼</span></template>
            </el-statistic>
          </el-col>
        </el-row>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { View, Download, Edit, Delete, Plus, Search } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { reportApi } from '@/api/report'
import { testPlanApi } from '@/api/test-plan'

const activeTab = ref('list')
const reportList = ref([])
const templateList = ref([])
const planList = ref([])
const showAdvancedSearch = ref(false)

const dialogVisible = ref(false)
const detailDialogVisible = ref(false)
const currentReport = ref(null)
const formRef = ref()

const pieChartRef = ref()
const barChartRef = ref()
const lineChartRef = ref()

const searchForm = reactive({ keyword: '', report_type: '' })

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const form = reactive({
  name: '',
  report_type: 'execution',
  test_plan_id: null
})

const rules = {
  name: [{ required: true, message: '请输入报告名称', trigger: 'blur' }]
}

function getReportTypeText(type) {
  const map = { execution: '执行报告', summary: '汇总报告', trend: '趋势报告', coverage: '覆盖率报告' }
  return map[type] || type
}

function getPassRateColor(rate) {
  if (rate < 60) return 'var(--color-error)'
  if (rate < 80) return 'var(--color-warning)'
  return 'var(--color-success)'
}

async function loadReports() {
  const res = await reportApi.getList({
    page: pagination.page,
    per_page: pagination.pageSize,
    ...searchForm
  })
  reportList.value = res.data?.items || []
  pagination.total = res.data?.total || 0
}

async function loadTemplates() {
  const res = await reportApi.getTemplates()
  templateList.value = res.data || []
}

async function loadPlans() {
  const res = await testPlanApi.getList({ per_page: 100 })
  planList.value = res.data?.items || []
}

function handleCreate() {
  Object.assign(form, {
    name: '',
    report_type: 'execution',
    test_plan_id: null
  })
  dialogVisible.value = true
}

function handleCreateTemplate() {
  ElMessage.info('新建模板功能开发中...')
}

function handleEditTemplate(row) {
  ElMessage.info('编辑模板功能开发中...')
}

function handleDeleteTemplate(row) {
  ElMessage.info('删除模板功能开发中...')
}

function handleView(row) {
  currentReport.value = row
  detailDialogVisible.value = true
}

function handleExport(row) {
  reportApi.export(row.id, { format: 'html' }).then(() => {
    ElMessage.success('导出任务已提交')
  })
}

function handleDelete(row) {
  ElMessageBox.confirm('确定要删除这个报告吗？', '提示', { type: 'warning' })
    .then(() => reportApi.delete(row.id))
    .then(() => {
      ElMessage.success('删除成功')
      loadReports()
    })
}

function handleSubmit() {
  formRef.value.validate((valid) => {
    if (valid) {
      reportApi.create({ ...form, auto_generate: true }).then(() => {
        ElMessage.success('报告生成成功')
        dialogVisible.value = false
        loadReports()
      })
    }
  })
}

function initCharts() {
  // Get theme colors
  const root = document.documentElement
  const computedStyle = getComputedStyle(root)
  const colorSuccess = computedStyle.getPropertyValue('--color-success').trim() || '#67c23a'
  const colorError = computedStyle.getPropertyValue('--color-error').trim() || '#f56c6c'
  const colorWarning = computedStyle.getPropertyValue('--color-warning').trim() || '#e6a23c'
  const colorInfo = computedStyle.getPropertyValue('--color-info').trim() || '#909399'
  const colorAccent = computedStyle.getPropertyValue('--color-accent').trim() || '#409eff'

  // 饼图
  const pieChart = echarts.init(pieChartRef.value)
  pieChart.setOption({
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left' },
    series: [{
      type: 'pie',
      radius: ['45%', '70%'],
      data: [
        { value: 335, name: '通过', itemStyle: { color: colorSuccess } },
        { value: 234, name: '失败', itemStyle: { color: colorError } },
        { value: 135, name: '阻塞', itemStyle: { color: colorWarning } },
        { value: 48, name: '跳过', itemStyle: { color: colorInfo } }
      ],
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }]
  })

  // 柱状图
  const barChart = echarts.init(barChartRef.value)
  barChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: ['紧急', '高', '中', '低', '轻微'] },
    yAxis: { type: 'value' },
    series: [{
      data: [12, 23, 45, 67, 8],
      type: 'bar',
      itemStyle: { color: colorAccent }
    }]
  })

  // 折线图
  const lineChart = echarts.init(lineChartRef.value)
  lineChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'] },
    yAxis: { type: 'value' },
    series: [
      { name: '用例数', data: [120, 132, 101, 134, 90, 230, 210], type: 'line', smooth: true, itemStyle: { color: colorAccent } },
      { name: '通过率', data: [85, 88, 90, 87, 92, 95, 93], type: 'line', smooth: true, itemStyle: { color: colorSuccess } }
    ]
  })
}

onMounted(() => {
  loadReports()
  loadTemplates()
  loadPlans()
  nextTick(() => {
    initCharts()
  })
})
</script>

<style scoped>
.report-page {
  height: 100%;
  padding: var(--space-6);
  overflow-y: auto;
}

.main-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  overflow: hidden;
  padding: var(--space-5);
}

.report-page :deep(.el-card) {
  background: var(--color-surface);
  border: none;
  border-radius: var(--radius-lg);
  box-shadow: none;
}

.report-tabs :deep(.el-tabs__header) {
  margin: 0 0 var(--space-4) 0;
}

.report-tabs :deep(.el-tabs__content) {
  flex: 1;
  overflow-y: auto;
}

/* Charts grid */
.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-4);
  margin-bottom: var(--space-4);
}

/* Override toolbar padding for inside main-content */
.main-content .toolbar {
  padding: 0 0 var(--space-4) 0;
}

.main-content .page-table {
  padding: 0;
}

.main-content .table-pagination {
  padding: var(--space-4) 0 0 0;
}

.chart-card {
  background: var(--color-bg-alt);
  border-radius: var(--radius-md);
  padding: var(--space-4);
}

.chart-card-full {
  grid-column: 1 / -1;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
}

.card-title {
  font-size: var(--text-md);
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
}

.chart-container {
  height: 300px;
}

.chart-container > div {
  width: 100%;
  height: 100%;
}

/* Responsive */
@media (max-width: 1200px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .report-page {
    padding: var(--space-3);
  }

  .toolbar {
    flex-wrap: wrap;
  }
}
</style>

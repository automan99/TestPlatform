<template>
  <div class="report-page">
    <el-card>
      <template #header>
        <div class="page-header">
          <span>测试报告</span>
          <el-button type="primary" :icon="Plus" @click="handleCreate">生成报告</el-button>
        </div>
      </template>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="报告列表" name="list">
          <div class="toolbar">
            <el-input v-model="searchForm.keyword" placeholder="搜索报告" clearable style="width: 200px" @change="loadReports" />
            <el-select v-model="searchForm.report_type" placeholder="报告类型" clearable @change="loadReports">
              <el-option label="执行报告" value="execution" />
              <el-option label="汇总报告" value="summary" />
              <el-option label="趋势报告" value="trend" />
            </el-select>
            <div style="flex: 1"></div>
          </div>

          <el-table :data="reportList" style="width: 100%">
            <el-table-column prop="report_no" label="编号" width="120" />
            <el-table-column prop="name" label="报告名称" show-overflow-tooltip />
            <el-table-column prop="report_type" label="类型" width="120">
              <template #default="{ row }">
                <el-tag>{{ getReportTypeText(row.report_type) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="start_time" label="开始时间" width="160" />
            <el-table-column prop="end_time" label="结束时间" width="160" />
            <el-table-column prop="total_cases" label="用例数" width="100" />
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

          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.pageSize"
            :total="pagination.total"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @current-change="loadReports"
            @size-change="loadReports"
            style="margin-top: 20px; justify-content: flex-end"
          />
        </el-tab-pane>

        <el-tab-pane label="统计概览" name="statistics">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-card>
                <template #header>
                  <span>用例执行分布</span>
                </template>
                <div ref="pieChartRef" style="height: 300px"></div>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card>
                <template #header>
                  <span>缺陷严重程度分布</span>
                </template>
                <div ref="barChartRef" style="height: 300px"></div>
              </el-card>
            </el-col>
          </el-row>
          <el-row :gutter="20" style="margin-top: 20px">
            <el-col :span="24">
              <el-card>
                <template #header>
                  <span>测试趋势</span>
                </template>
                <div ref="lineChartRef" style="height: 300px"></div>
              </el-card>
            </el-col>
          </el-row>
        </el-tab-pane>

        <el-tab-pane label="报告模板" name="templates">
          <div class="toolbar">
            <div style="flex: 1"></div>
            <el-button type="primary" :icon="'Plus'" @click="handleCreateTemplate">新建模板</el-button>
          </div>
          <el-table :data="templateList" style="width: 100%">
            <el-table-column prop="name" label="模板名称" />
            <el-table-column prop="report_type" label="类型" width="120">
              <template #default="{ row }">
                <el-tag>{{ getReportTypeText(row.report_type) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="180" />
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
        </el-tab-pane>
      </el-tabs>
    </el-card>

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
              <template #suffix><span style="color: #67c23a">▼</span></template>
            </el-statistic>
          </el-col>
          <el-col :span="6">
            <el-statistic title="失败" :value="currentReport.failed_cases">
              <template #suffix><span style="color: #f56c6c">▼</span></template>
            </el-statistic>
          </el-col>
          <el-col :span="6">
            <el-statistic title="缺陷" :value="currentReport.total_defects">
              <template #suffix><span style="color: #e6a23c">▼</span></template>
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
import { View, Download, Edit, Delete, Plus } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { reportApi } from '@/api/report'
import { testPlanApi } from '@/api/test-plan'

const activeTab = ref('list')
const reportList = ref([])
const templateList = ref([])
const planList = ref([])

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
  if (rate < 60) return '#f56c6c'
  if (rate < 80) return '#e6a23c'
  return '#67c23a'
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
  // 饼图
  const pieChart = echarts.init(pieChartRef.value)
  pieChart.setOption({
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left' },
    series: [{
      type: 'pie',
      radius: '50%',
      data: [
        { value: 335, name: '通过' },
        { value: 234, name: '失败' },
        { value: 135, name: '阻塞' },
        { value: 48, name: '跳过' }
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
    xAxis: { type: 'category', data: ['紧急', '高', '中', '低', '轻微'] },
    yAxis: { type: 'value' },
    series: [{
      data: [12, 23, 45, 67, 8],
      type: 'bar',
      itemStyle: { color: '#409eff' }
    }]
  })

  // 折线图
  const lineChart = echarts.init(lineChartRef.value)
  lineChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'] },
    yAxis: { type: 'value' },
    series: [
      { name: '用例数', data: [120, 132, 101, 134, 90, 230, 210], type: 'line', smooth: true },
      { name: '通过率', data: [85, 88, 90, 87, 92, 95, 93], type: 'line', smooth: true }
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

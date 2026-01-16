<template>
  <div class="defect-detail-page">
    <el-page-header @back="goBack" title="返回">
      <template #content>
        <span class="page-title">{{ defect?.title }}</span>
      </template>
    </el-page-header>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="16">
        <el-card>
          <template #header>
            <span>缺陷详情</span>
          </template>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="缺陷编号">{{ defect?.defect_no }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="getStatusType(defect?.status)">{{ getStatusText(defect?.status) }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="严重程度">
              <el-tag :type="getSeverityType(defect?.severity)">{{ defect?.severity }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="优先级">
              <el-tag :type="getPriorityType(defect?.priority)">{{ defect?.priority }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="报告人">{{ defect?.reported_by }}</el-descriptions-item>
            <el-descriptions-item label="分配给">{{ defect?.assigned_to || '未分配' }}</el-descriptions-item>
            <el-descriptions-item label="报告日期">{{ defect?.reported_date }}</el-descriptions-item>
            <el-descriptions-item label="期望解决日期">{{ defect?.due_date || '-' }}</el-descriptions-item>
          </el-descriptions>

          <el-divider />

          <div class="section">
            <h4>描述</h4>
            <p>{{ defect?.description || '无描述' }}</p>
          </div>

          <div class="section">
            <h4>复现步骤</h4>
            <p>{{ defect?.reproduction_steps || '无复现步骤' }}</p>
          </div>

          <div class="section">
            <h4>期望行为</h4>
            <p>{{ defect?.expected_behavior || '无' }}</p>
          </div>

          <div class="section">
            <h4>实际行为</h4>
            <p>{{ defect?.actual_behavior || '无' }}</p>
          </div>

          <div class="section">
            <h4>环境信息</h4>
            <el-space>
              <el-tag v-if="defect?.environment">{{ defect.environment }}</el-tag>
              <el-tag v-if="defect?.browser">{{ defect.browser }}</el-tag>
              <el-tag v-if="defect?.os">{{ defect.os }}</el-tag>
            </el-space>
          </div>

          <div class="section" v-if="defect?.resolution">
            <h4>解决方案</h4>
            <p>{{ defect.resolution }}</p>
            <el-tag v-if="defect.resolution_version" type="success">{{ defect.resolution_version }}</el-tag>
          </div>
        </el-card>

        <el-card style="margin-top: 20px">
          <template #header>
            <span>评论 ({{ defect?.comment_count || 0 }})</span>
          </template>
          <div class="comments">
            <div v-for="comment in comments" :key="comment.id" class="comment-item">
              <div class="comment-header">
                <span class="comment-author">{{ comment.commented_by }}</span>
                <span class="comment-time">{{ comment.created_at }}</span>
              </div>
              <div class="comment-content">{{ comment.content }}</div>
            </div>
            <el-empty v-if="!comments || comments.length === 0" description="暂无评论" />
          </div>
          <div class="comment-input">
            <el-input
              v-model="newComment"
              type="textarea"
              :rows="3"
              placeholder="输入评论内容..."
            />
            <el-button type="primary" @click="handleAddComment" style="margin-top: 12px">发表评论</el-button>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card>
          <template #header>
            <span>操作</span>
          </template>
          <el-space direction="vertical" fill style="width: 100%">
            <el-button type="primary" :icon="'Edit'" @click="handleEdit">编辑</el-button>
            <el-button type="success" :icon="'User'" @click="handleAssign">分配</el-button>
            <el-button type="warning" :icon="'Close'" @click="handleClose">关闭</el-button>
            <el-button type="danger" :icon="'Delete'" @click="handleDelete">删除</el-button>
          </el-space>
        </el-card>

        <el-card style="margin-top: 20px">
          <template #header>
            <span>状态流程</span>
          </template>
          <el-steps direction="vertical" :space="80" :active="getStepIndex(defect?.status)">
            <el-step title="新建" description="缺陷已创建" />
            <el-step title="已分配" description="已分配处理人" />
            <el-step title="进行中" description="正在修复" />
            <el-step title="已解决" description="已修复" />
            <el-step title="已关闭" description="已关闭" />
          </el-steps>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { defectApi, defectCommentApi } from '@/api/defect'

const route = useRoute()
const router = useRouter()

const defect = ref(null)
const comments = ref([])
const newComment = ref('')

function goBack() {
  router.push('/defects')
}

function getSeverityType(severity) {
  const map = { critical: 'danger', high: 'warning', medium: 'primary', low: 'info', trivial: 'info' }
  return map[severity] || 'info'
}

function getPriorityType(priority) {
  const map = { urgent: 'danger', high: 'warning', medium: 'primary', low: 'info' }
  return map[priority] || 'info'
}

function getStatusType(status) {
  const map = { new: 'info', assigned: 'warning', in_progress: 'primary', resolved: 'success', closed: 'info' }
  return map[status] || 'info'
}

function getStatusText(status) {
  const map = { new: '新建', assigned: '已分配', in_progress: '进行中', resolved: '已解决', closed: '已关闭' }
  return map[status] || status
}

function getStepIndex(status) {
  const map = { new: 0, assigned: 1, in_progress: 2, resolved: 3, closed: 4 }
  return map[status] || 0
}

async function loadDefect() {
  const res = await defectApi.getDetail(route.params.id)
  defect.value = res.data
  comments.value = res.data?.comments || []
}

function handleEdit() {
  ElMessage.info('跳转到编辑页面')
}

function handleAssign() {
  ElMessageBox.prompt('请输入分配给谁', '分配缺陷', {
    confirmButtonText: '确定',
    cancelButtonText: '取消'
  }).then(({ value }) => {
    defectApi.assign(defect.value.id, { assigned_to: value }).then(() => {
      ElMessage.success('分配成功')
      loadDefect()
    })
  })
}

function handleClose() {
  ElMessageBox.confirm('确定要关闭这个缺陷吗？', '提示', { type: 'warning' })
    .then(() => defectApi.update(defect.value.id, { status: 'closed' }))
    .then(() => {
      ElMessage.success('已关闭')
      loadDefect()
    })
}

function handleDelete() {
  ElMessageBox.confirm('确定要删除这个缺陷吗？', '提示', { type: 'warning' })
    .then(() => defectApi.delete(defect.value.id))
    .then(() => {
      ElMessage.success('删除成功')
      router.push('/defects')
    })
}

function handleAddComment() {
  if (!newComment.value.trim()) {
    ElMessage.warning('请输入评论内容')
    return
  }
  defectCommentApi.create({
    defect_id: defect.value.id,
    content: newComment.value,
    commented_by: 'current_user'
  }).then(() => {
    ElMessage.success('评论成功')
    newComment.value = ''
    loadDefect()
  })
}

onMounted(() => {
  loadDefect()
})
</script>

<style scoped>
.page-title {
  font-size: 16px;
  font-weight: 500;
}

.section {
  margin-bottom: 24px;
}

.section h4 {
  margin-bottom: 8px;
  color: #303133;
}

.section p {
  color: #606266;
  line-height: 1.6;
}

.comment-item {
  padding: 12px 0;
  border-bottom: 1px solid #e4e7ed;
}

.comment-item:last-child {
  border-bottom: none;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.comment-author {
  font-weight: 500;
  color: #303133;
}

.comment-time {
  color: #909399;
  font-size: 12px;
}

.comment-content {
  color: #606266;
  line-height: 1.6;
}

.comment-input {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e4e7ed;
}
</style>

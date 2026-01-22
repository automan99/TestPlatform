<template>
  <div class="settings-page animate-fade-in-up">
    <!-- Page Header -->
    <div class="page-header">
      <h1 class="page-title">缺陷工作流</h1>
      <p class="page-description">配置缺陷状态和流转规则</p>
    </div>

    <!-- Action Bar -->
    <div class="action-bar">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索状态"
        clearable
        class="search-input"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <div style="flex: 1"></div>
      <el-button type="primary" :icon="Plus" @click="handleCreateStatus">新建状态</el-button>
    </div>

    <!-- Workflow Status List -->
    <div class="workflow-container">
      <div class="status-list">
        <div v-for="status in filteredStatuses" :key="status.id" class="status-card">
          <div class="status-header">
            <div class="status-info">
              <div class="status-badge" :style="{ backgroundColor: status.color }">
                {{ status.name }}
              </div>
              <div class="status-meta">
                <span class="status-code">{{ status.code }}</span>
                <el-tag :type="status.is_default ? 'success' : 'info'" size="small">
                  {{ status.is_default ? '默认' : '自定义' }}
                </el-tag>
                <el-tag :type="status.is_terminal ? 'warning' : 'info'" size="small">
                  {{ status.is_terminal ? '终态' : '进行中' }}
                </el-tag>
              </div>
            </div>
            <div class="status-actions">
              <el-button type="primary" link @click="handleEditStatus(status)">
                <el-icon><Edit /></el-icon>
              </el-button>
              <el-button type="danger" link @click="handleDeleteStatus(status)" :disabled="status.is_default">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>

          <div class="status-description">
            {{ status.description || '暂无描述' }}
          </div>

          <div class="status-transitions">
            <div class="transitions-title">
              <el-icon><Sort /></el-icon>
              可流转到
            </div>
            <div class="transitions-list">
              <el-tag
                v-for="targetId in status.transitions"
                :key="targetId"
                :style="{
                  backgroundColor: getStatusById(targetId)?.color,
                  color: '#fff',
                  border: 'none'
                }"
                closable
                @close="handleRemoveTransition(status.id, targetId)"
              >
                {{ getStatusById(targetId)?.name }}
              </el-tag>
              <el-dropdown
                trigger="click"
                @command="(cmd) => handleAddTransition(status.id, cmd)"
                v-if="availableTransitions(status.id).length > 0"
              >
                <el-button type="primary" link>
                  <el-icon><Plus /></el-icon>
                  添加流转
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item
                      v-for="target in availableTransitions(status.id)"
                      :key="target.id"
                      :command="target.id"
                    >
                      <span class="transition-dot" :style="{ backgroundColor: target.color }"></span>
                      {{ target.name }}
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </div>
      </div>

      <!-- Workflow Visualization -->
      <div class="workflow-viz">
        <h3 class="viz-title">工作流预览</h3>
        <div class="viz-canvas">
          <svg v-if="filteredStatuses.length > 0" viewBox="0 0 800 400" class="workflow-svg">
            <defs>
              <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                <polygon points="0 0, 10 3.5, 0 7" fill="#94a3b8" />
              </marker>
            </defs>
            <!-- Nodes -->
            <g v-for="(status, index) in filteredStatuses" :key="status.id">
              <rect
                :x="getNodePosition(index, filteredStatuses.length).x"
                :y="getNodePosition(index, filteredStatuses.length).y"
                width="100"
                height="40"
                :fill="status.color"
                rx="6"
              />
              <text
                :x="getNodePosition(index, filteredStatuses.length).x + 50"
                :y="getNodePosition(index, filteredStatuses.length).y + 25"
                text-anchor="middle"
                fill="white"
                font-size="12"
              >{{ status.name }}</text>
            </g>
            <!-- Edges -->
            <g v-for="status in filteredStatuses" :key="'edge-' + status.id">
              <line
                v-for="targetId in status.transitions"
                :key="targetId"
                :x1="getNodePosition(filteredStatuses.indexOf(status), filteredStatuses.length).x + 100"
                :y1="getNodePosition(filteredStatuses.indexOf(status), filteredStatuses.length).y + 20"
                :x2="getNodePosition(filteredStatuses.indexOf(getStatusById(targetId)), filteredStatuses.length).x"
                :y2="getNodePosition(filteredStatuses.indexOf(getStatusById(targetId)), filteredStatuses.length).y + 20"
                stroke="#94a3b8"
                stroke-width="2"
                marker-end="url(#arrowhead)"
              />
            </g>
          </svg>
          <el-empty v-else description="暂无状态数据" />
        </div>
      </div>
    </div>

    <!-- Status Form Dialog -->
    <el-dialog v-model="statusDialogVisible" :title="statusDialogTitle" width="500px" destroy-on-close>
      <el-form :model="statusForm" :rules="statusRules" ref="statusFormRef" label-width="100px">
        <el-form-item label="状态名称" prop="name">
          <el-input v-model="statusForm.name" placeholder="如：待处理、进行中、已解决" />
        </el-form-item>
        <el-form-item label="状态代码" prop="code">
          <el-input v-model="statusForm.code" placeholder="如：open、in_progress、resolved" :disabled="isEditStatus" />
        </el-form-item>
        <el-form-item label="状态颜色" prop="color">
          <el-color-picker v-model="statusForm.color" show-alpha />
          <span class="color-preview" :style="{ backgroundColor: statusForm.color }">{{ statusForm.name || '预览' }}</span>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="statusForm.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="设为默认">
          <el-switch v-model="statusForm.is_default" />
          <span class="form-hint">新创建的缺陷将使用此状态</span>
        </el-form-item>
        <el-form-item label="终态状态">
          <el-switch v-model="statusForm.is_terminal" />
          <span class="form-hint">终态状态无法再流转到其他状态</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="statusDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitStatus">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus, Edit, Delete, Sort } from '@element-plus/icons-vue'

const searchKeyword = ref('')

const statusList = ref([
  {
    id: 1,
    name: '待处理',
    code: 'open',
    color: '#64748b',
    description: '新创建的缺陷，等待处理',
    is_default: true,
    is_terminal: false,
    transitions: [2, 5]
  },
  {
    id: 2,
    name: '进行中',
    code: 'in_progress',
    color: '#3b82f6',
    description: '正在处理中的缺陷',
    is_default: false,
    is_terminal: false,
    transitions: [3, 4, 6]
  },
  {
    id: 3,
    name: '已解决',
    code: 'resolved',
    color: '#22c55e',
    description: '缺陷已修复，等待验证',
    is_default: false,
    is_terminal: false,
    transitions: [4, 5]
  },
  {
    id: 4,
    name: '已关闭',
    code: 'closed',
    color: '#64748b',
    description: '缺陷已确认关闭',
    is_default: false,
    is_terminal: true,
    transitions: []
  },
  {
    id: 5,
    name: '已拒绝',
    code: 'rejected',
    color: '#ef4444',
    description: '拒绝处理的缺陷',
    is_default: false,
    is_terminal: true,
    transitions: []
  },
  {
    id: 6,
    name: '重新打开',
    code: 'reopened',
    color: '#f59e0b',
    description: '之前关闭的缺陷重新打开',
    is_default: false,
    is_terminal: false,
    transitions: [2, 3]
  }
])

const filteredStatuses = computed(() => {
  if (!searchKeyword.value) return statusList.value
  return statusList.value.filter(s =>
    s.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
    s.code.toLowerCase().includes(searchKeyword.value.toLowerCase())
  )
})

const statusDialogVisible = ref(false)
const statusDialogTitle = ref('')
const statusFormRef = ref()
const isEditStatus = ref(false)

const statusForm = reactive({
  id: null,
  name: '',
  code: '',
  color: '#64748b',
  description: '',
  is_default: false,
  is_terminal: false,
  transitions: []
})

const statusRules = {
  name: [{ required: true, message: '请输入状态名称', trigger: 'blur' }],
  code: [
    { required: true, message: '请输入状态代码', trigger: 'blur' },
    { pattern: /^[a-z_]+$/, message: '只能包含小写字母和下划线', trigger: 'blur' }
  ],
  color: [{ required: true, message: '请选择状态颜色', trigger: 'change' }]
}

function getStatusById(id) {
  return statusList.value.find(s => s.id === id)
}

function availableTransitions(statusId) {
  return statusList.value.filter(s => s.id !== statusId && !getStatusById(statusId)?.transitions.includes(s.id))
}

function handleCreateStatus() {
  isEditStatus.value = false
  statusDialogTitle.value = '新建状态'
  Object.assign(statusForm, {
    id: null,
    name: '',
    code: '',
    color: '#64748b',
    description: '',
    is_default: false,
    is_terminal: false,
    transitions: []
  })
  statusDialogVisible.value = true
}

function handleEditStatus(status) {
  isEditStatus.value = true
  statusDialogTitle.value = '编辑状态'
  Object.assign(statusForm, {
    id: status.id,
    name: status.name,
    code: status.code,
    color: status.color,
    description: status.description,
    is_default: status.is_default,
    is_terminal: status.is_terminal,
    transitions: [...status.transitions]
  })
  statusDialogVisible.value = true
}

function handleSubmitStatus() {
  statusFormRef.value.validate((valid) => {
    if (valid) {
      if (isEditStatus.value) {
        const index = statusList.value.findIndex(s => s.id === statusForm.id)
        if (index !== -1) {
          statusList.value[index] = { ...statusForm }
        }
        ElMessage.success('更新成功')
      } else {
        const newId = Math.max(...statusList.value.map(s => s.id)) + 1
        statusList.value.push({
          ...statusForm,
          id: newId,
          transitions: []
        })
        ElMessage.success('创建成功')
      }
      statusDialogVisible.value = false
    }
  })
}

function handleDeleteStatus(status) {
  ElMessageBox.confirm('确定要删除该状态吗？', '确认删除', {
    type: 'warning'
  }).then(() => {
    const index = statusList.value.findIndex(s => s.id === status.id)
    if (index !== -1) {
      statusList.value.splice(index, 1)
      // Remove transitions to this status
      statusList.value.forEach(s => {
        const transitionIndex = s.transitions.indexOf(status.id)
        if (transitionIndex !== -1) {
          s.transitions.splice(transitionIndex, 1)
        }
      })
      ElMessage.success('删除成功')
    }
  })
}

function handleAddTransition(fromId, toId) {
  const status = statusList.value.find(s => s.id === fromId)
  if (status && !status.transitions.includes(toId)) {
    status.transitions.push(toId)
  }
}

function handleRemoveTransition(fromId, toId) {
  const status = statusList.value.find(s => s.id === fromId)
  if (status) {
    const index = status.transitions.indexOf(toId)
    if (index !== -1) {
      status.transitions.splice(index, 1)
    }
  }
}

function getNodePosition(index, total) {
  const width = 800
  const padding = 100
  const availableWidth = width - padding * 2
  const step = availableWidth / Math.max(total - 1, 1)
  return {
    x: padding + (total > 1 ? index * step : availableWidth / 2 - 50),
    y: 180
  }
}

onMounted(() => {
  // Load workflow statuses from backend
})
</script>

<style scoped>
.settings-page {
  padding: var(--space-6);
  background: var(--color-bg);
  min-height: 100vh;
}

.page-header {
  margin-bottom: var(--space-6);
}

.page-title {
  font-family: var(--font-display);
  font-size: 24px;
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: var(--space-2);
}

.page-description {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.action-bar {
  display: flex;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
  align-items: center;
}

.search-input {
  width: 300px;
}

.workflow-container {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: var(--space-5);
}

.status-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.status-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  transition: all var(--transition-base);
}

.status-card:hover {
  border-color: var(--color-primary);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.1);
}

.status-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--space-3);
}

.status-info {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: var(--radius-md);
  color: white;
  font-weight: 600;
  font-size: 14px;
}

.status-meta {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.status-code {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--color-text-muted);
  background: var(--color-bg-secondary);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
}

.status-actions {
  display: flex;
  gap: var(--space-1);
}

.status-description {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin-bottom: var(--space-3);
  padding: var(--space-3);
  background: var(--color-bg-secondary);
  border-radius: var(--radius-md);
}

.status-transitions {
  border-top: 1px solid var(--color-border-light);
  padding-top: var(--space-3);
}

.transitions-title {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-secondary);
  margin-bottom: var(--space-2);
}

.transitions-list {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  align-items: center;
}

.transition-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 8px;
}

.workflow-viz {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  position: sticky;
  top: var(--space-6);
  height: fit-content;
}

.viz-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: var(--space-4);
}

.viz-canvas {
  background: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.workflow-svg {
  width: 100%;
  height: auto;
}

.color-preview {
  display: inline-block;
  padding: 4px 12px;
  border-radius: var(--radius-md);
  color: white;
  font-size: 13px;
  margin-left: var(--space-2);
}

.form-hint {
  font-size: 12px;
  color: var(--color-text-muted);
  margin-left: var(--space-2);
}
</style>

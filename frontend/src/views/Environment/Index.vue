<template>
  <div class="environment-page">
    <el-card>
      <template #header>
        <div class="page-header">
          <span>测试环境管理</span>
          <el-button type="primary" :icon="Plus" @click="handleCreateEnv">新建环境</el-button>
        </div>
      </template>

      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="环境列表" name="list">
          <div class="toolbar">
            <el-input
              v-model="searchForm.keyword"
              placeholder="搜索环境"
              clearable
              style="width: 200px"
              @change="loadEnvironments"
            />
            <el-select v-model="searchForm.env_type" placeholder="环境类型" clearable @change="loadEnvironments">
              <el-option label="开发环境" value="dev" />
              <el-option label="测试环境" value="testing" />
              <el-option label="预发布环境" value="staging" />
              <el-option label="生产环境" value="production" />
            </el-select>
            <div style="flex: 1"></div>
          </div>

          <el-table :data="envList" style="width: 100%">
            <el-table-column prop="env_code" label="编码" width="120" />
            <el-table-column prop="name" label="环境名称" />
            <el-table-column prop="env_type" label="类型" width="120">
              <template #default="{ row }">
                <el-tag :type="getEnvTypeColor(row.env_type)">{{ getEnvTypeText(row.env_type) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="base_url" label="基础URL" show-overflow-tooltip />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'active' ? 'success' : 'info'">
                  {{ row.status === 'active' ? '正常' : '停用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="resources_count" label="资源数" width="100" />
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="handleViewResources(row)">资源</el-button>
                <el-button type="primary" link size="small" @click="handleEditEnv(row)">编辑</el-button>
                <el-button type="danger" link size="small" @click="handleDeleteEnv(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="主机资源" name="resources">
          <div class="toolbar">
            <el-select v-model="resourceSearchForm.environment_id" placeholder="选择环境" clearable @change="loadResources">
              <el-option v-for="env in envList" :key="env.id" :label="env.name" :value="env.id" />
            </el-select>
            <el-select v-model="resourceSearchForm.status" placeholder="状态" clearable @change="loadResources">
              <el-option label="在线" value="online" />
              <el-option label="离线" value="offline" />
              <el-option label="忙碌" value="busy" />
            </el-select>
            <div style="flex: 1"></div>
            <el-button type="primary" :icon="Plus" @click="handleCreateResource">新建资源</el-button>
          </div>

          <el-table :data="resourceList" style="width: 100%">
            <el-table-column prop="name" label="资源名称" />
            <el-table-column prop="resource_type" label="类型" width="100">
              <template #default="{ row }">
                <el-tag>{{ row.resource_type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="host" label="主机" />
            <el-table-column prop="port" label="端口" width="80" />
            <el-table-column prop="os_type" label="系统" width="100" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getResourceStatusType(row.status)">
                  {{ getResourceStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="handleEditResource(row)">编辑</el-button>
                <el-button type="danger" link size="small" @click="handleDeleteResource(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 环境表单对话框 -->
    <el-dialog v-model="envDialogVisible" title="环境配置" width="600px" destroy-on-close>
      <el-form :model="envForm" :rules="envRules" ref="envFormRef" label-width="100px">
        <el-form-item label="环境名称" prop="name">
          <el-input v-model="envForm.name" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="环境编码" prop="env_code">
              <el-input v-model="envForm.env_code" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="环境类型" prop="env_type">
              <el-select v-model="envForm.env_type" style="width: 100%">
                <el-option label="开发环境" value="dev" />
                <el-option label="测试环境" value="testing" />
                <el-option label="预发布环境" value="staging" />
                <el-option label="生产环境" value="production" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="基础URL" prop="base_url">
          <el-input v-model="envForm.base_url" placeholder="http://..." />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="envForm.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="envDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitEnv">确定</el-button>
      </template>
    </el-dialog>

    <!-- 资源表单对话框 -->
    <el-dialog v-model="resourceDialogVisible" title="资源配置" width="700px" destroy-on-close>
      <el-form :model="resourceForm" :rules="resourceRules" ref="resourceFormRef" label-width="100px">
        <el-form-item label="资源名称" prop="name">
          <el-input v-model="resourceForm.name" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="所属环境" prop="environment_id">
              <el-select v-model="resourceForm.environment_id" style="width: 100%">
                <el-option v-for="env in envList" :key="env.id" :label="env.name" :value="env.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="资源类型" prop="resource_type">
              <el-select v-model="resourceForm.resource_type" style="width: 100%">
                <el-option label="服务器" value="server" />
                <el-option label="数据库" value="database" />
                <el-option label="缓存" value="cache" />
                <el-option label="消息队列" value="message_queue" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="16">
            <el-form-item label="主机地址" prop="host">
              <el-input v-model="resourceForm.host" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="端口" prop="port">
              <el-input-number v-model="resourceForm.port" :min="1" :max="65535" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="用户名" prop="username">
              <el-input v-model="resourceForm.username" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="密码" prop="password">
              <el-input v-model="resourceForm.password" type="password" show-password />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="描述" prop="description">
          <el-input v-model="resourceForm.description" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resourceDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitResource">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { environmentApi, resourceApi } from '@/api/environment'

const activeTab = ref('list')
const envList = ref([])
const resourceList = ref([])

const envDialogVisible = ref(false)
const resourceDialogVisible = ref(false)
const envFormRef = ref()
const resourceFormRef = ref()

const searchForm = reactive({ keyword: '', env_type: '' })
const resourceSearchForm = reactive({ environment_id: null, status: '' })

const envForm = reactive({
  id: null,
  name: '',
  env_code: '',
  env_type: 'testing',
  base_url: '',
  description: ''
})

const resourceForm = reactive({
  id: null,
  environment_id: null,
  name: '',
  resource_type: 'server',
  host: '',
  port: 22,
  username: '',
  password: '',
  description: ''
})

const envRules = { name: [{ required: true, message: '请输入环境名称', trigger: 'blur' }] }
const resourceRules = {
  name: [{ required: true, message: '请输入资源名称', trigger: 'blur' }],
  environment_id: [{ required: true, message: '请选择环境', trigger: 'change' }]
}

function getEnvTypeColor(type) {
  const map = { dev: 'info', testing: 'warning', staging: 'primary', production: 'danger' }
  return map[type] || 'info'
}

function getEnvTypeText(type) {
  const map = { dev: '开发', testing: '测试', staging: '预发布', production: '生产' }
  return map[type] || type
}

function getResourceStatusType(status) {
  const map = { online: 'success', offline: 'info', busy: 'warning', error: 'danger' }
  return map[status] || 'info'
}

function getResourceStatusText(status) {
  const map = { online: '在线', offline: '离线', busy: '忙碌', error: '错误' }
  return map[status] || status
}

async function loadEnvironments() {
  const res = await environmentApi.getList(searchForm)
  envList.value = res.data?.items || []
}

async function loadResources() {
  const res = await resourceApi.getList(resourceSearchForm)
  resourceList.value = res.data?.items || []
}

function handleTabChange() {
  if (activeTab.value === 'resources') {
    loadResources()
  }
}

function handleCreateEnv() {
  Object.assign(envForm, {
    id: null,
    name: '',
    env_code: '',
    env_type: 'testing',
    base_url: '',
    description: ''
  })
  envDialogVisible.value = true
}

function handleEditEnv(row) {
  Object.assign(envForm, row)
  envDialogVisible.value = true
}

function handleDeleteEnv(row) {
  ElMessageBox.confirm('确定要删除这个环境吗？', '提示', { type: 'warning' })
    .then(() => environmentApi.delete(row.id))
    .then(() => {
      ElMessage.success('删除成功')
      loadEnvironments()
    })
}

function handleSubmitEnv() {
  envFormRef.value.validate((valid) => {
    if (valid) {
      const api = envForm.id ? environmentApi.update : environmentApi.create
      const params = envForm.id ? envForm.id : envForm
      api(params, envForm.id ? null : envForm).then(() => {
        ElMessage.success(envForm.id ? '更新成功' : '创建成功')
        envDialogVisible.value = false
        loadEnvironments()
      })
    }
  })
}

function handleViewResources(row) {
  activeTab.value = 'resources'
  resourceSearchForm.environment_id = row.id
  loadResources()
}

function handleCreateResource() {
  Object.assign(resourceForm, {
    id: null,
    environment_id: resourceSearchForm.environment_id,
    name: '',
    resource_type: 'server',
    host: '',
    port: 22,
    username: '',
    password: '',
    description: ''
  })
  resourceDialogVisible.value = true
}

function handleEditResource(row) {
  Object.assign(resourceForm, row)
  resourceDialogVisible.value = true
}

function handleDeleteResource(row) {
  ElMessageBox.confirm('确定要删除这个资源吗？', '提示', { type: 'warning' })
    .then(() => resourceApi.delete(row.id))
    .then(() => {
      ElMessage.success('删除成功')
      loadResources()
    })
}

function handleSubmitResource() {
  resourceFormRef.value.validate((valid) => {
    if (valid) {
      const api = resourceForm.id ? resourceApi.update : resourceApi.create
      const params = resourceForm.id ? resourceForm.id : resourceForm
      api(params, resourceForm.id ? null : resourceForm).then(() => {
        ElMessage.success(resourceForm.id ? '更新成功' : '创建成功')
        resourceDialogVisible.value = false
        loadResources()
      })
    }
  })
}

onMounted(() => {
  loadEnvironments()
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

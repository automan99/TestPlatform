<template>
  <div class="llm-models-config">
    <!-- 工具栏 -->
    <div class="toolbar">
      <el-input
        v-model="filters.keyword"
        placeholder="搜索模型名称或ID..."
        clearable
        class="search-input"
        style="width: 300px"
        @change="loadModels"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <el-select
        v-model="filters.provider"
        placeholder="提供商"
        clearable
        style="width: 150px"
        @change="loadModels"
      >
        <el-option label="OpenAI" value="openai" />
        <el-option label="Anthropic" value="anthropic" />
        <el-option label="Azure OpenAI" value="azure" />
        <el-option label="DeepSeek" value="deepseek" />
        <el-option label="Moonshot AI" value="moonshot" />
        <el-option label="智谱AI" value="zhipu" />
        <el-option label="百川智能" value="baichuan" />
      </el-select>
      <el-select
        v-model="filters.is_enabled"
        placeholder="状态"
        clearable
        style="width: 120px"
        @change="loadModels"
      >
        <el-option label="启用" value="true" />
        <el-option label="禁用" value="false" />
      </el-select>
      <div style="flex: 1"></div>
      <el-button type="primary" :icon="Plus" @click="handleCreate">新建模型</el-button>
    </div>

    <!-- 模型列表 -->
    <el-table :data="modelList" v-loading="loading" class="page-table">
      <el-table-column prop="name" label="模型名称" min-width="150" show-overflow-tooltip />
      <el-table-column prop="provider" label="提供商" width="120">
        <template #default="{ row }">
          <el-tag :type="getProviderTagType(row.provider)">{{ getProviderLabel(row.provider) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="model_id" label="模型ID" min-width="180" show-overflow-tooltip />
      <el-table-column prop="api_base" label="API地址" min-width="200" show-overflow-tooltip />
      <el-table-column label="参数" width="180">
        <template #default="{ row }">
          <span class="param-text">T: {{ row.temperature }}, Max: {{ row.max_tokens }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="is_default" label="默认" width="80" align="center">
        <template #default="{ row }">
          <el-tag v-if="row.is_default" type="success" size="small">是</el-tag>
          <span v-else style="color: var(--color-text-muted)">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="is_enabled" label="状态" width="80" align="center">
        <template #default="{ row }">
          <el-tag :type="row.is_enabled ? 'success' : 'info'" size="small">
            {{ row.is_enabled ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link size="small" @click="handleTest(row)" :loading="testingId === row.id">
            测试
          </el-button>
          <el-button type="primary" link size="small" @click="handleEdit(row)">编辑</el-button>
          <el-button type="success" link size="small" @click="handleSetDefault(row)" v-if="!row.is_default">
            设为默认
          </el-button>
          <el-button type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <el-pagination
      v-model:current-page="pagination.page"
      v-model:page-size="pagination.per_page"
      :total="pagination.total"
      :page-sizes="[10, 20, 50, 100]"
      layout="total, sizes, prev, pager, next, jumper"
      @current-change="loadModels"
      @size-change="loadModels"
      style="margin-top: 20px; justify-content: flex-end"
    />

    <!-- 新建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑模型' : '新建模型'"
      width="700px"
      destroy-on-close
      @close="resetForm"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="模型名称" prop="name">
          <el-input v-model="form.name" placeholder="例如: GPT-4 生产环境" />
        </el-form-item>
        <el-form-item label="提供商" prop="provider">
          <el-select v-model="form.provider" placeholder="选择提供商" style="width: 100%" @change="handleProviderChange">
            <el-option label="OpenAI" value="openai" />
            <el-option label="Anthropic" value="anthropic" />
            <el-option label="Azure OpenAI" value="azure" />
            <el-option label="DeepSeek" value="deepseek" />
            <el-option label="Moonshot AI" value="moonshot" />
            <el-option label="智谱AI" value="zhipu" />
            <el-option label="百川智能" value="baichuan" />
          </el-select>
        </el-form-item>
        <el-form-item label="模型ID" prop="model_id">
          <el-select
            v-model="form.model_id"
            placeholder="选择或输入模型ID"
            style="width: 100%"
            filterable
            allow-create
          >
            <el-option
              v-for="model in getCurrentProviderModels()"
              :key="model"
              :label="model"
              :value="model"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="API密钥" prop="api_key">
          <el-input
            v-model="form.api_key"
            type="password"
            placeholder="请输入API密钥"
            show-password
          />
        </el-form-item>
        <el-form-item label="API地址" prop="api_base">
          <el-input v-model="form.api_base" :placeholder="getApiBasePlaceholder()" />
        </el-form-item>
        <el-form-item label="API版本" prop="api_version" v-if="form.provider === 'azure'">
          <el-input v-model="form.api_version" placeholder="例如: 2024-02-15-preview" />
        </el-form-item>
        <el-divider content-position="left">模型参数</el-divider>
        <el-form-item label="温度">
          <el-slider v-model="form.temperature" :min="0" :max="2" :step="0.1" show-input />
        </el-form-item>
        <el-form-item label="最大Tokens">
          <el-input-number v-model="form.max_tokens" :min="1" :max="128000" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Top P">
          <el-slider v-model="form.top_p" :min="0" :max="1" :step="0.1" show-input />
        </el-form-item>
        <el-form-item label="频率惩罚">
          <el-slider v-model="form.frequency_penalty" :min="-2" :max="2" :step="0.1" show-input />
        </el-form-item>
        <el-form-item label="存在惩罚">
          <el-slider v-model="form.presence_penalty" :min="-2" :max="2" :step="0.1" show-input />
        </el-form-item>
        <el-form-item label="设为默认">
          <el-switch v-model="form.is_default" />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="form.is_enabled" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="模型描述..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import { llmModelApi } from '@/api/llm-models'

// 提供商配置
const providers = {
  openai: {
    label: 'OpenAI',
    models: ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo', 'gpt-4o', 'gpt-4o-mini'],
    apiBase: 'https://api.openai.com/v1'
  },
  anthropic: {
    label: 'Anthropic',
    models: ['claude-3-opus-20240229', 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307', 'claude-3-5-sonnet-20240620'],
    apiBase: 'https://api.anthropic.com'
  },
  azure: {
    label: 'Azure OpenAI',
    models: ['gpt-4', 'gpt-35-turbo'],
    apiBase: ''
  },
  deepseek: {
    label: 'DeepSeek',
    models: ['deepseek-chat', 'deepseek-coder'],
    apiBase: 'https://api.deepseek.com/v1'
  },
  moonshot: {
    label: 'Moonshot AI',
    models: ['moonshot-v1-8k', 'moonshot-v1-32k', 'moonshot-v1-128k'],
    apiBase: 'https://api.moonshot.cn/v1'
  },
  zhipu: {
    label: '智谱AI',
    models: ['glm-4', 'glm-3-turbo'],
    apiBase: 'https://open.bigmodel.cn/api/paas/v4'
  },
  baichuan: {
    label: '百川智能',
    models: ['Baichuan2-Turbo', 'Baichuan2-53B'],
    apiBase: 'https://api.baichuan-ai.com/v1'
  }
}

// 状态
const loading = ref(false)
const testingId = ref(null)
const dialogVisible = ref(false)
const isEdit = ref(false)
const saving = ref(false)
const modelList = ref([])
const formRef = ref()

// 筛选
const filters = reactive({
  keyword: '',
  provider: '',
  is_enabled: ''
})

// 分页
const pagination = reactive({
  page: 1,
  per_page: 20,
  total: 0
})

// 表单
const form = reactive({
  name: '',
  provider: 'openai',
  model_id: '',
  api_key: '',
  api_base: 'https://api.openai.com/v1',
  api_version: '',
  temperature: 0.7,
  max_tokens: 4096,
  top_p: 1.0,
  frequency_penalty: 0.0,
  presence_penalty: 0.0,
  is_default: false,
  is_enabled: true,
  description: ''
})

// 表单验证规则
const rules = {
  name: [{ required: true, message: '请输入模型名称', trigger: 'blur' }],
  provider: [{ required: true, message: '请选择提供商', trigger: 'change' }],
  model_id: [{ required: true, message: '请输入模型ID', trigger: 'blur' }],
  api_key: [{ required: true, message: '请输入API密钥', trigger: 'blur' }]
}

// 获取提供商标签
const getProviderLabel = (provider) => {
  return providers[provider]?.label || provider
}

// 获取提供商标签类型
const getProviderTagType = (provider) => {
  const types = {
    openai: 'primary',
    anthropic: 'success',
    azure: 'warning',
    deepseek: 'info',
    moonshot: 'danger',
    zhipu: '',
    baichuan: ''
  }
  return types[provider] || ''
}

// 获取当前提供商的模型列表
const getCurrentProviderModels = () => {
  return providers[form.provider]?.models || []
}

// 获取API地址占位符
const getApiBasePlaceholder = () => {
  if (form.provider === 'azure') {
    return 'https://your-resource.openai.azure.com'
  }
  return providers[form.provider]?.apiBase || ''
}

// 提供商变更处理
const handleProviderChange = () => {
  form.api_base = getApiBasePlaceholder()
  form.model_id = ''
}

// 加载模型列表
const loadModels = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      per_page: pagination.per_page
    }
    if (filters.keyword) params.keyword = filters.keyword
    if (filters.provider) params.provider = filters.provider
    if (filters.is_enabled) params.is_enabled = filters.is_enabled

    const res = await llmModelApi.getList(params)
    modelList.value = res.data.items
    pagination.total = res.data.total
  } catch (error) {
    console.error('加载模型列表失败:', error)
    ElMessage.error('加载模型列表失败')
  } finally {
    loading.value = false
  }
}

// 新建
const handleCreate = () => {
  isEdit.value = false
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row) => {
  isEdit.value = true
  Object.assign(form, {
    id: row.id,
    name: row.name,
    provider: row.provider,
    model_id: row.model_id,
    api_key: '', // 不回显密钥
    api_base: row.api_base || '',
    api_version: row.api_version || '',
    temperature: row.temperature,
    max_tokens: row.max_tokens,
    top_p: row.top_p,
    frequency_penalty: row.frequency_penalty,
    presence_penalty: row.presence_penalty,
    is_default: row.is_default,
    is_enabled: row.is_enabled,
    description: row.description || ''
  })
  dialogVisible.value = true
}

// 保存
const handleSave = async () => {
  await formRef.value.validate()
  saving.value = true
  try {
    const data = { ...form }
    delete data.id

    if (isEdit.value) {
      await llmModelApi.update(form.id, data)
      ElMessage.success('更新成功')
    } else {
      await llmModelApi.create(data)
      ElMessage.success('创建成功')
    }

    dialogVisible.value = false
    loadModels()
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error(error.response?.data?.message || '保存失败')
  } finally {
    saving.value = false
  }
}

// 删除
const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除模型"${row.name}"吗？`, '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      await llmModelApi.delete(row.id)
      ElMessage.success('删除成功')
      loadModels()
    } catch (error) {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

// 测试连接
const handleTest = async (row) => {
  testingId.value = row.id
  try {
    const res = await llmModelApi.test(row.id)
    if (res.data?.status === 'success') {
      ElMessage.success('连接测试成功')
    } else {
      ElMessage.error('连接测试失败')
    }
  } catch (error) {
    console.error('测试失败:', error)
    ElMessage.error(error.response?.data?.message || '连接测试失败')
  } finally {
    testingId.value = null
  }
}

// 设为默认
const handleSetDefault = (row) => {
  ElMessageBox.confirm(`确定将"${row.name}"设为默认模型吗？`, '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      await llmModelApi.update(row.id, { is_default: true })
      ElMessage.success('设置成功')
      loadModels()
    } catch (error) {
      console.error('设置失败:', error)
      ElMessage.error('设置失败')
    }
  }).catch(() => {})
}

// 重置表单
const resetForm = () => {
  formRef.value?.resetFields()
  Object.assign(form, {
    name: '',
    provider: 'openai',
    model_id: '',
    api_key: '',
    api_base: 'https://api.openai.com/v1',
    api_version: '',
    temperature: 0.7,
    max_tokens: 4096,
    top_p: 1.0,
    frequency_penalty: 0.0,
    presence_penalty: 0.0,
    is_default: false,
    is_enabled: true,
    description: ''
  })
}

// 初始化
onMounted(() => {
  loadModels()
})
</script>

<style scoped>
.llm-models-config {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.param-text {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.page-table {
  flex: 1;
}
</style>

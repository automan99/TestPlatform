<template>
  <div class="mcp-servers-page animate-fade-in-up">
    <el-card>
      <!-- MCP Server 左右布局 -->
      <div class="mcp-server-layout">
        <!-- 左侧 MCP Server 列表 -->
        <div class="mcp-server-list">
          <div class="list-header">
            <div class="list-title">MCP Servers</div>
            <el-button type="primary" :icon="Plus" size="small" @click="handleCreateMCP">新建</el-button>
          </div>
          <div class="list-search">
            <el-input
              v-model="mcpSearchForm.keyword"
              placeholder="搜索MCP名称..."
              clearable
              size="small"
              @change="loadMCPServers"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </div>
          <!-- 状态统计面板 -->
          <div class="status-panel">
            <div class="stat-item">
              <span class="stat-dot online"></span>
              <span class="stat-label">在线: {{ mcpStatusStats.online }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-dot offline"></span>
              <span class="stat-label">离线: {{ mcpStatusStats.offline }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-dot unknown"></span>
              <span class="stat-label">未知: {{ mcpStatusStats.unknown }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-total">总计: {{ mcpList.length }}</span>
            </div>
            <div style="flex: 1"></div>
            <el-button :icon="Refresh" size="small" circle @click="syncAllMCP" :loading="syncingAll" title="同步"></el-button>
          </div>
          <div class="list-items">
            <div
              v-for="mcp in mcpList"
              :key="mcp.id"
              :class="['list-item', { active: selectedMcpId === mcp.id }]"
              @click="selectMCP(mcp)"
            >
              <div class="item-header">
                <div class="item-left">
                  <el-icon :class="['status-icon', getConnectionStatusClass(mcp)]" :title="getConnectionStatusText(mcp)">
                    <component :is="getStatusIcon(mcp)" />
                  </el-icon>
                  <span class="item-name">{{ mcp.name }}</span>
                </div>
                <div class="item-tags">
                  <el-tag v-if="mcp.is_builtin" type="warning" size="small">内置</el-tag>
                  <el-switch
                    :model-value="mcp.is_enabled"
                    @update:model-value="(val) => handleToggleMCPStatus(mcp, val)"
                    size="small"
                    @click.stop
                  />
                </div>
              </div>
              <div class="item-info">
                <el-tag size="small" type="info">{{ getTransportTypeText(mcp.transport_type) }}</el-tag>
                <span class="item-command">{{ mcp.transport_type === 'stdio' ? mcp.command : mcp.url }}</span>
                <span class="item-tools-count">工具: {{ mcp.tools_count || 0 }}</span>
              </div>
            </div>
            <el-empty v-if="mcpList.length === 0" description="暂无MCP Server" :image-size="60" />
          </div>
        </div>

        <!-- 右侧 MCP Server 详情 -->
        <div class="mcp-server-detail">
          <div v-if="!selectedMcp" class="detail-empty">
            <el-empty description="请选择一个 MCP Server 查看详情" :image-size="100" />
          </div>
          <div v-else class="detail-content">
            <!-- 详情头部 -->
            <div class="detail-header">
              <div class="header-left">
                <h2 class="detail-title">{{ selectedMcp.name }}</h2>
                <el-tag v-if="selectedMcp.is_builtin" type="warning">内置</el-tag>
                <el-tag :type="selectedMcp.is_enabled ? 'success' : 'info'">
                  {{ selectedMcp.is_enabled ? '启用' : '禁用' }}
                </el-tag>
                <el-tag type="info">{{ getTransportTypeText(selectedMcp.transport_type) }}</el-tag>
              </div>
              <div class="header-actions">
                <el-button :icon="Refresh" @click="refreshMCPDetail" :loading="detailLoading">同步</el-button>
                <el-button v-if="!selectedMcp.is_builtin" :icon="Edit" @click="handleEditMCP(selectedMcp)">编辑</el-button>
                <el-button v-if="!selectedMcp.is_builtin" :icon="Delete" type="danger" @click="handleDeleteMCP(selectedMcp)">删除</el-button>
              </div>
            </div>

            <!-- 详情 Tabs -->
            <el-tabs v-model="detailTab" class="detail-tabs">
              <!-- 基本信息 -->
              <el-tab-pane label="基本信息" name="info">
                <div class="info-section">
                  <div class="info-row">
                    <span class="label">编码：</span>
                    <span class="value">{{ selectedMcp.code || `MCP-${selectedMcp.id}` }}</span>
                  </div>
                  <div v-if="selectedMcp.transport_type === 'stdio'" class="info-row">
                    <span class="label">执行命令：</span>
                    <span class="value code">{{ selectedMcp.command }}</span>
                  </div>
                  <div v-if="selectedMcp.transport_type === 'stdio'" class="info-row">
                    <span class="label">命令参数：</span>
                    <span class="value code">{{ formatArguments(selectedMcp.arguments) }}</span>
                  </div>
                  <div v-if="selectedMcp.transport_type === 'stdio'" class="info-row">
                    <span class="label">环境变量：</span>
                    <span class="value code">{{ formatEnv(selectedMcp.env) }}</span>
                  </div>
                  <div v-if="selectedMcp.transport_type !== 'stdio'" class="info-row">
                    <span class="label">连接URL：</span>
                    <span class="value code">{{ selectedMcp.url }}</span>
                  </div>
                  <div class="info-row">
                    <span class="label">超时时间：</span>
                    <span class="value">{{ selectedMcp.timeout }}秒</span>
                  </div>
                  <div class="info-row">
                    <span class="label">使用次数：</span>
                    <span class="value">{{ selectedMcp.usage_count }}</span>
                  </div>
                  <div class="info-row">
                    <span class="label">最后使用：</span>
                    <span class="value">{{ selectedMcp.last_used_at || '-' }}</span>
                  </div>
                </div>
              </el-tab-pane>

              <!-- 可用工具 -->
              <el-tab-pane label="可用工具" name="tools">
                <div class="tools-section">
                  <div v-if="tools.length === 0" class="tools-empty">
                    <el-empty description="暂无工具，请点击上方同步按钮" :image-size="60" />
                  </div>
                  <div v-else class="tools-list">
                    <div v-for="tool in tools" :key="tool.name" class="tool-item">
                      <div class="tool-header">
                        <span class="tool-name">{{ tool.name }}</span>
                        <el-button type="primary" size="small" @click="showToolDebug(tool)">调试</el-button>
                      </div>
                      <div class="tool-description">{{ tool.description }}</div>
                    </div>
                  </div>
                </div>
              </el-tab-pane>

              <!-- 资源列表 -->
              <el-tab-pane label="资源" name="resources">
                <div class="resources-section">
                  <div v-if="resources.length === 0" class="resources-empty">
                    <el-empty description="暂无资源" :image-size="60" />
                  </div>
                  <div v-else class="resources-list">
                    <div v-for="resource in resources" :key="resource.uri" class="resource-item">
                      <div class="resource-header">
                        <span class="resource-name">{{ resource.name }}</span>
                        <el-tag size="small">{{ resource.mime_type }}</el-tag>
                      </div>
                      <div class="resource-description">{{ resource.description }}</div>
                      <div class="resource-uri">{{ resource.uri }}</div>
                    </div>
                  </div>
                </div>
              </el-tab-pane>

              <!-- 调试面板 -->
              <el-tab-pane label="调试" name="debug">
                <div class="debug-section">
                  <div class="debug-header">
                    <span>工具调试</span>
                  </div>

                  <!-- 工具选择 -->
                  <div class="debug-tool-selector">
                    <el-form :model="debugForm" label-width="100px" label-position="top">
                      <el-form-item label="选择工具">
                        <el-select
                          v-model="debugForm.toolName"
                          placeholder="请选择工具"
                          style="width: 100%"
                          @change="onToolChange"
                        >
                          <el-option v-for="tool in tools" :key="tool.name" :label="tool.name" :value="tool.name" />
                        </el-select>
                      </el-form-item>
                    </el-form>
                  </div>

                  <!-- 工具说明和参数定义 -->
                  <div v-if="selectedTool" class="debug-tool-info">
                    <div class="tool-info-card">
                      <div class="tool-info-header" @click="toolInfoCollapsed = !toolInfoCollapsed" style="cursor: pointer">
                        <span class="tool-info-title">{{ selectedTool.name }}</span>
                        <div style="display: flex; align-items: center; gap: 8px">
                          <el-tag size="small">{{ selectedTool.name }}</el-tag>
                          <el-icon :class="{ 'icon-rotate': toolInfoCollapsed }"><ArrowDown /></el-icon>
                        </div>
                      </div>
                      <div v-show="!toolInfoCollapsed">
                        <div class="tool-info-description">{{ selectedTool.description }}</div>

                        <!-- 参数说明表格 -->
                        <div v-if="schemaParams.length > 0" class="schema-params-table">
                          <div class="schema-title">参数说明</div>
                          <el-table :data="schemaParams" size="small" border>
                            <el-table-column prop="name" label="参数名" width="150" />
                            <el-table-column prop="type" label="类型" width="100" />
                            <el-table-column prop="required" label="必填" width="80">
                              <template #default="{ row }">
                                <el-tag :type="row.required ? 'danger' : 'info'" size="small">
                                  {{ row.required ? '是' : '否' }}
                                </el-tag>
                              </template>
                            </el-table-column>
                            <el-table-column prop="description" label="说明" />
                          </el-table>
                        </div>
                        <div v-else class="no-params">
                          <el-text type="info">该工具无需参数</el-text>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- 参数输入表单 -->
                  <div v-if="selectedTool" class="debug-params-form">
                    <div class="params-form-header">
                      <span>参数输入</span>
                      <el-button size="small" text @click="toggleParamsMode">
                        {{ paramsMode === 'form' ? 'JSON模式' : '表单模式' }}
                      </el-button>
                    </div>

                    <!-- 表单模式 -->
                    <div v-if="paramsMode === 'form'" class="params-form-content">
                      <el-form :model="debugParams" label-width="120px" label-position="left">
                        <el-form-item
                          v-for="param in schemaParams"
                          :key="param.name"
                          :label="param.name"
                          :required="param.required"
                        >
                          <template #label>
                            <span>{{ param.name }}</span>
                            <el-tooltip v-if="param.description" :content="param.description" placement="top">
                              <el-icon style="margin-left: 4px; cursor: help;"><InfoFilled /></el-icon>
                            </el-tooltip>
                          </template>

                          <!-- 根据类型显示不同的输入组件 -->
                          <el-input
                            v-if="param.type === 'string' && !param.enum"
                            v-model="debugParams[param.name]"
                            :placeholder="param.description || `请输入${param.name}`"
                          />
                          <el-select
                            v-else-if="param.enum"
                            v-model="debugParams[param.name]"
                            :placeholder="`请选择${param.name}`"
                            style="width: 100%"
                          >
                            <el-option v-for="opt in param.enum" :key="opt" :label="opt" :value="opt" />
                          </el-select>
                          <el-input-number
                            v-else-if="param.type === 'number' || param.type === 'integer'"
                            v-model="debugParams[param.name]"
                            style="width: 100%"
                          />
                          <el-switch
                            v-else-if="param.type === 'boolean'"
                            v-model="debugParams[param.name]"
                          />
                          <el-input
                            v-else-if="param.type === 'array'"
                            v-model="debugParamsArray[param.name]"
                            type="textarea"
                            :rows="2"
                            placeholder="请输入数组格式的值，如: [&quot;item1&quot;, &quot;item2&quot;]"
                            @input="parseArrayParam(param.name)"
                          />
                          <el-input
                            v-else
                            v-model="debugParams[param.name]"
                            type="textarea"
                            :rows="2"
                            :placeholder="param.description || `请输入${param.name}`"
                          />
                        </el-form-item>

                        <el-form-item v-if="schemaParams.length === 0">
                          <el-text type="info">该工具无需参数</el-text>
                        </el-form-item>
                      </el-form>
                    </div>

                    <!-- JSON模式 -->
                    <div v-else class="params-json-content">
                      <el-input
                        v-model="debugForm.paramsJson"
                        type="textarea"
                        :rows="6"
                        placeholder='{"param1": "value1"}'
                        class="code-editor"
                      />
                      <div v-if="paramsJsonError" class="params-json-error">
                        <el-text type="danger">{{ paramsJsonError }}</el-text>
                      </div>
                    </div>

                    <div class="debug-actions">
                      <el-button type="primary" :icon="VideoPlay" @click="invokeTool" :loading="debugInvoking">
                        执行
                      </el-button>
                      <el-button @click="clearDebugResult">清空结果</el-button>
                      <el-button v-if="paramsMode === 'form'" @click="fillParamsExample">填充示例</el-button>
                    </div>
                  </div>

                  <!-- 执行结果 -->
                  <div v-if="debugResult" class="debug-result">
                    <div class="result-header">执行结果</div>
                    <pre class="result-content">{{ debugResult }}</pre>
                  </div>
                </div>
              </el-tab-pane>
            </el-tabs>
          </div>
        </div>
      </div>
    </el-card>

    <!-- MCP Server 表单对话框 -->
    <el-dialog v-model="mcpDialogVisible" :title="mcpDialogTitle" width="800px" destroy-on-close>
      <el-form :model="mcpForm" :rules="mcpRules" ref="mcpFormRef" label-width="120px">
        <el-form-item label="MCP名称" prop="name">
          <el-input v-model="mcpForm.name" placeholder="请输入MCP Server名称" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="传输类型" prop="transport_type">
              <el-select v-model="mcpForm.transport_type" style="width: 100%">
                <el-option label="Stdio" value="stdio" />
                <el-option label="SSE" value="sse" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态" prop="status">
              <el-select v-model="mcpForm.status" style="width: 100%">
                <el-option label="启用" value="active" />
                <el-option label="禁用" value="inactive" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- Stdio 类型配置 -->
        <template v-if="mcpForm.transport_type === 'stdio'">
          <el-form-item label="执行命令" prop="command">
            <el-input v-model="mcpForm.command" placeholder="例如: npx, python, /path/to/server" />
          </el-form-item>
          <el-form-item label="命令参数">
            <el-input
              v-model="mcpForm.arguments_text"
              type="textarea"
              :rows="3"
              placeholder="一行一个参数，例如：&#10;--port=3000&#10;--debug&#10;--config=/path/to/config.json"
            />
            <div class="form-tip">每行输入一个参数</div>
          </el-form-item>
          <el-form-item label="环境变量">
            <el-input
              v-model="mcpForm.env_text"
              type="textarea"
              :rows="3"
              placeholder="一行一个变量，格式：KEY=VALUE，例如：&#10;API_KEY=your_api_key&#10;NODE_ENV=production&#10;DEBUG=true"
            />
            <div class="form-tip">格式：KEY=VALUE，每行一个</div>
          </el-form-item>
        </template>

        <!-- SSE 类型配置 -->
        <template v-if="mcpForm.transport_type === 'sse'">
          <el-form-item label="连接URL" prop="url">
            <el-input v-model="mcpForm.url" placeholder="https://example.com/mcp-endpoint" />
          </el-form-item>
        </template>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="超时时间">
              <el-input-number v-model="mcpForm.timeout" :min="1" :max="300" style="width: 100%" />
              <span style="margin-left: 8px">秒</span>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="mcpDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitMCP">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Search, Edit, Delete, VideoPlay, Refresh, InfoFilled, ArrowDown,
  SuccessFilled, CircleCloseFilled, WarningFilled
} from '@element-plus/icons-vue'
import { mcpServerApi } from '@/api/mcp-skills'

const mcpList = ref([])

// MCP Server 相关
const selectedMcpId = ref(null)
const selectedMcp = computed(() => mcpList.value.find(m => m.id === selectedMcpId.value))
const detailTab = ref('info')
const detailLoading = ref(false)
const toolsLoading = ref(false)
const resourcesLoading = ref(false)
const tools = ref([])
const resources = ref([])

// 连接状态相关
const mcpConnectionStatus = ref({})  // { mcpId: 'online' | 'offline' | 'unknown' }
const checkingAll = ref(false)
const syncingAll = ref(false)

// 状态统计
const mcpStatusStats = computed(() => {
  const stats = { online: 0, offline: 0, unknown: 0 }
  mcpList.value.forEach(mcp => {
    const status = mcpConnectionStatus.value[mcp.id] || 'unknown'
    stats[status]++
  })
  return stats
})

// 调试相关
const debugInvoking = ref(false)
const debugResult = ref('')
const debugForm = reactive({
  toolName: '',
  paramsJson: ''
})
const toolInfoCollapsed = ref(false) // 工具说明折叠状态，默认展开
const selectedTool = ref(null)
const paramsMode = ref('form') // 'form' or 'json'
const debugParams = reactive({})
const debugParamsArray = reactive({})
const paramsJsonError = ref('')

// 计算属性：解析参数schema
const schemaParams = computed(() => {
  if (!selectedTool.value?.input_schema) return []

  // 解析 JSON 字符串
  let schema
  if (typeof selectedTool.value.input_schema === 'string') {
    try {
      schema = JSON.parse(selectedTool.value.input_schema)
    } catch (e) {
      console.error('Failed to parse input_schema:', e)
      return []
    }
  } else {
    schema = selectedTool.value.input_schema
  }

  const params = []

  // 解析 JSON Schema 格式
  if (schema.properties) {
    // 标准 JSON Schema 格式
    const required = schema.required || []
    Object.entries(schema.properties).forEach(([name, propSchema]) => {
      params.push({
        name,
        type: propSchema.type || 'string',
        required: required.includes(name),
        description: propSchema.description || '',
        enum: propSchema.enum,
        default: propSchema.default
      })
    })
  } else if (schema.type === 'object' && schema.properties) {
    // 嵌套的 object 类型
    const required = schema.required || []
    Object.entries(schema.properties).forEach(([name, propSchema]) => {
      params.push({
        name,
        type: propSchema.type || 'string',
        required: required.includes(name),
        description: propSchema.description || '',
        enum: propSchema.enum,
        default: propSchema.default
      })
    })
  }

  return params
})

// 当前选中工具的信息
function onToolChange(toolName) {
  selectedTool.value = tools.value.find(t => t.name === toolName) || null
  // 重置参数
  Object.keys(debugParams).forEach(key => delete debugParams[key])
  Object.keys(debugParamsArray).forEach(key => delete debugParamsArray[key])
  debugForm.paramsJson = '{}'
  paramsJsonError.value = ''

  // 设置默认值
  if (selectedTool.value?.input_schema) {
    schemaParams.value.forEach(param => {
      if (param.default !== undefined) {
        debugParams[param.name] = param.default
      } else if (param.type === 'boolean') {
        debugParams[param.name] = false
      } else if (param.type === 'array') {
        debugParams[param.name] = []
        debugParamsArray[param.name] = '[]'
      }
    })
  }
}

// 切换参数输入模式
function toggleParamsMode() {
  paramsMode.value = paramsMode.value === 'form' ? 'json' : 'form'
  if (paramsMode.value === 'form' && debugForm.paramsJson) {
    // 从JSON模式切换到表单模式，解析JSON填充表单
    try {
      const params = JSON.parse(debugForm.paramsJson)
      Object.entries(params).forEach(([key, value]) => {
        if (Array.isArray(value)) {
          debugParamsArray[key] = JSON.stringify(value)
        } else {
          debugParams[key] = value
        }
      })
      paramsJsonError.value = ''
    } catch (e) {
      // JSON解析失败，保持表单不变
    }
  } else if (paramsMode.value === 'json') {
    // 从表单模式切换到JSON模式，生成JSON
    const params = {}
    schemaParams.value.forEach(param => {
      const value = debugParams[param.name]
      if (value !== undefined && value !== '') {
        if (param.type === 'array' && debugParamsArray[param.name]) {
          try {
            params[param.name] = JSON.parse(debugParamsArray[param.name])
          } catch (e) {
            // 数组解析失败，使用原始值
          }
        } else {
          params[param.name] = value
        }
      }
    })
    debugForm.paramsJson = Object.keys(params).length > 0 ? JSON.stringify(params, null, 2) : '{}'
  }
}

// 解析数组类型的参数
function parseArrayParam(name) {
  const value = debugParamsArray[name]
  try {
    if (value && value.trim()) {
      const parsed = JSON.parse(value)
      debugParams[name] = parsed
    } else {
      debugParams[name] = []
    }
  } catch (e) {
    // 解析失败，稍后在validate时处理
  }
}

// 验证参数
function validateParams() {
  const errors = []

  schemaParams.value.forEach(param => {
    const value = debugParams[param.name]

    // 检查必填参数
    if (param.required && (value === undefined || value === null || value === '')) {
      errors.push(`参数 "${param.name}" 为必填项`)
      return
    }

    // 类型验证
    if (value !== undefined && value !== null && value !== '') {
      if (param.type === 'number' || param.type === 'integer') {
        if (isNaN(Number(value))) {
          errors.push(`参数 "${param.name}" 必须是数字`)
        }
      } else if (param.type === 'boolean' && typeof value !== 'boolean') {
        // 布尔值已经通过switch组件处理，这里忽略
      } else if (param.type === 'array') {
        if (!Array.isArray(value)) {
          errors.push(`参数 "${param.name}" 必须是数组格式`)
        }
      } else if (param.enum && !param.enum.includes(value)) {
        errors.push(`参数 "${param.name}" 必须是以下值之一: ${param.enum.join(', ')}`)
      }
    }
  })

  return errors
}

// 填充示例参数
function fillParamsExample() {
  schemaParams.value.forEach(param => {
    if (param.enum && param.enum.length > 0) {
      debugParams[param.name] = param.enum[0]
    } else if (param.type === 'string') {
      debugParams[param.name] = param.description || 'example_value'
    } else if (param.type === 'number' || param.type === 'integer') {
      debugParams[param.name] = 0
    } else if (param.type === 'boolean') {
      debugParams[param.name] = true
    } else if (param.type === 'array') {
      debugParams[param.name] = []
      debugParamsArray[param.name] = '[]'
    }
  })
  ElMessage.success('已填充示例参数')
}

const mcpSearchForm = reactive({ keyword: '' })

const mcpDialogVisible = ref(false)
const mcpDialogTitle = ref('')
const mcpFormRef = ref()
const isEditMCP = ref(false)

const mcpForm = reactive({
  id: null,
  name: '',
  code: '',
  transport_type: 'stdio',
  command: '',
  arguments_text: '',
  env_text: '',
  url: '',
  timeout: 30,
  status: 'active'
})

const mcpRules = {
  name: [{ required: true, message: '请输入MCP名称', trigger: 'blur' }]
}

// 辅助函数
function getTransportTypeText(type) {
  const map = {
    stdio: 'Stdio',
    sse: 'SSE'
  }
  return map[type] || type
}

function formatArguments(jsonStr) {
  if (!jsonStr) return '-'
  try {
    const arr = JSON.parse(jsonStr)
    if (Array.isArray(arr) && arr.length > 0) {
      return arr.join('\n')
    }
    return '-'
  } catch (e) {
    return '-'
  }
}

function formatEnv(jsonStr) {
  if (!jsonStr) return '-'
  try {
    const obj = JSON.parse(jsonStr)
    if (typeof obj === 'object' && obj !== null) {
      return Object.entries(obj)
        .map(([k, v]) => `${k}=${v}`)
        .join('\n')
    }
    return '-'
  } catch (e) {
    return '-'
  }
}

// 连接状态相关函数
function getConnectionStatusClass(mcp) {
  const status = mcpConnectionStatus.value[mcp.id] || 'unknown'
  const map = {
    online: 'online',
    offline: 'offline',
    unknown: 'unknown'
  }
  return map[status] || 'unknown'
}

function getConnectionStatusText(mcp) {
  const status = mcpConnectionStatus.value[mcp.id] || 'unknown'
  const map = {
    online: '在线',
    offline: '离线',
    unknown: '未知状态'
  }
  return map[status] || '未知状态'
}

function getStatusIcon(mcp) {
  const status = mcpConnectionStatus.value[mcp.id] || 'unknown'
  const iconMap = {
    online: SuccessFilled,
    offline: CircleCloseFilled,
    unknown: WarningFilled
  }
  return iconMap[status] || WarningFilled
}

async function checkMCPStatus(mcp) {
  try {
    const res = await mcpServerApi.testConnection(mcp.id)
    if (res.data?.success) {
      mcpConnectionStatus.value[mcp.id] = 'online'
    } else {
      mcpConnectionStatus.value[mcp.id] = 'offline'
    }
  } catch (e) {
    mcpConnectionStatus.value[mcp.id] = 'offline'
  }
}

async function checkAllMCPStatus() {
  checkingAll.value = true
  try {
    const enabledMCPs = mcpList.value.filter(m => m.is_enabled)
    for (const mcp of enabledMCPs) {
      await checkMCPStatus(mcp)
    }
    ElMessage.success('状态检测完成')
  } catch (e) {
    ElMessage.error('状态检测失败')
  } finally {
    checkingAll.value = false
  }
}

// 同步所有启用的 MCP Server
async function syncAllMCP() {
  syncingAll.value = true
  let successCount = 0
  let failCount = 0
  let totalTools = 0
  let totalResources = 0

  try {
    const enabledMCPs = mcpList.value.filter(m => m.is_enabled)

    for (const mcp of enabledMCPs) {
      try {
        const res = await mcpServerApi.sync(mcp.id)
        if (res.data) {
          successCount++
          totalTools += res.data.tools_synced || 0
          totalResources += res.data.resources_synced || 0
          mcpConnectionStatus.value[mcp.id] = 'online'
        }
      } catch (e) {
        failCount++
        mcpConnectionStatus.value[mcp.id] = 'offline'
      }
    }

    // 重新加载 MCP 列表以更新统计数据
    await loadMCPServers()

    ElMessage.success(`同步完成: ${successCount}个成功, ${failCount}个失败, 共${totalTools}个工具, ${totalResources}个资源`)
  } catch (e) {
    ElMessage.error('同步失败')
  } finally {
    syncingAll.value = false
  }
}

// MCP Server 操作
function selectMCP(mcp) {
  selectedMcpId.value = mcp.id
  detailTab.value = 'info'
  loadTools()
  loadResources()
  // 自动检测该 MCP Server 状态
  if (mcp.is_enabled) {
    checkMCPStatus(mcp)
  }
}

async function refreshMCPDetail() {
  if (!selectedMcpId.value) return
  detailLoading.value = true
  try {
    // 同步选中的 MCP Server
    const res = await mcpServerApi.sync(selectedMcpId.value)
    if (res.data) {
      ElMessage.success(`同步成功: ${res.data.tools_synced || 0}个工具, ${res.data.resources_synced || 0}个资源`)
    }
    // 重新加载数据
    await loadMCPServers()
    await loadTools()
    await loadResources()
  } catch (e) {
    ElMessage.error('同步失败')
  } finally {
    detailLoading.value = false
  }
}

async function loadTools() {
  if (!selectedMcpId.value) return
  toolsLoading.value = true
  try {
    const res = await mcpServerApi.getTools(selectedMcpId.value)
    tools.value = res.data?.tools || []
  } catch (e) {
    tools.value = []
  } finally {
    toolsLoading.value = false
  }
}

async function loadResources() {
  if (!selectedMcpId.value) return
  resourcesLoading.value = true
  try {
    const res = await mcpServerApi.getResources(selectedMcpId.value)
    resources.value = res.data?.resources || []
  } catch (e) {
    resources.value = []
  } finally {
    resourcesLoading.value = false
  }
}

function showToolDebug(tool) {
  detailTab.value = 'debug'
  debugForm.toolName = tool.name
  debugForm.paramsJson = '{}'
  paramsMode.value = 'form'
  onToolChange(tool.name)
}

function clearDebugResult() {
  debugResult.value = ''
}

async function invokeTool() {
  if (!debugForm.toolName) {
    ElMessage.warning('请选择工具')
    return
  }

  let params = {}

  // 根据模式获取参数
  if (paramsMode.value === 'form') {
    // 表单模式：验证并使用表单参数
    const errors = validateParams()
    if (errors.length > 0) {
      ElMessage.error(errors[0])
      return
    }

    // 收集有值的参数
    schemaParams.value.forEach(param => {
      const value = debugParams[param.name]
      if (value !== undefined && value !== null && value !== '') {
        params[param.name] = value
      }
    })
  } else {
    // JSON模式：解析JSON参数
    try {
      if (debugForm.paramsJson.trim()) {
        params = JSON.parse(debugForm.paramsJson)
        paramsJsonError.value = ''
      }
    } catch (e) {
      ElMessage.error('参数JSON格式错误')
      paramsJsonError.value = 'JSON格式错误: ' + e.message
      return
    }
  }

  debugInvoking.value = true
  try {
    const res = await mcpServerApi.invokeTool(selectedMcpId.value, debugForm.toolName, { params })
    debugResult.value = JSON.stringify(res.data, null, 2)
    ElMessage.success('调用成功')
    await loadMCPServers()
  } catch (e) {
    debugResult.value = JSON.stringify({ error: e.response?.data?.message || e.message || '调用失败' }, null, 2)
    ElMessage.error('调用失败')
  } finally {
    debugInvoking.value = false
  }
}

async function loadMCPServers() {
  const params = {}
  if (mcpSearchForm.keyword) params.keyword = mcpSearchForm.keyword

  const res = await mcpServerApi.getList(params)
  mcpList.value = res.data?.items || []

  // 初始化连接状态
  mcpList.value.forEach(mcp => {
    if (!mcpConnectionStatus.value[mcp.id]) {
      // 禁用的服务器直接标记为离线
      if (!mcp.is_enabled) {
        mcpConnectionStatus.value[mcp.id] = 'offline'
      } else {
        // 启用的服务器标记为未知，等待用户点击刷新检查
        mcpConnectionStatus.value[mcp.id] = 'unknown'
      }
    }
  })

  // 如果没有选中的 MCP Server 且列表不为空，自动选中第一个
  if (!selectedMcpId.value && mcpList.value.length > 0) {
    selectMCP(mcpList.value[0])
  }
}

async function handleToggleMCPStatus(row, newStatus) {
  const action = newStatus ? '启用' : '禁用'
  try {
    await mcpServerApi.update(row.id, { is_enabled: newStatus })
    ElMessage.success(`${action}成功`)

    // 更新本地状态
    mcpConnectionStatus.value[row.id] = newStatus ? 'unknown' : 'offline'

    // 如果是启用操作，立即同步一次以获取工具和确认连接
    if (newStatus) {
      try {
        await mcpServerApi.sync(row.id)
        mcpConnectionStatus.value[row.id] = 'online'
      } catch (e) {
        mcpConnectionStatus.value[row.id] = 'offline'
      }
    }

    await loadMCPServers()
  } catch (e) {
    ElMessage.error(`${action}失败`)
  }
}

function handleCreateMCP() {
  isEditMCP.value = false
  mcpDialogTitle.value = '新建MCP Server'
  Object.assign(mcpForm, {
    id: null,
    name: '',
    code: '',
    transport_type: 'stdio',
    command: '',
    arguments_text: '',
    env_text: '',
    url: '',
    timeout: 30,
    status: 'active'
  })
  mcpDialogVisible.value = true
}

function handleEditMCP(row) {
  isEditMCP.value = true
  mcpDialogTitle.value = '编辑MCP Server'

  let argumentsText = ''
  if (row.arguments) {
    try {
      const parsed = JSON.parse(row.arguments)
      if (Array.isArray(parsed) && parsed.length > 0) {
        argumentsText = parsed.join('\n')
      }
    } catch (e) {
    }
  }

  let envText = ''
  if (row.env) {
    try {
      const parsed = JSON.parse(row.env)
      if (typeof parsed === 'object' && parsed !== null) {
        envText = Object.entries(parsed)
          .map(([key, value]) => `${key}=${value}`)
          .join('\n')
      }
    } catch (e) {
    }
  }

  Object.assign(mcpForm, {
    id: row.id,
    name: row.name,
    code: row.code,
    transport_type: row.transport_type,
    command: row.command || '',
    arguments_text: argumentsText,
    env_text: envText,
    url: row.url || '',
    timeout: row.timeout,
    status: row.status
  })
  mcpDialogVisible.value = true
}

function handleDeleteMCP(row) {
  ElMessageBox.confirm('确定要删除这个MCP Server吗？', '提示', { type: 'warning' })
    .then(() => mcpServerApi.delete(row.id))
    .then(() => {
      ElMessage.success('删除成功')
      if (selectedMcpId.value === row.id) {
        selectedMcpId.value = null
        tools.value = []
        resources.value = []
      }
      loadMCPServers()
    })
}

function handleSubmitMCP() {
  mcpFormRef.value.validate((valid) => {
    if (valid) {
      const data = { ...mcpForm }
      delete data.arguments_text
      delete data.env_text

      const argsText = mcpForm.arguments_text?.trim()
      if (argsText && argsText !== '') {
        data.arguments = argsText
          .split('\n')
          .map(line => line.trim())
          .filter(line => line !== '')
      } else {
        data.arguments = null
      }

      const envText = mcpForm.env_text?.trim()
      if (envText && envText !== '') {
        const envObj = {}
        envText.split('\n').forEach(line => {
          line = line.trim()
          if (line) {
            const eqIndex = line.indexOf('=')
            if (eqIndex > 0) {
              const key = line.substring(0, eqIndex).trim()
              const value = line.substring(eqIndex + 1).trim()
              if (key) {
                envObj[key] = value
              }
            }
          }
        })
        data.env = Object.keys(envObj).length > 0 ? envObj : null
      } else {
        data.env = null
      }

      const api = isEditMCP.value ? mcpServerApi.update : mcpServerApi.create
      if (isEditMCP.value) {
        api(data.id, data).then(() => {
          ElMessage.success('更新成功')
          mcpDialogVisible.value = false
          loadMCPServers()
        })
      } else {
        api(data).then(() => {
          ElMessage.success('创建成功')
          mcpDialogVisible.value = false
          loadMCPServers()
        })
      }
    }
  })
}

onMounted(() => {
  loadMCPServers()
})
</script>

<style scoped>
.icon-rotate {
  transform: rotate(-90deg);
  transition: transform 0.3s;
}

.mcp-servers-page {
  padding: var(--space-6);
  height: 100%;
  overflow-y: auto;
}

.mcp-servers-page :deep(.el-card) {
  background: var(--color-surface);
  border: none;
  border-radius: var(--radius-lg);
  box-shadow: none;
}

.mcp-servers-page :deep(.el-card__body) {
  padding: var(--space-5);
}

/* 状态统计面板 */
.status-panel {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2) var(--space-3);
  background: var(--color-fill-bg, #f9fafb);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-3);
}

.status-panel .stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.status-panel .stat-label {
  font-size: 12px;
}

.status-panel .stat-total {
  font-size: 12px;
  font-weight: 500;
}

.stat-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.stat-dot.online {
  background-color: #67c23a;
}

.stat-dot.offline {
  background-color: #f56c6c;
}

.stat-dot.unknown {
  background-color: #909399;
}

.stat-label {
  font-size: 13px;
  color: var(--color-text-secondary, #6b7280);
}

.stat-total {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-primary, #303133);
}

/* MCP Server 左右布局 */
.mcp-server-layout {
  display: flex;
  gap: var(--space-4);
  height: 600px;
}

/* 左侧列表 */
.mcp-server-list {
  width: 320px;
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--color-border, #e5e7eb);
  padding-right: var(--space-4);
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-3);
}

.list-title {
  font-size: 16px;
  font-weight: 600;
}

.list-search {
  margin-bottom: var(--space-3);
}

.list-items {
  flex: 1;
  overflow-y: auto;
}

.list-item {
  padding: var(--space-3);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background-color 0.2s;
  margin-bottom: var(--space-2);
  border: 1px solid transparent;
}

.list-item:hover {
  background-color: var(--color-hover-bg, #f3f4f6);
}

.list-item.active {
  background-color: var(--color-primary-bg, #e0f2fe);
  border-color: var(--color-primary, #3b82f6);
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-2);
}

.item-left {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.status-icon {
  font-size: 14px;
  flex-shrink: 0;
}

.status-icon.online {
  color: var(--el-color-success);
}

.status-icon.offline {
  color: var(--el-color-danger);
}

.status-icon.unknown {
  color: var(--el-color-warning);
}

.item-name {
  font-weight: 500;
}

.item-tags {
  display: flex;
  gap: var(--space-2);
}

.item-info {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: 12px;
  color: var(--color-text-secondary, #6b7280);
}

.item-command {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 180px;
}

.item-tools-count {
  margin-left: auto;
  font-size: 12px;
  color: var(--color-text-secondary, #6b7280);
}

/* Switch 开关样式 */
.item-tags :deep(.el-switch) {
  --el-switch-border-color: transparent;
}

.item-tags :deep(.el-switch__core) {
  border: none;
  border-radius: 10px;
}

.item-tags :deep(.el-switch__action) {
  border-radius: 50%;
}

/* 右侧详情 */
.mcp-server-detail {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.detail-empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.detail-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--color-border, #e5e7eb);
  margin-bottom: var(--space-4);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.detail-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: var(--space-2);
}

.detail-tabs {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.detail-tabs :deep(.el-tabs__content) {
  flex: 1;
  overflow-y: auto;
}

/* 信息展示 */
.info-section {
  padding: var(--space-4);
}

.info-row {
  display: flex;
  padding: var(--space-2) 0;
  border-bottom: 1px solid var(--color-border-light, #f3f4f6);
}

.info-row:last-child {
  border-bottom: none;
}

.label {
  width: 120px;
  color: var(--color-text-secondary, #6b7280);
  flex-shrink: 0;
}

.value {
  flex: 1;
}

.value.code {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  white-space: pre-wrap;
  word-break: break-all;
}

/* 工具列表 */
.tools-section,
.resources-section {
  padding: var(--space-4);
}

.tools-header,
.resources-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-3);
  font-weight: 500;
}

.tool-item,
.resource-item {
  padding: var(--space-3);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-3);
}

.tool-header,
.resource-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-2);
}

.tool-name,
.resource-name {
  font-weight: 500;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
}

.tool-description,
.resource-description {
  color: var(--color-text-secondary, #6b7280);
  font-size: 13px;
}

.resource-uri {
  font-size: 12px;
  color: var(--color-text-tertiary, #9ca3af);
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  margin-top: var(--space-1);
}

/* 调试面板 */
.debug-section {
  padding: var(--space-4);
}

.debug-header {
  font-weight: 500;
  margin-bottom: var(--space-3);
}

.debug-tool-selector {
  margin-bottom: var(--space-4);
}

.debug-tool-info {
  margin-bottom: var(--space-4);
}

.tool-info-card {
  padding: var(--space-4);
  background: var(--color-fill-bg, #f9fafb);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: var(--radius-md);
}

.tool-info-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-2);
}

.tool-info-title {
  font-size: 16px;
  font-weight: 600;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
}

.tool-info-description {
  color: var(--color-text-secondary, #6b7280);
  margin-bottom: var(--space-3);
  line-height: 1.6;
}

.schema-title {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: var(--space-2);
  color: var(--color-text-primary, #303133);
}

.schema-params-table {
  margin-top: var(--space-3);
}

.no-params {
  padding: var(--space-2);
  text-align: center;
}

.debug-params-form {
  margin-bottom: var(--space-4);
}

.params-form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-2);
  font-weight: 500;
}

.params-form-content {
  padding: var(--space-4);
  background: var(--color-fill-bg, #f9fafb);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: var(--radius-md);
}

.params-json-content {
  margin-bottom: var(--space-2);
}

.params-json-error {
  margin-top: var(--space-2);
}

.debug-actions {
  display: flex;
  gap: var(--space-2);
  margin-top: var(--space-2);
}

.debug-result {
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.result-header {
  padding: var(--space-2) var(--space-3);
  background: var(--color-fill-bg, #f9fafb);
  border-bottom: 1px solid var(--color-border, #e5e7eb);
  font-weight: 500;
  font-size: 14px;
}

.result-content {
  padding: var(--space-3);
  margin: 0;
  background: var(--color-fill-bg, #f9fafb);
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  max-height: 300px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-all;
}

/* Code editor */
.code-editor {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
}

.code-editor :deep(textarea) {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
}

/* Error and tip messages */
.json-error {
  color: var(--color-error, #f56c6c);
  font-size: 12px;
  margin-top: 4px;
}

.form-tip {
  color: var(--color-text-secondary, #909399);
  font-size: 12px;
  margin-top: 4px;
}
</style>

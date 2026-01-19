<template>
  <div class="test-case-page">
    <div class="page-layout" ref="layoutRef">
      <!-- 左侧目录树 -->
      <div class="suite-sidebar" :style="{ width: sidebarWidth + 'px' }">
        <div class="suite-header">
          <span>目录</span>
          <el-dropdown trigger="click" @command="handleSuiteCommand">
            <el-button type="primary" link size="small">
              <el-icon><Plus /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="add">新建目录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
        <el-tree
          ref="treeRef"
          :data="suiteTree"
          :props="treeProps"
          :highlight-current="true"
          node-key="id"
          default-expand-all
          @node-click="handleNodeClick"
        >
          <template #default="{ node, data }">
            <div class="tree-node">
              <div class="node-content">
                <el-icon class="folder-icon"><Folder /></el-icon>
                <span class="node-label">{{ node.label }}</span>
                <span class="node-count">({{ data.case_count || 0 }})</span>
              </div>
              <el-dropdown trigger="click" @command="(cmd) => handleSuiteAction(cmd, data)">
                <el-icon class="node-more" @click.stop><MoreFilled /></el-icon>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="addSub">添加子目录</el-dropdown-item>
                    <el-dropdown-item command="edit">编辑</el-dropdown-item>
                    <el-dropdown-item command="delete">删除</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </template>
        </el-tree>
      </div>

      <!-- 拖拽分隔条 -->
      <div
        class="resize-handle"
        @mousedown="handleMouseDown"
      ></div>

      <!-- 右侧内容区 -->
      <div class="content-area">
        <el-card>
          <div class="toolbar">
            <el-input
              v-model="searchForm.keyword"
              placeholder="搜索用例"
              clearable
              style="width: 200px"
              @change="loadCases"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-select v-model="searchForm.priority" placeholder="优先级" clearable @change="loadCases">
              <el-option label="紧急" value="critical" />
              <el-option label="高" value="high" />
              <el-option label="中" value="medium" />
              <el-option label="低" value="low" />
            </el-select>
            <el-select v-model="searchForm.status" placeholder="状态" clearable @change="loadCases">
              <el-option label="草稿" value="draft" />
              <el-option label="激活" value="active" />
              <el-option label="归档" value="archived" />
            </el-select>
            <el-button :icon="Search" @click="showAdvancedSearch = true">高级搜索</el-button>
            <div style="flex: 1"></div>
            <el-button type="primary" :icon="Plus" @click="handleCreateCase">新建用例</el-button>
            <el-button
              v-if="selectedCases.length > 0"
              type="danger"
              @click="handleBatchDelete"
            >
              批量删除 ({{ selectedCases.length }})
            </el-button>
            <el-button
              v-if="selectedCases.length > 0"
              @click="handleBatchMove"
            >
              批量移动
            </el-button>
          </div>

          <el-table
            :data="caseList"
            @selection-change="handleSelectionChange"
            style="width: 100%"
          >
            <el-table-column type="selection" width="55" />
            <el-table-column label="编号" width="120">
              <template #default="{ row }">
                {{ row.case_no || `CASE-${row.id}` }}
              </template>
            </el-table-column>
            <el-table-column prop="name" label="用例名称" show-overflow-tooltip />
            <el-table-column prop="priority" label="优先级" width="100">
              <template #default="{ row }">
                <el-tag :type="getPriorityType(row.priority)">{{ row.priority }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="case_type" label="类型" width="100">
              <template #default="{ row }">
                <el-tag type="info">{{ row.case_type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="automation_status" label="自动化" width="100">
              <template #default="{ row }">
                <el-tag :type="row.automation_status === 'automated' ? 'success' : 'info'">
                  {{ row.automation_status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-tooltip content="查看" placement="top">
                  <el-button type="info" link size="small" @click="handleView(row)">
                    <el-icon><View /></el-icon>
                  </el-button>
                </el-tooltip>
                <el-tooltip content="执行" placement="top">
                  <el-button type="success" link size="small" @click="handleExecute(row)">
                    <el-icon><VideoPlay /></el-icon>
                  </el-button>
                </el-tooltip>
                <el-tooltip content="AI执行" placement="top">
                  <el-button type="warning" link size="small" @click="handleAIExecute(row)">
                    <el-icon><MagicStick /></el-icon>
                  </el-button>
                </el-tooltip>
                <el-tooltip content="编辑" placement="top">
                  <el-button type="primary" link size="small" @click="handleEdit(row)">
                    <el-icon><Edit /></el-icon>
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
            @current-change="loadCases"
            @size-change="loadCases"
            style="margin-top: 20px; justify-content: flex-end"
          />
        </el-card>
      </div>
    </div>

    <!-- 用例表单对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="900px"
      destroy-on-close
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="用例名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入用例名称" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="用例编号" prop="case_no">
              <el-input v-model="form.case_no" placeholder="自动生成" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="所属目录" prop="suite_id">
              <el-tree-select
                v-model="form.suite_id"
                :data="suiteOptions"
                :props="{ value: 'id', label: 'name', children: 'children' }"
                check-strictly
                clearable
                placeholder="请选择目录"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="优先级" prop="priority">
              <el-select v-model="form.priority" style="width: 100%">
                <el-option label="紧急" value="critical" />
                <el-option label="高" value="high" />
                <el-option label="中" value="medium" />
                <el-option label="低" value="low" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="用例类型" prop="case_type">
              <el-select v-model="form.case_type" style="width: 100%">
                <el-option label="功能测试" value="functional" />
                <el-option label="性能测试" value="performance" />
                <el-option label="安全测试" value="security" />
                <el-option label="UI测试" value="ui" />
                <el-option label="API测试" value="api" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="自动化状态" prop="automation_status">
              <el-select v-model="form.automation_status" style="width: 100%">
                <el-option label="手工" value="manual" />
                <el-option label="自动化" value="automated" />
                <el-option label="半自动化" value="semi-automated" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="状态" prop="status">
              <el-select v-model="form.status" style="width: 100%">
                <el-option label="草稿" value="draft" />
                <el-option label="激活" value="active" />
                <el-option label="归档" value="archived" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="前置条件" prop="preconditions">
          <el-input v-model="form.preconditions" type="textarea" :rows="2" placeholder="测试执行前需要满足的条件..." />
        </el-form-item>

        <!-- 测试步骤表格 -->
        <el-form-item label="测试步骤" prop="stepList">
          <div class="steps-table-wrapper">
            <el-table :data="form.stepList" border style="width: 100%">
              <el-table-column label="序号" width="60" align="center">
                <template #default="{ $index }">
                  <span>{{ $index + 1 }}</span>
                </template>
              </el-table-column>
              <el-table-column label="步骤描述" min-width="200">
                <template #default="{ row }">
                  <el-input
                    v-model="row.step"
                    type="textarea"
                    :rows="2"
                    placeholder="请输入步骤描述"
                    @blur="handleStepChange"
                  />
                </template>
              </el-table-column>
              <el-table-column label="期望结果" min-width="200">
                <template #default="{ row }">
                  <el-input
                    v-model="row.expected"
                    type="textarea"
                    :rows="2"
                    placeholder="请输入期望结果"
                    @blur="handleStepChange"
                  />
                </template>
              </el-table-column>
              <el-table-column label="操作" width="80" align="center">
                <template #default="{ $index }">
                  <el-button
                    type="danger"
                    link
                    :icon="Delete"
                    @click="removeStep($index)"
                    :disabled="form.stepList.length <= 1"
                  >
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            <el-button
              type="primary"
              :icon="Plus"
              @click="addStep"
              style="margin-top: 10px"
            >
              添加步骤
            </el-button>
          </div>
        </el-form-item>

        <el-form-item label="后置条件" prop="postconditions">
          <el-input v-model="form.postconditions" type="textarea" :rows="2" placeholder="测试执行后的清理或恢复操作..." />
        </el-form-item>

        <el-form-item label="备注" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="其他说明..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 目录表单对话框 -->
    <el-dialog v-model="suiteDialogVisible" :title="suiteDialogTitle" width="500px">
      <el-form :model="suiteForm" :rules="suiteRules" ref="suiteFormRef" label-width="100px">
        <el-form-item label="目录名称" prop="name">
          <el-input v-model="suiteForm.name" placeholder="请输入目录名称" />
        </el-form-item>
        <el-form-item label="父目录" prop="parent_id">
          <el-tree-select
            v-model="suiteForm.parent_id"
            :data="suiteOptions"
            :props="{ value: 'id', label: 'name', children: 'children' }"
            check-strictly
            clearable
            placeholder="请选择父目录"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="suiteDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSuiteSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 查看用例对话框 -->
    <el-dialog
      v-model="viewDialogVisible"
      title="查看用例"
      width="900px"
      destroy-on-close
    >
      <div v-if="viewCase" class="case-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="用例编号">{{ viewCase.case_no || `CASE-${viewCase.id}` }}</el-descriptions-item>
          <el-descriptions-item label="用例名称">{{ viewCase.name }}</el-descriptions-item>
          <el-descriptions-item label="优先级">
            <el-tag :type="getPriorityType(viewCase.priority)">{{ viewCase.priority }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="用例类型">
            <el-tag type="info">{{ viewCase.case_type }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="自动化状态">
            <el-tag :type="viewCase.automation_status === 'automated' ? 'success' : 'info'">
              {{ viewCase.automation_status }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(viewCase.status)">{{ viewCase.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间" :span="2">
            {{ viewCase.created_at ? new Date(viewCase.created_at).toLocaleString() : '-' }}
          </el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left">前置条件</el-divider>
        <div class="detail-content">
          {{ viewCase.preconditions || '无' }}
        </div>

        <el-divider content-position="left">测试步骤</el-divider>
        <el-table :data="getStepList(viewCase.steps)" border style="width: 100%">
          <el-table-column label="序号" width="60" align="center">
            <template #default="{ $index }">
              <span>{{ $index + 1 }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="step" label="步骤描述" />
          <el-table-column prop="expected" label="期望结果" />
        </el-table>

        <el-divider content-position="left">后置条件</el-divider>
        <div class="detail-content">
          {{ viewCase.postconditions || '无' }}
        </div>

        <el-divider content-position="left">备注</el-divider>
        <div class="detail-content">
          {{ viewCase.description || '无' }}
        </div>
      </div>
      <template #footer>
        <el-button type="primary" @click="viewDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 执行用例对话框 -->
    <el-dialog
      v-model="executeDialogVisible"
      title="执行用例"
      width="900px"
      destroy-on-close
    >
      <div v-if="executeCase" class="case-execute">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="用例编号">{{ executeCase.case_no || `CASE-${executeCase.id}` }}</el-descriptions-item>
          <el-descriptions-item label="用例名称">{{ executeCase.name }}</el-descriptions-item>
          <el-descriptions-item label="优先级">
            <el-tag :type="getPriorityType(executeCase.priority)">{{ executeCase.priority }}</el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left">前置条件</el-divider>
        <div class="detail-content">
          {{ executeCase.preconditions || '无' }}
        </div>

        <el-divider content-position="left">测试步骤</el-divider>
        <el-table :data="getStepList(executeCase.steps)" border style="width: 100%">
          <el-table-column label="序号" width="60" align="center">
            <template #default="{ $index }">
              <span>{{ $index + 1 }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="step" label="步骤描述" />
          <el-table-column prop="expected" label="期望结果" />
        </el-table>

        <el-divider content-position="left">执行结果</el-divider>
        <el-form :model="executeForm" label-width="100px">
          <el-form-item label="执行状态" prop="status" required>
            <el-radio-group v-model="executeForm.status">
              <el-radio label="passed">通过</el-radio>
              <el-radio label="failed">失败</el-radio>
              <el-radio label="blocked">阻塞</el-radio>
              <el-radio label="skipped">跳过</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="实际结果">
            <el-input
              v-model="executeForm.actual_result"
              type="textarea"
              :rows="4"
              placeholder="请输入实际执行结果..."
            />
          </el-form-item>

          <el-form-item label="备注">
            <el-input
              v-model="executeForm.notes"
              type="textarea"
              :rows="3"
              placeholder="其他备注信息..."
            />
          </el-form-item>

          <el-form-item label="执行时长(秒)">
            <el-input-number
              v-model="executeForm.duration"
              :min="0"
              :max="99999"
              placeholder="执行时长"
            />
          </el-form-item>

          <el-form-item label="关联缺陷">
            <div style="display: flex; gap: 8px; width: 100%">
              <el-select
                v-model="executeForm.defect_ids"
                multiple
                filterable
                placeholder="选择已有缺陷"
                style="flex: 1"
              >
                <el-option
                  v-for="defect in defectList"
                  :key="defect.id"
                  :label="`${defect.defect_no || `DEF-${defect.id}`} - ${defect.title}`"
                  :value="defect.id"
                />
              </el-select>
              <el-button type="primary" @click="handleCreateDefect">创建缺陷</el-button>
            </div>
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="executeDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="executing" @click="handleSubmitExecution">提交执行结果</el-button>
      </template>
    </el-dialog>

    <!-- 选择执行环境对话框 -->
    <el-dialog v-model="envDialogVisible" title="选择执行环境" width="500px" destroy-on-close>
      <el-form label-width="100px">
        <el-form-item label="执行环境" required>
          <el-select v-model="selectedEnvironmentId" placeholder="请选择执行环境" style="width: 100%">
            <el-option
              v-for="env in environmentList"
              :key="env.id"
              :label="`${env.name} (${env.url || env.base_url})`"
              :value="env.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="envDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmAIExecute">确定</el-button>
      </template>
    </el-dialog>

    <!-- 高级搜索对话框 -->
    <el-dialog v-model="showAdvancedSearch" title="高级搜索" width="700px" destroy-on-close>
      <el-form :model="advancedSearchForm" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="用例编号">
              <el-input v-model="advancedSearchForm.case_no" placeholder="如: CASE-0001" clearable />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="用例名称">
              <el-input v-model="advancedSearchForm.name" placeholder="输入用例名称" clearable />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="优先级">
              <el-select v-model="advancedSearchForm.priority" placeholder="选择优先级" clearable style="width: 100%">
                <el-option label="紧急" value="critical" />
                <el-option label="高" value="high" />
                <el-option label="中" value="medium" />
                <el-option label="低" value="low" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-select v-model="advancedSearchForm.status" placeholder="选择状态" clearable style="width: 100%">
                <el-option label="草稿" value="draft" />
                <el-option label="激活" value="active" />
                <el-option label="归档" value="archived" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="用例类型">
              <el-select v-model="advancedSearchForm.case_type" placeholder="选择类型" clearable style="width: 100%">
                <el-option label="功能测试" value="functional" />
                <el-option label="性能测试" value="performance" />
                <el-option label="安全测试" value="security" />
                <el-option label="UI测试" value="ui" />
                <el-option label="API测试" value="api" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="自动化状态">
              <el-select v-model="advancedSearchForm.automation_status" placeholder="选择状态" clearable style="width: 100%">
                <el-option label="手工" value="manual" />
                <el-option label="自动化" value="automated" />
                <el-option label="半自动化" value="semi-automated" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="创建时间">
              <el-date-picker
                v-model="advancedSearchForm.created_at"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="更新时间">
              <el-date-picker
                v-model="advancedSearchForm.updated_at"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="关键词">
          <el-input v-model="advancedSearchForm.keyword" placeholder="搜索用例名称、编号、步骤、期望结果" clearable />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="handleResetAdvancedSearch">重置</el-button>
        <el-button @click="showAdvancedSearch = false">取消</el-button>
        <el-button type="primary" @click="handleAdvancedSearch">搜索</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Delete, Folder, View, VideoPlay, MagicStick, Edit, MoreFilled, Search
} from '@element-plus/icons-vue'
import { useTestCaseStore } from '@/store/test-case'
import { useProjectStore } from '@/store/project'
import { defectApi } from '@/api/defect'
import { environmentApi } from '@/api/environment'

const router = useRouter()

const testCaseStore = useTestCaseStore()
const projectStore = useProjectStore()
const treeRef = ref()
const formRef = ref()
const suiteFormRef = ref()
const layoutRef = ref()

// 侧边栏宽度相关
const sidebarWidth = ref(250)
const minWidth = 180
const maxWidth = 500
const isResizing = ref(false)

// 从 localStorage 恢复宽度
const savedWidth = localStorage.getItem('test-case-sidebar-width')
if (savedWidth) {
  sidebarWidth.value = parseInt(savedWidth)
}

// 监听宽度变化并保存
watch(sidebarWidth, (newWidth) => {
  localStorage.setItem('test-case-sidebar-width', newWidth.toString())
})

// 鼠标按下开始拖拽
function handleMouseDown(e) {
  isResizing.value = true
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
  document.body.style.cursor = 'col-resize'
  document.body.style.userSelect = 'none'
}

// 鼠标移动
function handleMouseMove(e) {
  if (!isResizing.value || !layoutRef.value) return

  const rect = layoutRef.value.getBoundingClientRect()
  const newWidth = e.clientX - rect.left

  // 限制宽度范围
  if (newWidth >= minWidth && newWidth <= maxWidth) {
    sidebarWidth.value = newWidth
  }
}

// 鼠标释放
function handleMouseUp() {
  isResizing.value = false
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
  document.body.style.cursor = ''
  document.body.style.userSelect = ''
}

// 当前项目ID
const currentProjectId = computed(() => projectStore.currentProject?.id)

const suiteTree = ref([])
const suiteOptions = ref([])
const caseList = ref([])
const selectedCases = ref([])
const currentSuiteId = ref(null)

const dialogVisible = ref(false)
const dialogTitle = ref('')
const isEdit = ref(false)

// 目录相关
const suiteDialogVisible = ref(false)
const suiteDialogTitle = ref('')
const isSuiteEdit = ref(false)
const suiteForm = reactive({
  id: null,
  name: '',
  parent_id: null
})

const suiteRules = {
  name: [{ required: true, message: '请输入目录名称', trigger: 'blur' }]
}

const treeProps = {
  children: 'children',
  label: 'name',
  value: 'id'
}

const currentSuiteName = computed(() => {
  if (currentSuiteId.value === null) return '全部测试用例'
  const findName = (tree, id) => {
    for (const item of tree) {
      if (item.id === id) return item.name
      if (item.children) {
        const found = findName(item.children, id)
        if (found) return found
      }
    }
    return ''
  }
  return findName(suiteTree.value, currentSuiteId.value) || '当前目录'
})

// 查看和执行相关
const viewDialogVisible = ref(false)
const viewCase = ref(null)
const executeDialogVisible = ref(false)
const executeCase = ref(null)
const executing = ref(false)

const executeForm = reactive({
  status: 'passed',
  actual_result: '',
  notes: '',
  duration: 0,
  defect_ids: []
})

// 缺陷列表
const defectList = ref([])

// 环境选择相关
const envDialogVisible = ref(false)
const environmentList = ref([])
const selectedEnvironmentId = ref(null)
const pendingAIExecuteCase = ref(null)

// 高级搜索
const showAdvancedSearch = ref(false)
const advancedSearchForm = reactive({
  case_no: '',
  name: '',
  priority: '',
  status: '',
  case_type: '',
  automation_status: '',
  keyword: '',
  created_at: null,
  updated_at: null
})

const searchForm = reactive({
  keyword: '',
  priority: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const form = reactive({
  id: null,
  name: '',
  case_no: '',
  suite_id: null,
  preconditions: '',
  postconditions: '',
  stepList: [{ step: '', expected: '' }],
  steps: '',
  expected_result: '',
  description: '',
  priority: 'medium',
  case_type: 'functional',
  automation_status: 'manual',
  status: 'draft'
})

const rules = {
  name: [{ required: true, message: '请输入用例名称', trigger: 'blur' }]
}

function getPriorityType(priority) {
  const map = { critical: 'danger', high: 'warning', medium: 'primary', low: 'info' }
  return map[priority] || 'info'
}

function getStatusType(status) {
  const map = { draft: 'info', active: 'success', archived: 'warning' }
  return map[status] || 'info'
}

async function loadSuites() {
  const res = await testCaseStore.fetchSuites({
    project_id: currentProjectId.value
  })
  suiteTree.value = res.data || []
  suiteOptions.value = buildOptions(suiteTree.value)
}

function buildOptions(tree) {
  const options = []
  for (const node of tree) {
    options.push({
      id: node.id,
      name: node.name,
      children: node.children?.length ? buildOptions(node.children) : undefined
    })
  }
  return options
}

function handleNodeClick(data) {
  currentSuiteId.value = data.id
  testCaseStore.setCurrentSuite(data)
  pagination.page = 1
  loadCases()
}

// 目录操作命令
function handleSuiteCommand(command) {
  if (command === 'add') {
    handleAddSuite()
  }
}

function handleSuiteAction(command, data) {
  if (command === 'addSub') {
    handleAddSuite(data.id)
  } else if (command === 'edit') {
    handleEditSuite(data)
  } else if (command === 'delete') {
    handleDeleteSuite(data)
  }
}

// 添加目录
function handleAddSuite(parentId = null) {
  isSuiteEdit.value = false
  suiteDialogTitle.value = parentId ? '新建子目录' : '新建目录'
  Object.assign(suiteForm, {
    id: null,
    name: '',
    parent_id: parentId
  })
  suiteDialogVisible.value = true
}

// 编辑目录
function handleEditSuite(data) {
  isSuiteEdit.value = true
  suiteDialogTitle.value = '编辑目录'
  Object.assign(suiteForm, {
    id: data.id,
    name: data.name,
    parent_id: data.parent_id
  })
  suiteDialogVisible.value = true
}

// 删除目录
function handleDeleteSuite(data) {
  ElMessageBox.confirm('确定要删除这个目录吗？删除后目录下的测试用例将变为无目录状态。', '提示', {
    type: 'warning'
  }).then(() => {
    testCaseStore.deleteSuite(data.id).then(() => {
      ElMessage.success('删除成功')
      loadSuites()
      if (currentSuiteId.value === data.id) {
        currentSuiteId.value = null
        testCaseStore.setCurrentSuite(null)
      }
    })
  })
}

// 提交目录表单
function handleSuiteSubmit() {
  suiteFormRef.value.validate((valid) => {
    if (valid) {
      const data = {
        ...suiteForm,
        project_id: currentProjectId.value
      }
      const api = isSuiteEdit.value ? testCaseStore.updateSuite : testCaseStore.createSuite
      const params = isSuiteEdit.value ? suiteForm.id : data
      api(params, isSuiteEdit.value ? data : null).then(() => {
        ElMessage.success(isSuiteEdit.value ? '更新成功' : '创建成功')
        suiteDialogVisible.value = false
        loadSuites()
      })
    }
  })
}

async function loadCases() {
  const params = {
    page: pagination.page,
    per_page: pagination.pageSize,
    suite_id: currentSuiteId.value,
    project_id: currentProjectId.value
  }

  // 基本搜索：只搜索名称
  if (searchForm.keyword) {
    params.name = searchForm.keyword
  }
  // 优先级和状态筛选
  if (searchForm.priority) {
    params.priority = searchForm.priority
  }
  if (searchForm.status) {
    params.status = searchForm.status
  }

  const res = await testCaseStore.fetchCases(params)
  caseList.value = res.data?.items || []
  pagination.total = res.data?.total || 0
}

// 高级搜索处理
function handleAdvancedSearch() {
  // 构建搜索参数
  const params = {
    page: 1,
    per_page: pagination.pageSize,
    suite_id: currentSuiteId.value,
    project_id: currentProjectId.value
  }

  // 添加高级搜索条件
  if (advancedSearchForm.case_no) {
    params.case_no = advancedSearchForm.case_no
  }
  if (advancedSearchForm.name) {
    params.name = advancedSearchForm.name
  }
  if (advancedSearchForm.priority) {
    params.priority = advancedSearchForm.priority
  }
  if (advancedSearchForm.status) {
    params.status = advancedSearchForm.status
  }
  if (advancedSearchForm.case_type) {
    params.case_type = advancedSearchForm.case_type
  }
  if (advancedSearchForm.automation_status) {
    params.automation_status = advancedSearchForm.automation_status
  }
  if (advancedSearchForm.keyword) {
    params.keyword = advancedSearchForm.keyword
  }
  if (advancedSearchForm.created_at && advancedSearchForm.created_at.length === 2) {
    params.created_after = advancedSearchForm.created_at[0]
    params.created_before = advancedSearchForm.created_at[1]
  }
  if (advancedSearchForm.updated_at && advancedSearchForm.updated_at.length === 2) {
    params.updated_after = advancedSearchForm.updated_at[0]
    params.updated_before = advancedSearchForm.updated_at[1]
  }

  // 同步到基本搜索的显示
  searchForm.keyword = advancedSearchForm.name || advancedSearchForm.keyword || ''
  searchForm.priority = advancedSearchForm.priority || ''
  searchForm.status = advancedSearchForm.status || ''

  pagination.page = 1
  testCaseStore.fetchCases(params).then(res => {
    caseList.value = res.data?.items || []
    pagination.total = res.data?.total || 0
    showAdvancedSearch.value = false
  })
}

// 重置高级搜索
function handleResetAdvancedSearch() {
  Object.assign(advancedSearchForm, {
    case_no: '',
    name: '',
    priority: '',
    status: '',
    case_type: '',
    automation_status: '',
    keyword: '',
    created_at: null,
    updated_at: null
  })
  searchForm.keyword = ''
  searchForm.priority = ''
  searchForm.status = ''
  pagination.page = 1
  loadCases()
}

function handleSelectionChange(selection) {
  selectedCases.value = selection.map(item => item.id)
}

function handleCreateCase() {
  isEdit.value = false
  dialogTitle.value = '新建测试用例'
  Object.assign(form, {
    id: null,
    name: '',
    case_no: '',
    suite_id: currentSuiteId.value,
    preconditions: '',
    postconditions: '',
    stepList: [{ step: '', expected: '' }],
    steps: '',
    expected_result: '',
    description: '',
    priority: 'medium',
    case_type: 'functional',
    automation_status: 'manual',
    status: 'draft'
  })
  dialogVisible.value = true
}

function handleEdit(row) {
  isEdit.value = true
  dialogTitle.value = '编辑测试用例'

  // 解析steps数据
  let stepList = [{ step: '', expected: '' }]
  if (row.steps) {
    try {
      const parsed = JSON.parse(row.steps)
      if (Array.isArray(parsed)) {
        stepList = parsed.map(item => ({
          step: item.step || '',
          expected: item.expected || ''
        }))
      }
    } catch {
      stepList = [{ step: row.steps || '', expected: row.expected_result || '' }]
    }
  }

  Object.assign(form, {
    id: row.id,
    name: row.name,
    case_no: row.case_no,
    suite_id: row.suite_id,
    preconditions: row.preconditions || '',
    postconditions: row.postconditions || '',
    stepList: stepList,
    steps: row.steps,
    expected_result: row.expected_result || '',
    description: row.description || '',
    priority: row.priority,
    case_type: row.case_type,
    automation_status: row.automation_status,
    status: row.status
  })
  dialogVisible.value = true
}

function handleDelete(row) {
  ElMessageBox.confirm('确定要删除这条用例吗？', '提示', {
    type: 'warning'
  }).then(() => {
    testCaseStore.deleteCase(row.id).then(() => {
      ElMessage.success('删除成功')
      loadCases()
    })
  })
}

function handleBatchDelete() {
  ElMessageBox.confirm(`确定要删除选中的 ${selectedCases.value.length} 条用例吗？`, '提示', {
    type: 'warning'
  }).then(() => {
    testCaseStore.batchDeleteCases(selectedCases.value).then(() => {
      ElMessage.success('删除成功')
      loadCases()
    })
  })
}

function handleBatchMove() {
  ElMessageBox.prompt('请输入目标文件夹ID', '批量移动', {
    confirmButtonText: '确定',
    cancelButtonText: '取消'
  }).then(({ value }) => {
    testCaseStore.batchMoveCases(selectedCases.value, parseInt(value)).then(() => {
      ElMessage.success('移动成功')
      loadCases()
    })
  })
}

function addStep() {
  form.stepList.push({ step: '', expected: '' })
}

function removeStep(index) {
  if (form.stepList.length > 1) {
    form.stepList.splice(index, 1)
  }
}

function handleStepChange() {
  // 将步骤列表转换为JSON格式
  const validSteps = form.stepList.filter(s => s.step || s.expected)
  form.steps = JSON.stringify(validSteps)
  // 兼容旧字段
  form.expected_result = validSteps.map(s => s.expected).filter(Boolean).join('\n')
}

function handleSubmit() {
  formRef.value.validate((valid) => {
    if (valid) {
      // 提交前处理步骤数据
      handleStepChange()

      const submitData = { ...form }
      delete submitData.stepList

      const api = isEdit.value ? testCaseStore.updateCase : testCaseStore.createCase
      const params = isEdit.value ? form.id : submitData
      api(params, isEdit.value ? submitData : null).then(() => {
        ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
        dialogVisible.value = false
        loadCases()
        loadSuites()
      })
    }
  })
}

// 解析步骤列表
function getStepList(steps) {
  if (!steps) return [{ step: '无', expected: '无' }]

  // 尝试解析 JSON
  try {
    let parsed = steps
    // 如果是字符串，尝试解析
    if (typeof steps === 'string') {
      // 尝试直接解析
      try {
        parsed = JSON.parse(steps)
      } catch {
        // 如果失败，尝试去除转义字符后再解析
        try {
          // 处理被双重转义的情况
          const unescaped = steps.replace(/\\"/g, '"').replace(/\\\\/g, '\\')
          parsed = JSON.parse(unescaped)
        } catch {
          // 仍然失败，返回提示
          return [{ step: '步骤格式错误', expected: '请检查数据格式' }]
        }
      }
    }

    // 确保是数组
    if (Array.isArray(parsed)) {
      return parsed.length > 0 ? parsed : [{ step: '无', expected: '无' }]
    }
  } catch (e) {
    console.error('解析步骤失败:', e, steps)
  }

  return [{ step: '无', expected: '无' }]
}

// 查看用例
function handleView(row) {
  viewCase.value = row
  viewDialogVisible.value = true
}

// 执行用例
function handleExecute(row) {
  executeCase.value = row
  // 重置执行表单
  Object.assign(executeForm, {
    status: 'passed',
    actual_result: '',
    notes: '',
    duration: 0,
    defect_ids: []
  })
  // 加载缺陷列表
  loadDefects()
  executeDialogVisible.value = true
}

// AI执行用例
// AI执行单个用例
function handleAIExecute(row) {
  pendingAIExecuteCase.value = row
  selectedEnvironmentId.value = null
  envDialogVisible.value = true
  loadEnvironments()
}

// 加载环境列表
async function loadEnvironments() {
  try {
    const res = await environmentApi.getList({
      per_page: 100
    })
    environmentList.value = res.data?.items || []
  } catch (error) {
    console.error('加载环境列表失败:', error)
  }
}

// 确认AI执行
function handleConfirmAIExecute() {
  if (!selectedEnvironmentId.value) {
    ElMessage.warning('请选择执行环境')
    return
  }

  envDialogVisible.value = false

  router.push({
    path: '/test-cases/ai-execution',
    query: {
      caseIds: pendingAIExecuteCase.value.id,
      environmentId: selectedEnvironmentId.value
    }
  })
}

// 加载缺陷列表
async function loadDefects() {
  try {
    const res = await defectApi.getList({
      project_id: currentProjectId.value,
      per_page: 100
    })
    defectList.value = res.data?.items || []
  } catch (error) {
    console.error('加载缺陷列表失败:', error)
  }
}

// 创建缺陷
function handleCreateDefect() {
  router.push({
    path: '/defects',
    query: {
      action: 'create',
      test_case_id: executeCase.value?.id,
      test_result: executeForm.status === 'failed' ? executeForm.actual_result : ''
    }
  })
}

// 提交执行结果
async function handleSubmitExecution() {
  if (!executeForm.status) {
    ElMessage.warning('请选择执行状态')
    return
  }

  executing.value = true
  try {
    // 调用执行API创建执行记录
    const { testExecutionApi } = await import('@/api/test-plan')

    await testExecutionApi.create({
      test_case_id: executeCase.value.id,
      status: executeForm.status,
      actual_result: executeForm.actual_result,
      notes: executeForm.notes,
      duration: executeForm.duration,
      defect_ids: executeForm.defect_ids,
      executed_by: 'current_user' // TODO: 从登录用户信息获取
    })

    ElMessage.success('执行结果提交成功')
    executeDialogVisible.value = false

    // 刷新用例列表（可能显示最新执行状态）
    loadCases()
  } catch (error) {
    console.error('提交执行结果失败:', error)
    ElMessage.error('提交失败: ' + (error.response?.data?.message || error.message))
  } finally {
    executing.value = false
  }
}

onMounted(() => {
  if (currentProjectId.value) {
    loadSuites()
    loadCases()
  }
})

// 监听项目变化，重新加载数据
watch(currentProjectId, (newVal, oldVal) => {
  if (newVal && newVal !== oldVal) {
    currentSuiteId.value = null
    testCaseStore.setCurrentSuite(null)
    loadSuites()
    loadCases()
  }
})
</script>

<style scoped>
.test-case-page {
  height: 100%;
}

.page-layout {
  display: flex;
  height: calc(100vh - 120px);
  overflow: hidden;
}

.suite-sidebar {
  flex-shrink: 0;
  background: #fff;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

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

.suite-header {
  padding: 12px 16px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 500;
}

.suite-sidebar :deep(.el-tree) {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.tree-node {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-right: 8px;
  width: 100%;
}

.node-content {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 6px;
  overflow: hidden;
}

.folder-icon {
  color: #409eff;
  font-size: 16px;
  flex-shrink: 0;
}

.node-label {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
}

.node-count {
  color: #909399;
  font-size: 12px;
  flex-shrink: 0;
}

.node-more {
  opacity: 0;
  transition: opacity 0.2s;
}

.tree-node:hover .node-more {
  opacity: 1;
}

.content-area {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.content-area :deep(.el-card) {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.content-area :deep(.el-card__body) {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.steps-table-wrapper {
  width: 100%;
}

.steps-table-wrapper :deep(.el-textarea__inner) {
  resize: none;
}

.detail-content {
  padding: 12px;
  background-color: #f5f7fa;
  border-radius: 4px;
  min-height: 40px;
  white-space: pre-wrap;
  word-break: break-word;
}

.case-detail .el-divider {
  margin: 20px 0;
}

.case-execute .el-divider {
  margin: 20px 0;
}
</style>

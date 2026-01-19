<template>
  <div class="page-container">
    <div class="page-layout" ref="layoutRef">
      <!-- Sidebar with Directory Tree -->
      <div class="page-sidebar suite-sidebar" :style="{ width: sidebarWidth + 'px' }">
        <div class="sidebar-header">
          <span class="sidebar-title">{{ t('testCase.suite', '套件') }}</span>
          <el-dropdown trigger="click" @command="handleSuiteCommand">
            <el-button type="primary" link size="small">
              <el-icon><Plus /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="add">{{ t('testCase.newFolder') }}</el-dropdown-item>
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
          class="suite-tree"
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
                    <el-dropdown-item command="addSub">{{ t('testCase.addSubSuite', '添加子套件') }}</el-dropdown-item>
                    <el-dropdown-item command="edit">{{ t('common.edit') }}</el-dropdown-item>
                    <el-dropdown-item command="delete">{{ t('common.delete') }}</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </template>
        </el-tree>
      </div>

      <!-- Resize Handle -->
      <div
        class="resize-handle"
        @mousedown="handleMouseDown"
      ></div>

      <!-- Content Area -->
      <div class="content-area">
        <el-card>
          <!-- Toolbar -->
          <div class="toolbar">
            <div class="toolbar-left">
              <el-input
                v-model="searchForm.keyword"
                :placeholder="t('testCase.searchPlaceholder', t('common.search'))"
                clearable
                class="search-input"
                @change="loadCases"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
              <el-select v-model="searchForm.priority" :placeholder="t('testCase.priority')" clearable @change="loadCases">
                <el-option :label="t('testCase.critical')" value="critical" />
                <el-option :label="t('testCase.high')" value="high" />
                <el-option :label="t('testCase.medium')" value="medium" />
                <el-option :label="t('testCase.low')" value="low" />
              </el-select>
              <el-select v-model="searchForm.status" :placeholder="t('testCase.status')" clearable @change="loadCases">
                <el-option :label="t('testCase.draft')" value="draft" />
                <el-option :label="t('testCase.active')" value="active" />
                <el-option :label="t('testCase.archived')" value="archived" />
              </el-select>
              <el-button :icon="Search" @click="showAdvancedSearch = true">{{ t('common.advanced', '高级搜索') }}</el-button>
            </div>
            <div class="toolbar-right">
              <el-button type="primary" :icon="Plus" @click="handleCreateCase">{{ t('testCase.newCase') }}</el-button>
              <el-button
                v-if="selectedCases.length > 0"
                type="danger"
                @click="handleBatchDelete"
              >
                {{ t('testCase.batchDelete') }} ({{ selectedCases.length }})
              </el-button>
              <el-button
                v-if="selectedCases.length > 0"
                @click="handleBatchMove"
              >
                {{ t('testCase.batchMove') }}
              </el-button>
            </div>
          </div>

          <!-- Table -->
          <el-table
            :data="caseList"
            @selection-change="handleSelectionChange"
            class="case-table"
          >
            <el-table-column type="selection" width="55" />
            <el-table-column :label="t('testCase.caseNo')" width="120">
              <template #default="{ row }">
                {{ row.case_no || `CASE-${row.id}` }}
              </template>
            </el-table-column>
            <el-table-column prop="name" :label="t('testCase.caseName')" show-overflow-tooltip />
            <el-table-column prop="priority" :label="t('testCase.priority')" width="100">
              <template #default="{ row }">
                <el-tag :type="getPriorityType(row.priority)">{{ getPriorityText(row.priority) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="case_type" :label="t('testCase.type')" width="100">
              <template #default="{ row }">
                <el-tag type="info">{{ getCaseTypeText(row.case_type) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="automation_status" :label="t('testCase.automation')" width="110">
              <template #default="{ row }">
                <el-tag :type="row.automation_status === 'automated' ? 'success' : 'info'">
                  {{ getAutomationText(row.automation_status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" :label="t('testCase.status')" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column :label="t('common.operation')" width="200" fixed="right">
              <template #default="{ row }">
                <el-tooltip :content="t('testCase.viewCase', '查看用例')" placement="top">
                  <el-button type="info" link size="small" @click="handleView(row)">
                    <el-icon><View /></el-icon>
                  </el-button>
                </el-tooltip>
                <el-tooltip :content="t('testCase.executeCase', '执行用例')" placement="top">
                  <el-button type="success" link size="small" @click="handleExecute(row)">
                    <el-icon><VideoPlay /></el-icon>
                  </el-button>
                </el-tooltip>
                <el-tooltip content="AI执行" placement="top">
                  <el-button type="warning" link size="small" @click="handleAIExecute(row)">
                    <el-icon><MagicStick /></el-icon>
                  </el-button>
                </el-tooltip>
                <el-tooltip :content="t('testCase.editCase', t('common.edit') + '用例')" placement="top">
                  <el-button type="primary" link size="small" @click="handleEdit(row)">
                    <el-icon><Edit /></el-icon>
                  </el-button>
                </el-tooltip>
                <el-tooltip :content="t('common.delete')" placement="top">
                  <el-button type="danger" link size="small" @click="handleDelete(row)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </el-tooltip>
              </template>
            </el-table-column>
          </el-table>

          <!-- Pagination -->
          <div class="table-pagination">
            <el-pagination
              v-model:current-page="pagination.page"
              v-model:page-size="pagination.pageSize"
              :total="pagination.total"
              :page-sizes="[10, 20, 50, 100]"
              layout="total, sizes, prev, pager, next, jumper"
              @current-change="loadCases"
              @size-change="loadCases"
            />
          </div>
        </el-card>
      </div>
    </div>

    <!-- Case Form Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="900px"
      destroy-on-close
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item :label="t('testCase.caseName')" prop="name">
          <el-input v-model="form.name" :placeholder="t('testCase.enterCaseName', '请输入用例名称')" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item :label="t('testCase.caseNo')" prop="case_no">
              <el-input v-model="form.case_no" :placeholder="t('testCase.autoGenerated', '自动生成')" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item :label="t('testCase.suite', '套件')" prop="suite_id">
              <el-tree-select
                v-model="form.suite_id"
                :data="suiteOptions"
                :props="{ value: 'id', label: 'name', children: 'children' }"
                check-strictly
                clearable
                :placeholder="t('testCase.selectSuite', '选择套件')"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item :label="t('testCase.priority')" prop="priority">
              <el-select v-model="form.priority" style="width: 100%">
                <el-option :label="t('testCase.critical')" value="critical" />
                <el-option :label="t('testCase.high')" value="high" />
                <el-option :label="t('testCase.medium')" value="medium" />
                <el-option :label="t('testCase.low')" value="low" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item :label="t('testCase.type')" prop="case_type">
              <el-select v-model="form.case_type" style="width: 100%">
                <el-option :label="t('testCase.functional')" value="functional" />
                <el-option :label="t('testCase.performance')" value="performance" />
                <el-option :label="t('testCase.security')" value="security" />
                <el-option :label="t('testCase.ui')" value="ui" />
                <el-option :label="t('testCase.api')" value="api" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item :label="t('testCase.automation')" prop="automation_status">
              <el-select v-model="form.automation_status" style="width: 100%">
                <el-option :label="t('testCase.manual')" value="manual" />
                <el-option :label="t('testCase.automated')" value="automated" />
                <el-option :label="t('testCase.semiAutomated')" value="semi-automated" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item :label="t('testCase.status')" prop="status">
              <el-select v-model="form.status" style="width: 100%">
                <el-option :label="t('testCase.draft')" value="draft" />
                <el-option :label="t('testCase.active')" value="active" />
                <el-option :label="t('testCase.archived')" value="archived" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item :label="t('testCase.preconditions')" prop="preconditions">
          <el-input v-model="form.preconditions" type="textarea" :rows="2" :placeholder="t('testCase.preconditionsPlaceholder', '测试执行前的条件...')" />
        </el-form-item>

        <!-- Test Steps Table -->
        <el-form-item :label="t('testCase.testSteps')" prop="stepList">
          <div class="steps-table-wrapper">
            <el-table :data="form.stepList" border style="width: 100%">
              <el-table-column label="#" width="60" align="center">
                <template #default="{ $index }">
                  <span>{{ $index + 1 }}</span>
                </template>
              </el-table-column>
              <el-table-column :label="t('testCase.stepDesc')" min-width="200">
                <template #default="{ row }">
                  <el-input
                    v-model="row.step"
                    type="textarea"
                    :rows="2"
                    :placeholder="t('testCase.enterStepDesc', '输入步骤描述')"
                    @blur="handleStepChange"
                  />
                </template>
              </el-table-column>
              <el-table-column :label="t('testCase.expected')" min-width="200">
                <template #default="{ row }">
                  <el-input
                    v-model="row.expected"
                    type="textarea"
                    :rows="2"
                    :placeholder="t('testCase.enterExpected', '输入期望结果')"
                    @blur="handleStepChange"
                  />
                </template>
              </el-table-column>
              <el-table-column :label="t('common.operation')" width="80" align="center">
                <template #default="{ $index }">
                  <el-button
                    type="danger"
                    link
                    :icon="Delete"
                    @click="removeStep($index)"
                    :disabled="form.stepList.length <= 1"
                  >
                    {{ t('testCase.removeStep') }}
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
              {{ t('testCase.addStep') }}
            </el-button>
          </div>
        </el-form-item>

        <el-form-item :label="t('testCase.postconditions')" prop="postconditions">
          <el-input v-model="form.postconditions" type="textarea" :rows="2" :placeholder="t('testCase.postconditionsPlaceholder', '清理或恢复操作...')" />
        </el-form-item>

        <el-form-item :label="t('testCase.remarks')" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" :placeholder="t('testCase.remarksPlaceholder', '额外备注...')" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" @click="handleSubmit">{{ t('common.submit') }}</el-button>
      </template>
    </el-dialog>

    <!-- Suite Form Dialog -->
    <el-dialog v-model="suiteDialogVisible" :title="suiteDialogTitle" width="500px">
      <el-form :model="suiteForm" :rules="suiteRules" ref="suiteFormRef" label-width="100px">
        <el-form-item :label="t('testCase.folderName')" prop="name">
          <el-input v-model="suiteForm.name" :placeholder="t('testCase.enterSuiteName', '输入套件名称')" />
        </el-form-item>
        <el-form-item :label="t('testCase.parentSuite', '父套件')" prop="parent_id">
          <el-tree-select
            v-model="suiteForm.parent_id"
            :data="suiteOptions"
            :props="{ value: 'id', label: 'name', children: 'children' }"
            check-strictly
            clearable
            :placeholder="t('testCase.selectParentSuite', '选择父套件')"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="suiteDialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" @click="handleSuiteSubmit">{{ t('common.submit') }}</el-button>
      </template>
    </el-dialog>

    <!-- View Case Dialog -->
    <el-dialog
      v-model="viewDialogVisible"
      :title="t('testCase.viewCase', '查看用例')"
      width="900px"
      destroy-on-close
    >
      <div v-if="viewCase" class="case-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item :label="t('testCase.caseNo')">{{ viewCase.case_no || `CASE-${viewCase.id}` }}</el-descriptions-item>
          <el-descriptions-item :label="t('testCase.caseName')">{{ viewCase.name }}</el-descriptions-item>
          <el-descriptions-item :label="t('testCase.priority')">
            <el-tag :type="getPriorityType(viewCase.priority)">{{ getPriorityText(viewCase.priority) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item :label="t('testCase.type')">
            <el-tag type="info">{{ getCaseTypeText(viewCase.case_type) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item :label="t('testCase.automation')">
            <el-tag :type="viewCase.automation_status === 'automated' ? 'success' : 'info'">
              {{ getAutomationText(viewCase.automation_status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item :label="t('testCase.status')">
            <el-tag :type="getStatusType(viewCase.status)">{{ getStatusText(viewCase.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item :label="t('common.createdAt')" :span="2">
            {{ viewCase.created_at ? new Date(viewCase.created_at).toLocaleString() : '-' }}
          </el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left">{{ t('testCase.preconditions') }}</el-divider>
        <div class="detail-content">
          {{ viewCase.preconditions || t('common.none', '无') }}
        </div>

        <el-divider content-position="left">{{ t('testCase.testSteps') }}</el-divider>
        <el-table :data="getStepList(viewCase.steps)" border style="width: 100%">
          <el-table-column label="#" width="60" align="center">
            <template #default="{ $index }">
              <span>{{ $index + 1 }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="step" :label="t('testCase.stepDesc')" />
          <el-table-column prop="expected" :label="t('testCase.expectedResult', '期望结果')" />
        </el-table>

        <el-divider content-position="left">{{ t('testCase.postconditions') }}</el-divider>
        <div class="detail-content">
          {{ viewCase.postconditions || t('common.none', '无') }}
        </div>

        <el-divider content-position="left">{{ t('testCase.remarks') }}</el-divider>
        <div class="detail-content">
          {{ viewCase.description || t('common.none', '无') }}
        </div>
      </div>
      <template #footer>
        <el-button type="primary" @click="viewDialogVisible = false">{{ t('common.close', '关闭') }}</el-button>
      </template>
    </el-dialog>

    <!-- Execute Case Dialog -->
    <el-dialog
      v-model="executeDialogVisible"
      :title="t('testCase.executeCase', '执行用例')"
      width="900px"
      destroy-on-close
    >
      <div v-if="executeCase" class="case-execute">
        <el-descriptions :column="2" border>
          <el-descriptions-item :label="t('testCase.caseNo')">{{ executeCase.case_no || `CASE-${executeCase.id}` }}</el-descriptions-item>
          <el-descriptions-item :label="t('testCase.caseName')">{{ executeCase.name }}</el-descriptions-item>
          <el-descriptions-item :label="t('testCase.priority')">
            <el-tag :type="getPriorityType(executeCase.priority)">{{ getPriorityText(executeCase.priority) }}</el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left">{{ t('testCase.preconditions') }}</el-divider>
        <div class="detail-content">
          {{ executeCase.preconditions || t('common.none', '无') }}
        </div>

        <el-divider content-position="left">{{ t('testCase.testSteps') }}</el-divider>
        <el-table :data="getStepList(executeCase.steps)" border style="width: 100%">
          <el-table-column label="#" width="60" align="center">
            <template #default="{ $index }">
              <span>{{ $index + 1 }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="step" :label="t('testCase.stepDesc')" />
          <el-table-column prop="expected" :label="t('testCase.expectedResult', '期望结果')" />
        </el-table>

        <el-divider content-position="left">{{ t('testCase.executionResult', '执行结果') }}</el-divider>
        <el-form :model="executeForm" label-width="100px">
          <el-form-item :label="t('testCase.status')" prop="status" required>
            <el-radio-group v-model="executeForm.status">
              <el-radio label="passed">{{ t('testCase.passed', '通过') }}</el-radio>
              <el-radio label="failed">{{ t('testCase.failed', '失败') }}</el-radio>
              <el-radio label="blocked">{{ t('testCase.blocked', '阻塞') }}</el-radio>
              <el-radio label="skipped">{{ t('testCase.skipped', '跳过') }}</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item :label="t('testCase.actualResult', '实际结果')">
            <el-input
              v-model="executeForm.actual_result"
              type="textarea"
              :rows="4"
              :placeholder="t('testCase.enterActualResult', '输入实际执行结果...')"
            />
          </el-form-item>

          <el-form-item :label="t('testCase.remarks')">
            <el-input
              v-model="executeForm.notes"
              type="textarea"
              :rows="3"
              :placeholder="t('testCase.executionNotesPlaceholder', '额外备注...')"
            />
          </el-form-item>

          <el-form-item :label="t('testCase.duration', '时长(秒)')">
            <el-input-number
              v-model="executeForm.duration"
              :min="0"
              :max="99999"
              :placeholder="t('testCase.executionDuration', '执行时长')"
            />
          </el-form-item>

          <el-form-item :label="t('testCase.relatedDefects', '关联缺陷')">
            <div style="display: flex; gap: 8px; width: 100%">
              <el-select
                v-model="executeForm.defect_ids"
                multiple
                filterable
                :placeholder="t('testCase.selectDefects', '选择现有缺陷')"
                style="flex: 1"
              >
                <el-option
                  v-for="defect in defectList"
                  :key="defect.id"
                  :label="`${defect.defect_no || `DEF-${defect.id}`} - ${defect.title}`"
                  :value="defect.id"
                />
              </el-select>
              <el-button type="primary" @click="handleCreateDefect">{{ t('testCase.createDefect', '创建缺陷') }}</el-button>
            </div>
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="executeDialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="executing" @click="handleSubmitExecution">{{ t('testCase.submitResult', '提交结果') }}</el-button>
      </template>
    </el-dialog>

    <!-- Environment Selection Dialog -->
    <el-dialog v-model="envDialogVisible" :title="t('testCase.selectEnvironment', '选择执行环境')" width="500px" destroy-on-close>
      <el-form label-width="100px">
        <el-form-item :label="t('testCase.environment', '环境')" required>
          <el-select v-model="selectedEnvironmentId" :placeholder="t('testCase.selectEnvironment', '选择环境')" style="width: 100%">
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
        <el-button @click="envDialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" @click="handleConfirmAIExecute">{{ t('common.confirm') }}</el-button>
      </template>
    </el-dialog>

    <!-- Advanced Search Dialog -->
    <el-dialog v-model="showAdvancedSearch" :title="t('common.advanced', '高级搜索')" width="700px" destroy-on-close>
      <el-form :model="advancedSearchForm" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item :label="t('testCase.caseNo')">
              <el-input v-model="advancedSearchForm.case_no" :placeholder="t('testCase.caseNoPlaceholder', '例如：CASE-0001')" clearable />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('testCase.caseName')">
              <el-input v-model="advancedSearchForm.name" :placeholder="t('testCase.enterCaseName', '输入用例名称')" clearable />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item :label="t('testCase.priority')">
              <el-select v-model="advancedSearchForm.priority" :placeholder="t('testCase.selectPriority', '选择优先级')" clearable style="width: 100%">
                <el-option :label="t('testCase.critical')" value="critical" />
                <el-option :label="t('testCase.high')" value="high" />
                <el-option :label="t('testCase.medium')" value="medium" />
                <el-option :label="t('testCase.low')" value="low" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('testCase.status')">
              <el-select v-model="advancedSearchForm.status" :placeholder="t('testCase.selectStatus', '选择状态')" clearable style="width: 100%">
                <el-option :label="t('testCase.draft')" value="draft" />
                <el-option :label="t('testCase.active')" value="active" />
                <el-option :label="t('testCase.archived')" value="archived" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item :label="t('testCase.type')">
              <el-select v-model="advancedSearchForm.case_type" :placeholder="t('testCase.selectType', '选择类型')" clearable style="width: 100%">
                <el-option :label="t('testCase.functional')" value="functional" />
                <el-option :label="t('testCase.performance')" value="performance" />
                <el-option :label="t('testCase.security')" value="security" />
                <el-option :label="t('testCase.ui')" value="ui" />
                <el-option :label="t('testCase.api')" value="api" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('testCase.automation')">
              <el-select v-model="advancedSearchForm.automation_status" :placeholder="t('testCase.selectStatus', '选择状态')" clearable style="width: 100%">
                <el-option :label="t('testCase.manual')" value="manual" />
                <el-option :label="t('testCase.automated')" value="automated" />
                <el-option :label="t('testCase.semiAutomated')" value="semi-automated" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item :label="t('common.createdAt')">
              <el-date-picker
                v-model="advancedSearchForm.created_at"
                type="daterange"
                range-separator="to"
                :start-placeholder="t('testCase.startDate', '开始日期')"
                :end-placeholder="t('testCase.endDate', '结束日期')"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('common.updatedAt')">
              <el-date-picker
                v-model="advancedSearchForm.updated_at"
                type="daterange"
                range-separator="to"
                :start-placeholder="t('testCase.startDate', '开始日期')"
                :end-placeholder="t('testCase.endDate', '结束日期')"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item :label="t('testCase.keyword', '关键词')">
          <el-input v-model="advancedSearchForm.keyword" :placeholder="t('testCase.keywordPlaceholder', '搜索名称、编号、步骤、期望结果...')" clearable />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="handleResetAdvancedSearch">{{ t('common.reset') }}</el-button>
        <el-button @click="showAdvancedSearch = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" @click="handleAdvancedSearch">{{ t('common.search') }}</el-button>
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
import { useI18n } from '@/i18n'

const router = useRouter()
const { t } = useI18n()

const testCaseStore = useTestCaseStore()
const projectStore = useProjectStore()
const treeRef = ref()
const formRef = ref()
const suiteFormRef = ref()
const layoutRef = ref()

// Sidebar width related
const sidebarWidth = ref(250)
const minWidth = 180
const maxWidth = 500
const isResizing = ref(false)

// Restore width from localStorage
const savedWidth = localStorage.getItem('test-case-sidebar-width')
if (savedWidth) {
  sidebarWidth.value = parseInt(savedWidth)
}

// Watch width changes and save
watch(sidebarWidth, (newWidth) => {
  localStorage.setItem('test-case-sidebar-width', newWidth.toString())
})

// Mouse down start dragging
function handleMouseDown(e) {
  isResizing.value = true
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
  document.body.style.cursor = 'col-resize'
  document.body.style.userSelect = 'none'
}

// Mouse move
function handleMouseMove(e) {
  if (!isResizing.value || !layoutRef.value) return

  const rect = layoutRef.value.getBoundingClientRect()
  const newWidth = e.clientX - rect.left

  // Limit width range
  if (newWidth >= minWidth && newWidth <= maxWidth) {
    sidebarWidth.value = newWidth
  }
}

// Mouse up
function handleMouseUp() {
  isResizing.value = false
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
  document.body.style.cursor = ''
  document.body.style.userSelect = ''
}

// Current project ID
const currentProjectId = computed(() => projectStore.currentProject?.id)

const suiteTree = ref([])
const suiteOptions = ref([])
const caseList = ref([])
const selectedCases = ref([])
const currentSuiteId = ref(null)

const dialogVisible = ref(false)
const dialogTitle = ref('')
const isEdit = ref(false)

// Suite related
const suiteDialogVisible = ref(false)
const suiteDialogTitle = ref('')
const isSuiteEdit = ref(false)
const suiteForm = reactive({
  id: null,
  name: '',
  parent_id: null
})

const suiteRules = {
  name: [{ required: true, message: 'Suite name is required', trigger: 'blur' }]
}

const treeProps = {
  children: 'children',
  label: 'name',
  value: 'id'
}

const currentSuiteName = computed(() => {
  if (currentSuiteId.value === null) return 'All Test Cases'
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
  return findName(suiteTree.value, currentSuiteId.value) || 'Current Suite'
})

// View and Execute related
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

// Defect list
const defectList = ref([])

// Environment selection related
const envDialogVisible = ref(false)
const environmentList = ref([])
const selectedEnvironmentId = ref(null)
const pendingAIExecuteCase = ref(null)

// Advanced search
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
  name: [{ required: true, message: t('testCase.caseName') + ' ' + t('common.required', '为必填项'), trigger: 'blur' }]
}

function getPriorityType(priority) {
  const map = { critical: 'danger', high: 'warning', medium: 'primary', low: 'info' }
  return map[priority] || 'info'
}

function getPriorityText(priority) {
  const map = {
    critical: t('testCase.critical'),
    high: t('testCase.high'),
    medium: t('testCase.medium'),
    low: t('testCase.low')
  }
  return map[priority] || priority
}

function getStatusType(status) {
  const map = { draft: 'info', active: 'success', archived: 'warning' }
  return map[status] || 'info'
}

function getStatusText(status) {
  const map = {
    draft: t('testCase.draft'),
    active: t('testCase.active'),
    archived: t('testCase.archived')
  }
  return map[status] || status
}

function getCaseTypeText(type) {
  const map = {
    functional: t('testCase.functional'),
    performance: t('testCase.performance'),
    security: t('testCase.security'),
    ui: t('testCase.ui'),
    api: t('testCase.api')
  }
  return map[type] || type
}

function getAutomationText(status) {
  const map = {
    manual: t('testCase.manual'),
    automated: t('testCase.automated'),
    'semi-automated': t('testCase.semiAutomated')
  }
  return map[status] || status
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

// Suite operation commands
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

// Add suite
function handleAddSuite(parentId = null) {
  isSuiteEdit.value = false
  suiteDialogTitle.value = parentId ? t('testCase.addSubSuite', '添加子套件') : t('testCase.newFolder')
  Object.assign(suiteForm, {
    id: null,
    name: '',
    parent_id: parentId
  })
  suiteDialogVisible.value = true
}

// Edit suite
function handleEditSuite(data) {
  isSuiteEdit.value = true
  suiteDialogTitle.value = t('testCase.editSuite', '编辑套件')
  Object.assign(suiteForm, {
    id: data.id,
    name: data.name,
    parent_id: data.parent_id
  })
  suiteDialogVisible.value = true
}

// Delete suite
function handleDeleteSuite(data) {
  ElMessageBox.confirm(t('testCase.deleteSuiteConfirm', '确定要删除这个套件吗？测试用例将变成无套件状态。'), t('common.confirm'), {
    type: 'warning'
  }).then(() => {
    testCaseStore.deleteSuite(data.id).then(() => {
      ElMessage.success(t('testCase.deleteSuccess'))
      loadSuites()
      if (currentSuiteId.value === data.id) {
        currentSuiteId.value = null
        testCaseStore.setCurrentSuite(null)
      }
    })
  })
}

// Submit suite form
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
        ElMessage.success(isSuiteEdit.value ? t('testCase.updateSuccess') : t('testCase.createSuccess'))
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

  // Basic search: only search name
  if (searchForm.keyword) {
    params.name = searchForm.keyword
  }
  // Priority and status filter
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

// Advanced search handler
function handleAdvancedSearch() {
  // Build search params
  const params = {
    page: 1,
    per_page: pagination.pageSize,
    suite_id: currentSuiteId.value,
    project_id: currentProjectId.value
  }

  // Add advanced search conditions
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

  // Sync to basic search display
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

// Reset advanced search
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
  dialogTitle.value = t('testCase.newCase')
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
  dialogTitle.value = t('testCase.editCase', t('common.edit') + ' ' + t('testCase.title'))

  // Parse steps data
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
  ElMessageBox.confirm(t('testCase.deleteConfirm'), t('common.confirm'), {
    type: 'warning'
  }).then(() => {
    testCaseStore.deleteCase(row.id).then(() => {
      ElMessage.success(t('testCase.deleteSuccess'))
      loadCases()
    })
  })
}

function handleBatchDelete() {
  ElMessageBox.confirm(t('testCase.batchDeleteConfirm', `确定要删除选中的 ${selectedCases.value.length} 条用例吗？`), t('common.confirm'), {
    type: 'warning'
  }).then(() => {
    testCaseStore.batchDeleteCases(selectedCases.value).then(() => {
      ElMessage.success(t('testCase.deleteSuccess'))
      loadCases()
    })
  })
}

function handleBatchMove() {
  ElMessageBox.prompt(t('testCase.targetSuitePrompt', '输入目标套件ID'), t('testCase.batchMove'), {
    confirmButtonText: t('common.confirm'),
    cancelButtonText: t('common.cancel')
  }).then(({ value }) => {
    testCaseStore.batchMoveCases(selectedCases.value, parseInt(value)).then(() => {
      ElMessage.success(t('testCase.moveSuccess'))
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
  // Convert step list to JSON format
  const validSteps = form.stepList.filter(s => s.step || s.expected)
  form.steps = JSON.stringify(validSteps)
  // Compatible with old field
  form.expected_result = validSteps.map(s => s.expected).filter(Boolean).join('\n')
}

function handleSubmit() {
  formRef.value.validate((valid) => {
    if (valid) {
      // Process step data before submit
      handleStepChange()

      const submitData = { ...form }
      delete submitData.stepList

      const api = isEdit.value ? testCaseStore.updateCase : testCaseStore.createCase
      const params = isEdit.value ? form.id : submitData
      api(params, isEdit.value ? submitData : null).then(() => {
        ElMessage.success(isEdit.value ? t('testCase.updateSuccess') : t('testCase.createSuccess'))
        dialogVisible.value = false
        loadCases()
        loadSuites()
      })
    }
  })
}

// Parse step list
function getStepList(steps) {
  if (!steps) return [{ step: 'None', expected: 'None' }]

  // Try to parse JSON
  try {
    let parsed = steps
    // If string, try to parse
    if (typeof steps === 'string') {
      // Try direct parse
      try {
        parsed = JSON.parse(steps)
      } catch {
        // If fails, try to remove escape chars then parse
        try {
          // Handle double-escaped case
          const unescaped = steps.replace(/\\"/g, '"').replace(/\\\\/g, '\\')
          parsed = JSON.parse(unescaped)
        } catch {
          // Still fails, return prompt
          return [{ step: 'Step format error', expected: 'Please check data format' }]
        }
      }
    }

    // Ensure it's an array
    if (Array.isArray(parsed)) {
      return parsed.length > 0 ? parsed : [{ step: 'None', expected: 'None' }]
    }
  } catch (e) {
    console.error('Parse steps failed:', e, steps)
  }

  return [{ step: 'None', expected: 'None' }]
}

// View case
function handleView(row) {
  viewCase.value = row
  viewDialogVisible.value = true
}

// Execute case
function handleExecute(row) {
  executeCase.value = row
  // Reset execution form
  Object.assign(executeForm, {
    status: 'passed',
    actual_result: '',
    notes: '',
    duration: 0,
    defect_ids: []
  })
  // Load defect list
  loadDefects()
  executeDialogVisible.value = true
}

// AI execute case
function handleAIExecute(row) {
  pendingAIExecuteCase.value = row
  selectedEnvironmentId.value = null
  envDialogVisible.value = true
  loadEnvironments()
}

// Load environment list
async function loadEnvironments() {
  try {
    const res = await environmentApi.getList({
      per_page: 100
    })
    environmentList.value = res.data?.items || []
  } catch (error) {
    console.error('Failed to load environments:', error)
  }
}

// Confirm AI execute
function handleConfirmAIExecute() {
  if (!selectedEnvironmentId.value) {
    ElMessage.warning(t('testCase.selectEnvironment', '请选择执行环境'))
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

// Load defect list
async function loadDefects() {
  try {
    const res = await defectApi.getList({
      project_id: currentProjectId.value,
      per_page: 100
    })
    defectList.value = res.data?.items || []
  } catch (error) {
    console.error('Failed to load defects:', error)
  }
}

// Create defect
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

// Submit execution result
async function handleSubmitExecution() {
  if (!executeForm.status) {
    ElMessage.warning(t('testCase.selectExecutionStatus', '请选择执行状态'))
    return
  }

  executing.value = true
  try {
    // Call execution API to create execution record
    const { testExecutionApi } = await import('@/api/test-plan')

    await testExecutionApi.create({
      test_case_id: executeCase.value.id,
      status: executeForm.status,
      actual_result: executeForm.actual_result,
      notes: executeForm.notes,
      duration: executeForm.duration,
      defect_ids: executeForm.defect_ids,
      executed_by: 'current_user' // TODO: Get from logged in user
    })

    ElMessage.success(t('testCase.executionSubmitted', '执行结果提交成功'))
    executeDialogVisible.value = false

    // Refresh case list (may show latest execution status)
    loadCases()
  } catch (error) {
    console.error('Failed to submit execution result:', error)
    ElMessage.error(t('testCase.submitFailed', '提交失败：') + (error.response?.data?.message || error.message))
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

// Watch project changes, reload data
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
/* Page-specific styles only - general layout styles are in page-layout.css */

/* ========================================
   DETAIL CONTENT
   ======================================== */
.detail-content {
  padding: var(--space-4);
  background: var(--color-bg-alt);
  border-radius: var(--radius-sm);
  min-height: 40px;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--color-text);
}

.case-detail .el-divider {
  margin: var(--space-4) 0;
}

.case-execute .el-divider {
  margin: var(--space-4) 0;
}

/* ========================================
   STEPS TABLE
   ======================================== */
.steps-table-wrapper {
  width: 100%;
}

.steps-table-wrapper :deep(.el-textarea__inner) {
  resize: none;
}
</style>

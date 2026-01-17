<template>
  <div class="projects-page">
    <el-card>
      <div class="toolbar">
        <el-input
          v-model="searchForm.keyword"
          :placeholder="t('common.search')"
          clearable
          @change="fetchProjects"
          style="width: 200px"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <el-select
          v-model="searchForm.status"
          :placeholder="t('project.status')"
          clearable
          @change="fetchProjects"
          style="width: 150px"
        >
          <el-option :label="t('project.statusActive')" value="active" />
          <el-option :label="t('project.statusArchived')" value="archived" />
          <el-option :label="t('project.statusCompleted')" value="completed" />
        </el-select>

        <div style="flex: 1"></div>
        <el-button type="primary" :icon="Plus" @click="showCreateDialog">
          {{ t('common.create') }}
        </el-button>
      </div>

      <!-- 项目列表 -->
      <el-table v-loading="loading" :data="projectList" style="width: 100%">
        <el-table-column prop="name" :label="t('project.name')" min-width="200">
          <template #default="{ row }">
            <div class="project-name">
              <span
                v-if="row.icon"
                class="project-icon"
                :style="{ backgroundColor: row.color }"
              >
                {{ row.icon }}
              </span>
              <span v-else
                class="project-icon"
                :style="{ backgroundColor: row.color }"
              >
                {{ row.name.charAt(0) }}
              </span>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="code" :label="t('project.code')" width="120" />

        <el-table-column prop="key" :label="t('project.key')" width="100" />

        <el-table-column prop="project_type" :label="t('project.projectType')" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.project_type === 'web'" size="small">{{ t('project.typeWeb') }}</el-tag>
            <el-tag v-else-if="row.project_type === 'mobile'" type="success" size="small">
              {{ t('project.typeMobile') }}
            </el-tag>
            <el-tag v-else-if="row.project_type === 'api'" type="warning" size="small">
              {{ t('project.typeApi') }}
            </el-tag>
            <el-tag v-else type="info" size="small">{{ t('project.typeDesktop') }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column :label="t('project.testCaseCount')" width="100" align="center">
          <template #default="{ row }">
            <el-tag type="primary" size="small">{{ row.test_case_count || 0 }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column :label="t('project.testPlanCount')" width="100" align="center">
          <template #default="{ row }">
            <el-tag type="success" size="small">{{ row.test_plan_count || 0 }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column :label="t('project.defectCount')" width="100" align="center">
          <template #default="{ row }">
            <el-tag type="danger" size="small">{{ row.defect_count || 0 }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="status" :label="t('project.status')" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.status === 'active'" type="success" size="small">
              {{ t('project.statusActive') }}
            </el-tag>
            <el-tag v-else-if="row.status === 'archived'" type="info" size="small">
              {{ t('project.statusArchived') }}
            </el-tag>
            <el-tag v-else type="warning" size="small">
              {{ t('project.statusCompleted') }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column :label="t('common.operation')" width="140" fixed="right">
          <template #default="{ row }">
            <el-tooltip :content="t('common.edit')" placement="top">
              <el-button link type="primary" size="small" @click="handleEdit(row)">
                <el-icon><Edit /></el-icon>
              </el-button>
            </el-tooltip>
            <el-tooltip :content="t('common.delete')" placement="top">
              <el-button link type="danger" size="small" @click="handleDelete(row)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </el-tooltip>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.per_page"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="fetchProjects"
        @current-change="fetchProjects"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'create' ? t('common.create') : t('common.edit')"
      width="600px"
      @close="handleDialogClose"
      destroy-on-close
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
      >
        <el-form-item :label="t('project.name')" prop="name">
          <el-input v-model="formData.name" :placeholder="t('project.name')" />
        </el-form-item>

        <el-form-item :label="t('project.code')" prop="code">
          <el-input
            v-model="formData.code"
            :placeholder="t('project.code')"
            :disabled="dialogMode === 'edit'"
          />
        </el-form-item>

        <el-form-item :label="t('project.key')" prop="key">
          <el-input
            v-model="formData.key"
            :placeholder="t('project.key')"
            maxlength="10"
            show-word-limit
          />
        </el-form-item>

        <el-form-item :label="t('project.projectType')" prop="project_type">
          <el-select v-model="formData.project_type" :placeholder="t('project.projectType')" style="width: 100%">
            <el-option :label="t('project.typeWeb')" value="web" />
            <el-option :label="t('project.typeMobile')" value="mobile" />
            <el-option :label="t('project.typeApi')" value="api" />
            <el-option :label="t('project.typeDesktop')" value="desktop" />
          </el-select>
        </el-form-item>

        <el-form-item :label="t('project.description')">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            :placeholder="t('project.description')"
          />
        </el-form-item>

        <el-form-item :label="t('project.url')">
          <el-input v-model="formData.url" placeholder="https://example.com" />
        </el-form-item>

        <el-form-item :label="t('project.repository')">
          <el-input v-model="formData.repository" placeholder="https://github.com/user/repo" />
        </el-form-item>

        <el-form-item :label="t('project.status')" prop="status">
          <el-select v-model="formData.status" :placeholder="t('project.status')" style="width: 100%">
            <el-option :label="t('project.statusActive')" value="active" />
            <el-option :label="t('project.statusArchived')" value="archived" />
            <el-option :label="t('project.statusCompleted')" value="completed" />
          </el-select>
        </el-form-item>

        <el-form-item :label="t('project.owner')">
          <el-input v-model="formData.owner" :placeholder="t('project.owner')" />
        </el-form-item>

        <el-form-item :label="t('project.lead')">
          <el-input v-model="formData.lead" :placeholder="t('project.lead')" />
        </el-form-item>

        <el-form-item :label="t('project.color')">
          <el-color-picker v-model="formData.color" />
        </el-form-item>

        <el-form-item :label="t('project.icon')">
          <el-input v-model="formData.icon" placeholder="例如: 图标" maxlength="2" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          {{ t('common.save') }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Edit, Delete } from '@element-plus/icons-vue'
import { projectApi } from '@/api/project'
import { useI18n } from '@/i18n'

const { t } = useI18n()

// 数据
const loading = ref(false)
const submitting = ref(false)
const projectList = ref([])
const dialogVisible = ref(false)
const dialogMode = ref('create')
const formRef = ref(null)
const currentProjectId = ref(null)

// 搜索表单
const searchForm = reactive({
  keyword: '',
  status: ''
})

// 分页
const pagination = reactive({
  page: 1,
  per_page: 10,
  total: 0
})

// 表单数据
const formData = reactive({
  name: '',
  code: '',
  key: '',
  description: '',
  project_type: 'web',
  url: '',
  repository: '',
  status: 'active',
  owner: '',
  lead: '',
  color: '#409EFF',
  icon: ''
})

// 表单验证规则
const formRules = {
  name: [{ required: true, message: t('project.name') + '不能为空', trigger: 'blur' }],
  code: [{ required: true, message: t('project.code') + '不能为空', trigger: 'blur' }],
  project_type: [{ required: true, message: '请选择项目类型', trigger: 'change' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }]
}

// 获取项目列表
const fetchProjects = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      per_page: pagination.per_page,
      ...searchForm
    }
    const res = await projectApi.getList(params)
    if (res.code === 200) {
      projectList.value = res.data.items
      pagination.total = res.data.total
    }
  } catch (error) {
    ElMessage.error('获取项目列表失败')
  } finally {
    loading.value = false
  }
}

// 显示创建对话框
const showCreateDialog = () => {
  dialogMode.value = 'create'
  resetForm()
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row) => {
  dialogMode.value = 'edit'
  currentProjectId.value = row.id
  Object.assign(formData, {
    name: row.name,
    code: row.code,
    key: row.key,
    description: row.description,
    project_type: row.project_type,
    url: row.url,
    repository: row.repository,
    status: row.status,
    owner: row.owner,
    lead: row.lead,
    color: row.color,
    icon: row.icon
  })
  dialogVisible.value = true
}

// 删除
const handleDelete = (row) => {
  ElMessageBox.confirm(t('project.deleteConfirm'), '提示', {
    confirmButtonText: t('common.confirm'),
    cancelButtonText: t('common.cancel'),
    type: 'warning'
  }).then(async () => {
    try {
      const res = await projectApi.delete(row.id)
      if (res.code === 200) {
        ElMessage.success(t('project.deleteSuccess'))
        fetchProjects()
      }
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

// 提交表单
const handleSubmit = async () => {
  await formRef.value.validate()
  submitting.value = true
  try {
    const data = { ...formData }
    if (dialogMode.value === 'create') {
      const res = await projectApi.create(data)
      if (res.code === 200) {
        ElMessage.success(t('project.createSuccess'))
        dialogVisible.value = false
        fetchProjects()
      }
    } else {
      const res = await projectApi.update(currentProjectId.value, data)
      if (res.code === 200) {
        ElMessage.success(t('project.updateSuccess'))
        dialogVisible.value = false
        fetchProjects()
      }
    }
  } catch (error) {
    ElMessage.error(dialogMode.value === 'create' ? '创建失败' : '更新失败')
  } finally {
    submitting.value = false
  }
}

// 对话框关闭
const handleDialogClose = () => {
  resetForm()
  formRef.value?.clearValidate()
}

// 重置表单
const resetForm = () => {
  Object.assign(formData, {
    name: '',
    code: '',
    key: '',
    description: '',
    project_type: 'web',
    url: '',
    repository: '',
    status: 'active',
    owner: '',
    lead: '',
    color: '#409EFF',
    icon: ''
  })
  currentProjectId.value = null
}

onMounted(() => {
  fetchProjects()
})
</script>

<style scoped>
.projects-page {
  padding: 0;
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

.project-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.project-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  color: white;
  font-weight: 500;
  font-size: 14px;
  flex-shrink: 0;
}
</style>

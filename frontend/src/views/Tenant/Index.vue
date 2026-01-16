<template>
  <div class="tenant-page">
    <el-card>
      <template #header>
        <div class="page-header">
          <span>{{ t('tenant.title') }}</span>
          <el-button type="primary" :icon="Plus" @click="handleCreate">{{ t('tenant.create') }}</el-button>
        </div>
      </template>

      <div class="toolbar">
        <el-input
          v-model="searchForm.keyword"
          :placeholder="t('tenant.searchPlaceholder')"
          clearable
          style="width: 200px"
          @change="loadTenants"
        />
        <el-select v-model="searchForm.status" :placeholder="t('tenant.status')" clearable @change="loadTenants">
          <el-option :label="t('tenant.statusActive')" value="active" />
          <el-option :label="t('tenant.statusSuspended')" value="suspended" />
          <el-option :label="t('tenant.statusExpired')" value="expired" />
        </el-select>
        <div style="flex: 1"></div>
      </div>

      <el-table :data="tenantList" style="width: 100%">
        <el-table-column prop="name" :label="t('tenant.name')" />
        <el-table-column prop="code" :label="t('tenant.code')" width="120" />
        <el-table-column prop="status" :label="t('tenant.status')" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="users_count" :label="t('tenant.users')" width="100" />
        <el-table-column prop="projects_count" :label="t('tenant.projects')" width="100" />
        <el-table-column prop="max_users" :label="t('tenant.maxUsers')" width="100" />
        <el-table-column prop="expire_date" :label="t('tenant.expireDate')" width="120">
          <template #default="{ row }">
            {{ row.expire_date || '-' }}
          </template>
        </el-table-column>
        <el-table-column :label="t('common.operation')" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleSwitch(row)">{{ t('tenant.switch') }}</el-button>
            <el-button type="primary" link size="small" @click="handleEdit(row)">{{ t('common.edit') }}</el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">{{ t('common.delete') }}</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="loadTenants"
        @size-change="loadTenants"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <!-- 租户表单对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="700px" destroy-on-close>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item :label="t('tenant.name')" prop="name">
              <el-input v-model="form.name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('tenant.code')" prop="code">
              <el-input v-model="form.code" placeholder="e.g., acme" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item :label="t('tenant.description')" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item :label="t('tenant.maxUsers')" prop="max_users">
              <el-input-number v-model="form.max_users" :min="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('tenant.maxProjects')" prop="max_projects">
              <el-input-number v-model="form.max_projects" :min="1" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item :label="t('tenant.maxStorage')" prop="max_storage_gb">
              <el-input-number v-model="form.max_storage_gb" :min="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('tenant.expireDate')" prop="expire_date">
              <el-date-picker v-model="form.expireDate" type="date" placeholder="Select date" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item :label="t('tenant.status')" prop="status">
          <el-select v-model="form.status" style="width: 100%">
            <el-option :label="t('tenant.statusActive')" value="active" />
            <el-option :label="t('tenant.statusSuspended')" value="suspended" />
            <el-option :label="t('tenant.statusExpired')" value="expired" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" @click="handleSubmit">{{ t('common.confirm') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useI18n } from '@/i18n'
import { tenantApi } from '@/api/tenant'
import { useTenantStore } from '@/store/tenant'

const router = useRouter()
const { t } = useI18n()
const tenantStore = useTenantStore()
const formRef = ref()

const dialogVisible = ref(false)
const dialogTitle = ref('')
const isEdit = ref(false)

const tenantList = ref([])

const searchForm = reactive({
  keyword: '',
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
  code: '',
  description: '',
  max_users: 10,
  max_projects: 5,
  max_storage_gb: 10,
  expireDate: '',
  status: 'active'
})

const rules = {
  name: [{ required: true, message: 'Please enter tenant name', trigger: 'blur' }],
  code: [{ required: true, message: 'Please enter tenant code', trigger: 'blur' }]
}

function getStatusType(status) {
  const map = { active: 'success', suspended: 'warning', expired: 'danger' }
  return map[status] || 'info'
}

function getStatusText(status) {
  const map = { active: t('tenant.statusActive'), suspended: t('tenant.statusSuspended'), expired: t('tenant.statusExpired') }
  return map[status] || status
}

async function loadTenants() {
  const res = await tenantApi.getList({
    page: pagination.page,
    per_page: pagination.pageSize,
    ...searchForm
  })
  tenantList.value = res.data?.items || []
  pagination.total = res.data?.total || 0
}

function handleCreate() {
  isEdit.value = false
  dialogTitle.value = t('tenant.create')
  Object.assign(form, {
    id: null,
    name: '',
    code: '',
    description: '',
    max_users: 10,
    max_projects: 5,
    max_storage_gb: 10,
    expireDate: '',
    status: 'active'
  })
  dialogVisible.value = true
}

function handleEdit(row) {
  isEdit.value = true
  dialogTitle.value = t('tenant.edit')
  Object.assign(form, {
    id: row.id,
    name: row.name,
    code: row.code,
    description: row.description,
    max_users: row.max_users,
    max_projects: row.max_projects,
    max_storage_gb: row.max_storage_gb,
    expireDate: row.expire_date || '',
    status: row.status
  })
  dialogVisible.value = true
}

function handleDelete(row) {
  ElMessageBox.confirm(t('tenant.deleteConfirm'), t('common.confirm'), {
    type: 'warning'
  }).then(async () => {
    await tenantApi.delete(row.id)
    ElMessage.success(t('tenant.deleteSuccess'))
    loadTenants()
  })
}

function handleSubmit() {
  formRef.value.validate(async (valid) => {
    if (valid) {
      const data = {
        ...form,
        expire_date: form.expireDate ? new Date(form.expireDate).toISOString().split('T')[0] : null
      }
      delete data.expireDate

      if (isEdit.value) {
        await tenantApi.update(form.id, data)
        ElMessage.success(t('tenant.updateSuccess'))
      } else {
        await tenantApi.create(data)
        ElMessage.success(t('tenant.createSuccess'))
      }
      dialogVisible.value = false
      loadTenants()
    }
  })
}

async function handleSwitch(row) {
  try {
    await tenantApi.switch(row.id)
    // 更新租户存储
    await tenantStore.setCurrentTenant(row.id)
    ElMessage.success(t('tenant.switchSuccess'))
    router.push('/dashboard')
  } catch (error) {
    ElMessage.error(error.response?.data?.message || t('tenant.switchFailed'))
  }
}

onMounted(() => {
  loadTenants()
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

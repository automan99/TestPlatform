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
        <el-table-column :label="t('common.operation')" width="200" fixed="right">
          <template #default="{ row }">
            <el-tooltip content="成员管理" placement="top">
              <el-button type="info" link size="small" @click="handleMembers(row)">
                <el-icon><User /></el-icon>
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

    <!-- 成员管理对话框 -->
    <el-dialog v-model="membersDialogVisible" title="成员管理" width="800px" destroy-on-close>
      <div class="members-header">
        <el-button type="primary" :icon="Plus" @click="showAddMemberDialog">添加成员</el-button>
      </div>
      <el-table :data="memberList" style="width: 100%; margin-top: 16px">
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column prop="real_name" label="真实姓名" width="150" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="role" label="角色" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.role === 'owner'" type="danger">所有者</el-tag>
            <el-tag v-else-if="row.role === 'admin'" type="warning">管理员</el-tag>
            <el-tag v-else type="info">成员</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-tooltip content="移除" placement="top">
              <el-button type="danger" link size="small" @click="handleRemoveMember(row)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </el-tooltip>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <!-- 添加成员对话框 -->
    <el-dialog v-model="addMemberDialogVisible" title="添加成员" width="500px" destroy-on-close>
      <el-form :model="memberForm" ref="memberFormRef" label-width="100px">
        <el-form-item label="用户" prop="user_id" required>
          <el-select
            v-model="memberForm.user_id"
            placeholder="选择用户"
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="user in availableUsers"
              :key="user.id"
              :label="`${user.real_name || user.username} (${user.username})`"
              :value="user.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="memberForm.role" placeholder="选择角色" style="width: 100%">
            <el-option
              v-for="option in getAvailableRoleOptions()"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addMemberDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleAddMember">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, User, Edit, Delete } from '@element-plus/icons-vue'
import { useI18n } from '@/i18n'
import { tenantApi } from '@/api/tenant'
import { userApi } from '@/api/user'
import { useTenantStore } from '@/store/tenant'

const router = useRouter()
const { t } = useI18n()
const tenantStore = useTenantStore()
const formRef = ref()
const memberFormRef = ref()

const dialogVisible = ref(false)
const dialogTitle = ref('')
const isEdit = ref(false)
const membersDialogVisible = ref(false)
const addMemberDialogVisible = ref(false)
const currentTenantId = ref(null)

const tenantList = ref([])
const memberList = ref([])
const availableUsers = ref([])
const currentUserRole = ref('') // 当前用户在当前租户中的角色

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

const memberForm = reactive({
  user_id: null,
  role: 'member'
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

// 获取可用角色选项
function getAvailableRoleOptions() {
  const user = appStore.user
  // 超级管理员可以添加所有角色
  if (user?.role === 'super_admin') {
    return [
      { label: '成员', value: 'member' },
      { label: '管理员', value: 'admin' },
      { label: '所有者', value: 'owner' }
    ]
  }
  // 租户管理员只能添加普通成员
  return [
    { label: '成员', value: 'member' }
  ]
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

// 成员管理
async function handleMembers(row) {
  currentTenantId.value = row.id
  await loadMembers(row.id)
  membersDialogVisible.value = true
}

async function loadMembers(tenantId) {
  try {
    const res = await tenantApi.getMembers(tenantId)
    memberList.value = res.data || []
  } catch (error) {
    ElMessage.error('获取成员列表失败')
  }
}

async function showAddMemberDialog() {
  // 加载可用的用户列表（不在当前租户中的用户）
  try {
    const res = await userApi.getList({ per_page: 1000 })
    const allUsers = res.data?.items || []

    // 获取当前租户成员的用户ID
    const memberUserIds = memberList.value.map(m => m.user_id)

    // 过滤出不在当前租户中的用户
    availableUsers.value = allUsers.filter(u => !memberUserIds.includes(u.id))
  } catch (error) {
    ElMessage.error('获取用户列表失败')
  }

  memberForm.user_id = null
  memberForm.role = 'member'
  addMemberDialogVisible.value = true
}

async function handleAddMember() {
  if (!memberForm.user_id) {
    ElMessage.warning('请选择用户')
    return
  }

  try {
    await tenantApi.addMember(currentTenantId.value, {
      user_id: memberForm.user_id,
      role: memberForm.role
    })
    ElMessage.success('添加成员成功')
    addMemberDialogVisible.value = false
    await loadMembers(currentTenantId.value)
  } catch (error) {
    ElMessage.error('添加成员失败: ' + (error.response?.data?.message || error.message))
  }
}

async function handleRemoveMember(row) {
  ElMessageBox.confirm('确定要将该成员从租户中移除吗？', '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      await tenantApi.removeMember(currentTenantId.value, row.user_id)
      ElMessage.success('移除成员成功')
      await loadMembers(currentTenantId.value)
    } catch (error) {
      ElMessage.error('移除成员失败')
    }
  })
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
  gap: var(--space-3);
  margin-bottom: var(--space-4);
}
</style>

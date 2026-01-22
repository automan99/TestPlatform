<template>
  <div class="settings-page animate-fade-in-up">
    <!-- Page Header -->
    <div class="page-header">
      <h1 class="page-title">成员管理</h1>
      <p class="page-description">管理系统用户和权限</p>
    </div>

    <!-- Action Bar -->
    <div class="action-bar">
      <el-input
        v-model="searchKeyword"
        :placeholder="t('common.search')"
        clearable
        class="search-input"
        @change="loadUsers"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <div style="flex: 1"></div>
      <el-button type="primary" :icon="Plus" @click="handleCreateUser">新建用户</el-button>
    </div>

    <!-- User Table -->
    <div class="table-container">
      <el-table :data="userList" v-loading="loading" class="data-table" stripe>
        <el-table-column prop="username" :label="t('user.username')" width="120" show-overflow-tooltip />
        <el-table-column prop="real_name" :label="t('user.realName')" min-width="100" show-overflow-tooltip />
        <el-table-column prop="email" :label="t('user.email')" min-width="150" show-overflow-tooltip />
        <el-table-column prop="phone" :label="t('user.phone')" width="130" show-overflow-tooltip />
        <el-table-column prop="status" :label="t('user.status')" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
              {{ row.status === 'active' ? '激活' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_admin" :label="t('user.isAdmin')" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.is_admin" type="warning">管理员</el-tag>
            <el-tag v-else type="info">普通用户</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="oauth_provider" label="OAuth" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.oauth_provider" type="info">{{ row.oauth_provider }}</el-tag>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column :label="t('common.actions')" width="240" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEditUser(row)">{{ t('common.edit') }}</el-button>
            <el-button type="warning" link @click="handleResetPassword(row)">重置密码</el-button>
            <el-button type="danger" link @click="handleDeleteUser(row)">{{ t('common.delete') }}</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="loadUsers"
        @size-change="loadUsers"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </div>

    <!-- User Form Dialog -->
    <el-dialog v-model="userDialogVisible" :title="userDialogTitle" width="600px" destroy-on-close>
      <el-form :model="userForm" :rules="userRules" ref="userFormRef" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" :disabled="isEditUser" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!isEditUser">
          <el-input v-model="userForm.password" type="password" placeholder="不填则使用默认密码123456" />
        </el-form-item>
        <el-form-item label="真实姓名" prop="real_name">
          <el-input v-model="userForm.real_name" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="userForm.phone" />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="userForm.status">
            <el-radio label="active">激活</el-radio>
            <el-radio label="disabled">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="管理员">
          <el-switch v-model="userForm.is_admin" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="userDialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" @click="handleSubmitUser">{{ t('common.confirm') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'
import { useI18n } from '@/i18n'
import { userApi } from '@/api/user'

const { t } = useI18n()
const loading = ref(false)
const userList = ref([])
const searchKeyword = ref('')

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const userDialogVisible = ref(false)
const userDialogTitle = ref('')
const userFormRef = ref()
const isEditUser = ref(false)

const userForm = reactive({
  id: null,
  username: '',
  password: '',
  real_name: '',
  email: '',
  phone: '',
  status: 'active',
  is_admin: false
})

const userRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  real_name: [{ required: true, message: '请输入真实姓名', trigger: 'blur' }],
  email: [{ type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }]
}

async function loadUsers() {
  loading.value = true
  try {
    const res = await userApi.getList({
      page: pagination.page,
      per_page: pagination.pageSize,
      keyword: searchKeyword.value
    })
    userList.value = res.data.items || []
    pagination.total = res.data.total || 0
  } catch (error) {
    ElMessage.error('加载用户列表失败')
  } finally {
    loading.value = false
  }
}

function handleCreateUser() {
  isEditUser.value = false
  userDialogTitle.value = '新建用户'
  Object.assign(userForm, {
    id: null,
    username: '',
    password: '',
    real_name: '',
    email: '',
    phone: '',
    status: 'active',
    is_admin: false
  })
  userDialogVisible.value = true
}

function handleEditUser(row) {
  isEditUser.value = true
  userDialogTitle.value = '编辑用户'
  Object.assign(userForm, {
    id: row.id,
    username: row.username,
    real_name: row.real_name,
    email: row.email,
    phone: row.phone,
    status: row.status,
    is_admin: row.is_admin
  })
  userDialogVisible.value = true
}

async function handleSubmitUser() {
  userFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const data = { ...userForm }
        if (!data.password) {
          delete data.password
        }

        if (isEditUser.value) {
          await userApi.update(userForm.id, data)
          ElMessage.success('更新成功')
        } else {
          await userApi.create(data)
          ElMessage.success('创建成功')
        }
        userDialogVisible.value = false
        loadUsers()
      } catch (error) {
        ElMessage.error(error.response?.data?.message || '操作失败')
      }
    }
  })
}

function handleResetPassword(row) {
  ElMessageBox.confirm('确定要重置该用户的密码吗？重置后密码为：123456', '确认重置', {
    type: 'warning'
  }).then(async () => {
    try {
      await userApi.resetPassword(row.id)
      ElMessage.success('密码已重置为：123456')
    } catch (error) {
      ElMessage.error('重置失败')
    }
  })
}

function handleDeleteUser(row) {
  ElMessageBox.confirm('确定要删除该用户吗？', '确认删除', {
    type: 'warning'
  }).then(async () => {
    try {
      await userApi.delete(row.id)
      ElMessage.success('删除成功')
      loadUsers()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

onMounted(() => {
  loadUsers()
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

.table-container {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-4);
}

.data-table {
  width: 100%;
}

.text-muted {
  color: var(--color-text-muted);
}
</style>

<template>
  <div class="role-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">{{ t('role.title') }}</h1>
        <p class="page-description">{{ t('role.description') }}</p>
      </div>
      <el-button type="primary" :icon="Plus" @click="openCreateDialog">
        {{ t('role.createRole') }}
      </el-button>
    </div>

    <!-- Filters -->
    <div class="filter-section">
      <el-input
        v-model="searchKeyword"
        :placeholder="t('role.searchPlaceholder')"
        :prefix-icon="Search"
        clearable
        class="search-input"
        @input="handleSearch"
      />
    </div>

    <!-- Role Table -->
    <div class="table-section">
      <el-table
        v-loading="loading"
        :data="roleList"
        class="precision-table"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="50" />
        <el-table-column :label="t('role.name')" prop="name" min-width="150">
          <template #default="{ row }">
            <div class="role-name-cell">
              <el-icon class="role-icon" :class="getRoleIconClass(row)">
                <component :is="getRoleIcon(row)" />
              </el-icon>
              <span class="role-name">{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column :label="t('role.code')" prop="code" width="140" />
        <el-table-column :label="t('role.description')" prop="description" min-width="200" show-overflow-tooltip />
        <el-table-column :label="t('role.level')" prop="level" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getLevelType(row.level)" size="small">{{ row.level }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="t('role.users')" prop="user_count" width="100" align="center">
          <template #default="{ row }">
            <el-badge :value="row.user_count || 0" :max="99" class="user-badge" />
          </template>
        </el-table-column>
        <el-table-column :label="t('role.menus')" prop="menu_count" width="100" align="center">
          <template #default="{ row }">
            <el-badge :value="row.menu_count || 0" :max="99" type="info" />
          </template>
        </el-table-column>
        <el-table-column :label="t('role.status')" prop="is_enabled" width="100" align="center">
          <template #default="{ row }">
            <el-switch
              v-model="row.is_enabled"
              :disabled="row.is_system"
              @change="handleStatusChange(row)"
            />
          </template>
        </el-table-column>
        <el-table-column :label="t('common.actions')" width="280" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" :icon="Menu" @click="openMenusDialog(row)">
              {{ t('role.assignMenus') }}
            </el-button>
            <el-button link type="primary" :icon="User" @click="openUsersDialog(row)">
              {{ t('role.assignUsers') }}
            </el-button>
            <el-button
              v-if="!row.is_system"
              link
              type="primary"
              :icon="Edit"
              @click="openEditDialog(row)"
            >
              {{ t('common.edit') }}
            </el-button>
            <el-button
              v-if="!row.is_system"
              link
              type="danger"
              :icon="Delete"
              @click="handleDelete(row)"
            >
              {{ t('common.delete') }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.perPage"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="loadRoles"
          @size-change="loadRoles"
        />
      </div>
    </div>

    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="formDialogVisible"
      :title="isEdit ? t('role.editRole') : t('role.createRole')"
      width="600px"
      class="precision-dialog"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
        label-position="left"
      >
        <el-form-item :label="t('role.name')" prop="name">
          <el-input v-model="formData.name" :placeholder="t('role.namePlaceholder')" />
        </el-form-item>
        <el-form-item :label="t('role.code')" prop="code">
          <el-select
            v-model="formData.code"
            :placeholder="t('role.selectCode')"
            :disabled="isEdit"
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="option in roleCodeOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            >
              <div class="code-option">
                <span class="code-value">{{ option.value }}</span>
                <span class="code-label">{{ option.label }}</span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item :label="t('role.description')" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            :placeholder="t('role.descriptionPlaceholder')"
          />
        </el-form-item>
        <el-form-item :label="t('role.level')" prop="level">
          <el-input-number
            v-model="formData.level"
            :min="0"
            :max="999"
            :placeholder="t('role.levelPlaceholder')"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formDialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          {{ t('common.confirm') }}
        </el-button>
      </template>
    </el-dialog>

    <!-- Menus Assignment Dialog -->
    <el-dialog
      v-model="menusDialogVisible"
      :title="t('role.assignMenus') + ' - ' + currentRole?.name"
      width="700px"
      class="precision-dialog"
      @open="loadMenusForRole"
    >
      <div v-loading="menusLoading" class="menus-tree-container">
        <el-tree
          ref="menuTreeRef"
          :data="menuTreeData"
          :props="{ children: 'children', label: 'title' }"
          node-key="id"
          show-checkbox
          default-expand-all
          class="menu-tree"
        >
          <template #default="{ node, data }">
            <div class="menu-node">
              <el-icon v-if="data.icon" class="menu-icon">
                <component :is="iconMap[data.icon]" />
              </el-icon>
              <span class="menu-label">{{ node.label }}</span>
              <el-tag v-if="data.type" size="small" class="menu-type-tag">
                {{ t('menu.type' + data.type.charAt(0).toUpperCase() + data.type.slice(1)) }}
              </el-tag>
            </div>
          </template>
        </el-tree>
      </div>
      <template #footer>
        <el-button @click="menusDialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="menusSubmitting" @click="handleMenusSubmit">
          {{ t('common.save') }}
        </el-button>
      </template>
    </el-dialog>

    <!-- Users Assignment Dialog -->
    <el-dialog
      v-model="usersDialogVisible"
      :title="t('role.assignUsers') + ' - ' + currentRole?.name"
      width="800px"
      class="precision-dialog"
      @open="loadUsersForRole"
    >
      <div class="users-assignment">
        <div class="assignment-section">
          <div class="section-header">
            <h3>{{ t('role.allUsers') }}</h3>
            <el-input
              v-model="userSearchKeyword"
              :placeholder="t('role.searchUsers')"
              :prefix-icon="Search"
              clearable
              size="small"
              class="user-search"
            />
          </div>
          <div class="user-list available-users">
            <el-checkbox-group v-model="selectedUserIds">
              <el-checkbox
                v-for="user in filteredAvailableUsers"
                :key="user.id"
                :label="user.id"
                class="user-checkbox-item"
              >
                <div class="user-item">
                  <div class="user-avatar">{{ (user.real_name || user.username || '?').charAt(0) }}</div>
                  <div class="user-info">
                    <div class="user-name">{{ user.real_name || user.username }}</div>
                    <div class="user-email">{{ user.email }}</div>
                  </div>
                </div>
              </el-checkbox>
            </el-checkbox-group>
          </div>
        </div>
        <div class="assignment-divider">
          <el-button circle :icon="ArrowRight" />
        </div>
        <div class="assignment-section">
          <div class="section-header">
            <h3>{{ t('role.assignedUsers') }}</h3>
            <el-tag type="info">{{ selectedUserIds.length }}</el-tag>
          </div>
          <div class="user-list assigned-users">
            <div v-if="assignedUsersList.length === 0" class="empty-hint">
              {{ t('role.noUsersAssigned') }}
            </div>
            <div v-for="user in assignedUsersList" :key="user.id" class="user-item assigned">
              <div class="user-avatar">{{ (user.real_name || user.username || '?').charAt(0) }}</div>
              <div class="user-info">
                <div class="user-name">{{ user.real_name || user.username }}</div>
                <div class="user-email">{{ user.email }}</div>
              </div>
              <el-button
                link
                type="danger"
                :icon="Close"
                size="small"
                @click="removeUser(user.id)"
              />
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="usersDialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="usersSubmitting" @click="handleUsersSubmit">
          {{ t('common.save') }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { useI18n } from '@/i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Search, Edit, Delete, Menu, User, ArrowRight, Close,
  House, Document, Calendar, Monitor, CircleClose, DataAnalysis,
  Setting, FolderOpened, Connection, Files, OfficeBuilding, UserFilled,
  Star, Avatar, Trophy, Management
} from '@element-plus/icons-vue'
import { roleApi } from '@/api/role'
import { userApi } from '@/api/user'
import { menuApi } from '@/api/menu'

const { t } = useI18n()

// Icon mapping for menu tree
const iconMap = {
  House, Document, Calendar, Monitor, CircleClose, DataAnalysis,
  Setting, FolderOpened, Connection, Files, OfficeBuilding, UserFilled, Menu
}

// State
const loading = ref(false)
const roleList = ref([])
const searchKeyword = ref('')
const selectedIds = ref([])

const pagination = reactive({
  page: 1,
  perPage: 20,
  total: 0
})

// Form state
const formDialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref()
const formData = reactive({
  name: '',
  code: '',
  description: '',
  level: 0
})

// Role code options
const roleCodeOptions = computed(() => [
  { value: 'super_admin', label: t('role.codeSuperAdmin') },
  { value: 'admin', label: t('role.codeAdmin') },
  { value: 'tester', label: t('role.codeTester') },
  { value: 'developer', label: t('role.codeDeveloper') },
  { value: 'viewer', label: t('role.codeViewer') },
  { value: 'manager', label: t('role.codeManager') },
  { value: 'product_owner', label: t('role.codeProductOwner') }
])
const submitting = ref(false)

const formRules = {
  name: [{ required: true, message: t('role.nameRequired'), trigger: 'blur' }],
  code: [
    { required: true, message: t('role.codeRequired'), trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_-]+$/, message: t('role.codePattern'), trigger: 'blur' }
  ]
}

// Menus dialog state
const menusDialogVisible = ref(false)
const menusLoading = ref(false)
const menusSubmitting = ref(false)
const menuTreeRef = ref()
const menuTreeData = ref([])
const currentRoleMenus = ref([])
const currentRole = ref(null)

// Users dialog state
const usersDialogVisible = ref(false)
const usersSubmitting = ref(false)
const userSearchKeyword = ref('')
const allUsers = ref([])
const selectedUserIds = ref([])

// Methods
async function loadRoles() {
  loading.value = true
  try {
    const res = await roleApi.getList({
      page: pagination.page,
      per_page: pagination.perPage,
      keyword: searchKeyword.value || undefined
    })
    roleList.value = res.data.items || []
    pagination.total = res.data.total || 0
  } catch (error) {
    ElMessage.error(error.response?.data?.message || t('role.loadFailed'))
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.page = 1
  loadRoles()
}

function handleSelectionChange(selection) {
  selectedIds.value = selection.map(item => item.id)
}

function openCreateDialog() {
  isEdit.value = false
  formDialogVisible.value = true
}

function openEditDialog(row) {
  isEdit.value = true
  currentRole.value = row
  Object.assign(formData, {
    name: row.name,
    code: row.code,
    description: row.description || '',
    level: row.level || 0
  })
  formDialogVisible.value = true
}

function resetForm() {
  formRef.value?.resetFields()
  Object.assign(formData, {
    name: '',
    code: '',
    description: '',
    level: 0
  })
}

async function handleSubmit() {
  await formRef.value?.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      if (isEdit.value) {
        await roleApi.update(currentRole.value.id, formData)
        ElMessage.success(t('role.updateSuccess'))
      } else {
        await roleApi.create(formData)
        ElMessage.success(t('role.createSuccess'))
      }
      formDialogVisible.value = false
      loadRoles()
    } catch (error) {
      ElMessage.error(error.response?.data?.message || t('role.saveFailed'))
    } finally {
      submitting.value = false
    }
  })
}

async function handleStatusChange(row) {
  try {
    await roleApi.update(row.id, { is_enabled: row.is_enabled })
    ElMessage.success(t('role.statusUpdateSuccess'))
  } catch (error) {
    row.is_enabled = !row.is_enabled
    ElMessage.error(error.response?.data?.message || t('role.statusUpdateFailed'))
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(
      t('role.deleteConfirm', { name: row.name }),
      t('common.warning'),
      {
        confirmButtonText: t('common.confirm'),
        cancelButtonText: t('common.cancel'),
        type: 'warning'
      }
    )
    await roleApi.delete(row.id)
    ElMessage.success(t('role.deleteSuccess'))
    loadRoles()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.message || t('role.deleteFailed'))
    }
  }
}

// Menu assignment
async function openMenusDialog(row) {
  currentRole.value = row
  menusDialogVisible.value = true
}

async function loadMenusForRole() {
  menusLoading.value = true
  try {
    // Load all menus
    const menusRes = await menuApi.getTree()
    menuTreeData.value = buildMenuTree(menusRes.data || [])

    // Load role's current menus
    const roleMenusRes = await roleApi.getMenus(currentRole.value.id)
    currentRoleMenus.value = roleMenusRes.data.menu_ids || []

    // Set checked keys
    await Promise.resolve()
    menuTreeRef.value?.setCheckedKeys(currentRoleMenus.value)
  } catch (error) {
    ElMessage.error(error.response?.data?.message || t('role.loadMenusFailed'))
  } finally {
    menusLoading.value = false
  }
}

function buildMenuTree(flatList) {
  const map = {}
  const tree = []

  flatList.forEach(item => {
    map[item.id] = { ...item, children: [] }
  })

  flatList.forEach(item => {
    if (item.parent_id && map[item.parent_id]) {
      map[item.parent_id].children.push(map[item.id])
    } else {
      tree.push(map[item.id])
    }
  })

  return tree
}

async function handleMenusSubmit() {
  menusSubmitting.value = true
  try {
    const checkedKeys = menuTreeRef.value?.getCheckedKeys() || []
    const halfCheckedKeys = menuTreeRef.value?.getHalfCheckedKeys() || []
    const allMenuIds = [...checkedKeys, ...halfCheckedKeys]

    await roleApi.assignMenus(currentRole.value.id, allMenuIds)
    ElMessage.success(t('role.assignMenusSuccess'))
    menusDialogVisible.value = false
    loadRoles()
  } catch (error) {
    ElMessage.error(error.response?.data?.message || t('role.assignMenusFailed'))
  } finally {
    menusSubmitting.value = false
  }
}

// User assignment
async function openUsersDialog(row) {
  currentRole.value = row
  usersDialogVisible.value = true
}

async function loadUsersForRole() {
  try {
    // Load all users
    const usersRes = await userApi.getList({ per_page: 1000 })
    allUsers.value = usersRes.data.items || []

    // Load role's current users
    const roleUsersRes = await roleApi.getUsers(currentRole.value.id)
    selectedUserIds.value = roleUsersRes.data.user_ids || []
  } catch (error) {
    ElMessage.error(error.response?.data?.message || t('role.loadUsersFailed'))
  }
}

const filteredAvailableUsers = computed(() => {
  if (!userSearchKeyword.value) return allUsers.value
  const keyword = userSearchKeyword.value.toLowerCase()
  return allUsers.value.filter(user =>
    (user.real_name || user.username || '').toLowerCase().includes(keyword) ||
    (user.email || '').toLowerCase().includes(keyword)
  )
})

const assignedUsersList = computed(() => {
  return allUsers.value.filter(user => selectedUserIds.value.includes(user.id))
})

function removeUser(userId) {
  const index = selectedUserIds.value.indexOf(userId)
  if (index > -1) {
    selectedUserIds.value.splice(index, 1)
  }
}

async function handleUsersSubmit() {
  usersSubmitting.value = true
  try {
    await roleApi.assignUsers(currentRole.value.id, selectedUserIds.value)
    ElMessage.success(t('role.assignUsersSuccess'))
    usersDialogVisible.value = false
    loadRoles()
  } catch (error) {
    ElMessage.error(error.response?.data?.message || t('role.assignUsersFailed'))
  } finally {
    usersSubmitting.value = false
  }
}

// Utility functions
function getRoleIcon(row) {
  if (row.is_system) return Trophy
  if (row.level >= 100) return Star
  if (row.level >= 50) return Management
  return Avatar
}

function getRoleIconClass(row) {
  if (row.is_system) return 'role-icon-system'
  if (row.level >= 100) return 'role-icon-super-admin'
  if (row.level >= 50) return 'role-icon-admin'
  return 'role-icon-user'
}

function getLevelType(level) {
  if (level >= 100) return 'danger'
  if (level >= 50) return 'warning'
  return 'info'
}

onMounted(() => {
  loadRoles()
})
</script>

<style scoped>
.role-page {
  padding: var(--space-6);
  background: var(--color-bg);
  min-height: 100%;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--space-6);
  padding-bottom: var(--space-5);
  border-bottom: 1px solid var(--color-border);
}

.header-content {
  flex: 1;
}

.page-title {
  font-family: var(--font-display);
  font-size: 24px;
  font-weight: 700;
  color: var(--color-text);
  margin: 0 0 var(--space-2) 0;
  letter-spacing: -0.02em;
}

.page-description {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin: 0;
}

/* Filter Section */
.filter-section {
  display: flex;
  gap: var(--space-4);
  margin-bottom: var(--space-5);
}

.search-input {
  width: 320px;
}

/* Table Section */
.table-section {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.precision-table {
  width: 100%;
}

.role-name-cell {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.role-icon {
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.role-icon-system {
  color: #ef4444;
}

.role-icon-super-admin {
  color: #a855f7;
}

.role-icon-admin {
  color: #f59e0b;
}

.role-icon-user {
  color: var(--color-text-secondary);
}

.role-name {
  font-weight: 500;
  color: var(--color-text);
}

.code-option {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.code-value {
  font-family: var(--font-display);
  font-size: 12px;
  font-weight: 600;
  color: var(--color-primary);
  background: rgba(99, 102, 241, 0.1);
  padding: 2px 8px;
  border-radius: 4px;
  min-width: 100px;
}

.code-label {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.user-badge :deep(.el-badge__content) {
  background-color: var(--color-info);
}

.pagination-wrapper {
  padding: var(--space-4) var(--space-5);
  border-top: 1px solid var(--color-border);
  display: flex;
  justify-content: flex-end;
}

/* Menus Tree */
.menus-tree-container {
  max-height: 400px;
  overflow-y: auto;
  padding: var(--space-3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
}

.menu-tree {
  background: transparent;
}

.menu-node {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  flex: 1;
}

.menu-icon {
  color: var(--color-text-secondary);
}

.menu-label {
  flex: 1;
  font-weight: 500;
}

.menu-type-tag {
  font-size: 10px;
  height: 18px;
  padding: 0 6px;
}

/* Users Assignment */
.users-assignment {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: var(--space-4);
  min-height: 400px;
}

.assignment-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: var(--space-2);
  border-bottom: 1px solid var(--color-border);
}

.section-header h3 {
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
}

.user-search {
  width: 180px;
}

.user-list {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-2);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-bg);
}

.user-checkbox-item {
  display: flex;
  width: 100%;
  margin-bottom: var(--space-2);
  padding: var(--space-2);
  border-radius: var(--radius-sm);
  transition: background 0.15s ease;
}

.user-checkbox-item:hover {
  background: var(--color-bg-alt);
}

.user-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  flex: 1;
  margin-left: var(--space-2);
}

.user-item.assigned {
  padding: var(--space-3);
  background: var(--color-bg-alt);
  border-radius: var(--radius-sm);
  margin-left: 0;
}

.user-avatar {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: #ffffff;
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 600;
  border-radius: var(--radius-md);
  flex-shrink: 0;
}

.user-info {
  flex: 1;
  min-width: 0;
}

.user-name {
  font-weight: 500;
  color: var(--color-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-email {
  font-size: 12px;
  color: var(--color-text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.assignment-divider {
  display: flex;
  align-items: center;
  justify-content: center;
  padding-top: 60px;
}

.assignment-divider .el-button {
  background: var(--color-bg-alt);
  border-color: var(--color-border);
  color: var(--color-text-secondary);
}

.empty-hint {
  text-align: center;
  color: var(--color-text-muted);
  padding: var(--space-6);
  font-size: 13px;
}

/* Dialog */
:deep(.precision-dialog .el-dialog__header) {
  padding: var(--space-5) var(--space-6);
  border-bottom: 1px solid var(--color-border);
}

:deep(.precision-dialog .el-dialog__body) {
  padding: var(--space-6);
}

:deep(.precision-dialog .el-dialog__footer) {
  padding: var(--space-4) var(--space-6);
  border-top: 1px solid var(--color-border);
}
</style>

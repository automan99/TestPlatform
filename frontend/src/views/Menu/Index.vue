<template>
  <div class="menu-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>{{ t('menu.title') }}</span>
          <div class="header-actions">
            <el-input
              v-model="searchKeyword"
              :placeholder="t('menu.searchPlaceholder')"
              clearable
              style="width: 200px"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-button @click="expandAll">
              <el-icon><DCaret /></el-icon>
              {{ t('menu.expandAll') }}
            </el-button>
            <el-button @click="collapseAll">
              <el-icon><CaretTop /></el-icon>
              {{ t('menu.collapseAll') }}
            </el-button>
            <el-button type="primary" @click="openCreateDialog">
              <el-icon><Plus /></el-icon>
              {{ t('menu.addMenu') }}
            </el-button>
          </div>
        </div>
      </template>
      <el-table
        ref="menuTableRef"
        v-loading="loading"
        :data="filteredMenus"
        row-key="id"
        :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
        :expand-row-keys="expandedKeys"
        stripe
        class="data-table"
        height="500"
      >
        <el-table-column prop="title" :label="t('menu.menuName')" min-width="200">
          <template #default="{ row }">
            <div class="menu-name-cell">
              <el-icon v-if="row.icon" class="menu-icon">
                <component :is="iconMap[row.icon]" />
              </el-icon>
              <span>{{ row.title || row.name }}</span>
              <el-tag v-if="row.type === 'button'" size="small" type="info">
                {{ t('menu.button') }}
              </el-tag>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="code" :label="t('menu.code')" width="150" />

        <el-table-column prop="path" :label="t('menu.path')" width="200" />

        <el-table-column prop="icon" :label="t('menu.icon')" width="100">
          <template #default="{ row }">
            <el-icon v-if="row.icon">
              <component :is="iconMap[row.icon]" />
            </el-icon>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>

        <el-table-column prop="sort_order" :label="t('menu.sortOrder')" width="80" align="center" />

        <el-table-column :label="t('menu.status')" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_visible ? 'success' : 'info'" size="small">
              {{ row.is_visible ? t('menu.visible') : t('menu.hidden') }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column :label="t('common.actions')" width="240" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEditDialog(row)">
              {{ t('common.edit') }}
            </el-button>
            <el-button link type="primary" @click="openAddChildDialog(row)">
              {{ t('menu.addChild') }}
            </el-button>
            <el-button link type="danger" @click="handleDelete(row)">
              {{ t('common.delete') }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Menu Form Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      :close-on-click-modal="false"
      @close="resetForm"
    >
      <el-form
        ref="menuFormRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
        class="menu-form"
      >
        <el-form-item :label="t('menu.parentMenu')" prop="parent_id">
          <el-tree-select
            v-model="formData.parent_id"
            :data="menuTreeOptions"
            :props="{ label: 'title', value: 'id', children: 'children' }"
            :placeholder="t('menu.selectParent')"
            clearable
            check-strictly
          />
        </el-form-item>

        <el-form-item :label="t('menu.name')" prop="name">
          <el-input v-model="formData.name" :placeholder="t('menu.namePlaceholder')" />
        </el-form-item>

        <el-form-item :label="t('menu.title')" prop="title">
          <el-input v-model="formData.title" :placeholder="t('menu.titlePlaceholder')" />
        </el-form-item>

        <el-form-item :label="t('menu.code')" prop="code">
          <el-input v-model="formData.code" :placeholder="t('menu.codePlaceholder')" />
        </el-form-item>

        <el-form-item :label="t('menu.type')" prop="type">
          <el-select v-model="formData.type" :placeholder="t('menu.selectType')">
            <el-option :label="t('menu.typeMenu')" value="menu" />
            <el-option :label="t('menu.typeButton')" value="button" />
            <el-option :label="t('menu.typeLink')" value="link" />
          </el-select>
        </el-form-item>

        <el-form-item v-if="formData.type === 'menu' || formData.type === 'link'" :label="t('menu.path')" prop="path">
          <el-input v-model="formData.path" :placeholder="t('menu.pathPlaceholder')" />
        </el-form-item>

        <el-form-item :label="t('menu.icon')" prop="icon">
          <el-select v-model="formData.icon" :placeholder="t('menu.selectIcon')" clearable filterable>
            <el-option
              v-for="(icon, key) in iconMap"
              :key="key"
              :label="key"
              :value="key"
            >
              <div class="icon-option">
                <el-icon><component :is="icon" /></el-icon>
                <span>{{ key }}</span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item :label="t('menu.permission')" prop="permission">
          <el-input v-model="formData.permission" :placeholder="t('menu.permissionPlaceholder')" />
        </el-form-item>

        <el-form-item :label="t('menu.sortOrder')" prop="sort_order">
          <el-input-number v-model="formData.sort_order" :min="0" />
        </el-form-item>

        <el-form-item :label="t('menu.isVisible')" prop="is_visible">
          <el-switch v-model="formData.is_visible" />
        </el-form-item>

        <el-form-item :label="t('menu.isEnabled')" prop="is_enabled">
          <el-switch v-model="formData.is_enabled" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          {{ t('common.confirm') }}
        </el-button>
      </template>
    </el-dialog>

    <!-- Role Menu Assignment Dialog -->
    <el-dialog
      v-model="roleDialogVisible"
      :title="t('menu.assignMenus')"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form label-width="100px">
        <el-form-item :label="t('menu.selectRole')">
          <el-select v-model="selectedRoleId" :placeholder="t('menu.selectRole')" @change="loadRoleMenus">
            <el-option
              v-for="role in roles"
              :key="role.id"
              :label="role.name"
              :value="role.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item :label="t('menu.menus')">
          <el-tree
            ref="roleMenuTreeRef"
            :data="menuTreeData"
            :props="{ label: 'title', children: 'children' }"
            node-key="id"
            show-checkbox
            default-expand-all
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="roleDialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="assigning" @click="handleAssignMenus">
          {{ t('common.confirm') }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, h } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useI18n } from '@/i18n'
import { menuApi, roleApi } from '@/api/menu'
import {
  Search, Plus, DCaret, CaretTop, House, Document, Calendar,
  Monitor, CircleClose, DataAnalysis, Setting, FolderOpened,
  Connection, Files, OfficeBuilding, Menu, User, UserFilled,
  Operation, Bell
} from '@element-plus/icons-vue'

const { t } = useI18n()

// Icon mapping
const iconMap = {
  House, Document, Calendar, Monitor, CircleClose,
  DataAnalysis, Setting, FolderOpened, Connection, Files,
  OfficeBuilding, Menu, User, UserFilled, Operation, Bell
}

// Data
const loading = ref(false)
const menuList = ref([])
const menuTreeData = ref([])
const searchKeyword = ref('')
const expandedKeys = ref([])

// Dialog
const dialogVisible = ref(false)
const dialogTitle = ref('')
const isEdit = ref(false)
const menuFormRef = ref(null)
const submitting = ref(false)
const formData = ref({
  parent_id: null,
  name: '',
  title: '',
  code: '',
  type: 'menu',
  path: '',
  icon: '',
  permission: '',
  sort_order: 0,
  is_visible: true,
  is_enabled: true
})

// Form rules
const formRules = {
  name: [{ required: true, message: t('menu.nameRequired'), trigger: 'blur' }],
  code: [{ required: true, message: t('menu.codeRequired'), trigger: 'blur' }],
  type: [{ required: true, message: t('menu.typeRequired'), trigger: 'change' }]
}

// Role assignment
const roleDialogVisible = ref(false)
const roles = ref([])
const selectedRoleId = ref(null)
const roleMenuTreeRef = ref(null)
const assigning = ref(false)

// Computed
const filteredMenus = computed(() => {
  if (!searchKeyword.value) return menuTreeData.value
  const filterTree = (nodes) => {
    return nodes.filter(node => {
      const matchName = node.name?.toLowerCase().includes(searchKeyword.value.toLowerCase())
      const matchTitle = node.title?.toLowerCase().includes(searchKeyword.value.toLowerCase())
      const matchCode = node.code?.toLowerCase().includes(searchKeyword.value.toLowerCase())
      if (matchName || matchTitle || matchCode) return true
      if (node.children) {
        node.children = filterTree(node.children)
        return node.children.length > 0
      }
      return false
    })
  }
  return filterTree(JSON.parse(JSON.stringify(menuTreeData.value)))
})

const menuTreeOptions = computed(() => {
  const buildTree = (nodes, parentId = null) => {
    return nodes
      .filter(node => node.id !== parentId && node.parent_id === parentId)
      .map(node => ({
        ...node,
        children: buildTree(nodes, node.id)
      }))
  }
  return buildTree(menuList.value)
})

// Methods
async function loadMenus() {
  loading.value = true
  try {
    const res = await menuApi.getTree()
    // 后端已返回树形结构
    menuTreeData.value = res.data || []
    menuList.value = flattenMenuTree(menuTreeData.value)
  } catch (error) {
    ElMessage.error(error.response?.data?.message || t('menu.loadFailed'))
  } finally {
    loading.value = false
  }
}

function flattenMenuTree(nodes, result = []) {
  nodes.forEach(node => {
    result.push(node)
    if (node.children) {
      flattenMenuTree(node.children, result)
    }
  })
  return result
}

async function loadRoles() {
  try {
    const res = await roleApi.getList()
    roles.value = res.data?.roles || []
  } catch (error) {
    ElMessage.error(error.response?.data?.message || t('menu.loadRolesFailed'))
  }
}

function openCreateDialog() {
  isEdit.value = false
  dialogTitle.value = t('menu.addMenu')
  formData.value = {
    parent_id: null,
    name: '',
    title: '',
    code: '',
    type: 'menu',
    path: '',
    icon: '',
    permission: '',
    sort_order: 0,
    is_visible: true,
    is_enabled: true
  }
  dialogVisible.value = true
}

function openEditDialog(row) {
  isEdit.value = true
  dialogTitle.value = t('menu.editMenu')
  formData.value = {
    parent_id: row.parent_id,
    name: row.name,
    title: row.title,
    code: row.code,
    type: row.type,
    path: row.path,
    icon: row.icon,
    permission: row.permission,
    sort_order: row.sort_order,
    is_visible: row.is_visible,
    is_enabled: row.is_enabled
  }
  dialogVisible.value = true
}

function openAddChildDialog(row) {
  isEdit.value = false
  dialogTitle.value = t('menu.addChildMenu')
  formData.value = {
    parent_id: row.id,
    name: '',
    title: '',
    code: '',
    type: 'menu',
    path: '',
    icon: '',
    permission: '',
    sort_order: 0,
    is_visible: true,
    is_enabled: true
  }
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!menuFormRef.value) return

  await menuFormRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      if (isEdit.value) {
        await menuApi.update(currentEditId.value, formData.value)
        ElMessage.success(t('menu.updateSuccess'))
      } else {
        await menuApi.create(formData.value)
        ElMessage.success(t('menu.createSuccess'))
      }
      dialogVisible.value = false
      await loadMenus()
    } catch (error) {
      ElMessage.error(error.response?.data?.message || t('menu.saveFailed'))
    } finally {
      submitting.value = false
    }
  })
}

const currentEditId = ref(null)

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(
      t('menu.deleteConfirm'),
      t('common.warning'),
      {
        confirmButtonText: t('common.confirm'),
        cancelButtonText: t('common.cancel'),
        type: 'warning'
      }
    )

    await menuApi.delete(row.id)
    ElMessage.success(t('menu.deleteSuccess'))
    await loadMenus()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.message || t('menu.deleteFailed'))
    }
  }
}

function expandAll() {
  expandedKeys.value = menuList.value.map(item => item.id)
}

function collapseAll() {
  expandedKeys.value = []
}

function resetForm() {
  if (menuFormRef.value) {
    menuFormRef.value.resetFields()
  }
}

async function loadRoleMenus() {
  if (!selectedRoleId.value) return

  try {
    const res = await roleApi.getMenus(selectedRoleId.value)
    const menuIds = res.data?.menu_ids || []
    roleMenuTreeRef.value?.setCheckedKeys(menuIds)
  } catch (error) {
    ElMessage.error(error.response?.data?.message || t('menu.loadRoleMenusFailed'))
  }
}

async function handleAssignMenus() {
  if (!selectedRoleId.value) {
    ElMessage.warning(t('menu.selectRoleFirst'))
    return
  }

  assigning.value = true
  try {
    const checkedKeys = roleMenuTreeRef.value?.getCheckedKeys() || []
    await roleApi.assignMenus(selectedRoleId.value, checkedKeys)
    ElMessage.success(t('menu.assignSuccess'))
    roleDialogVisible.value = false
  } catch (error) {
    ElMessage.error(error.response?.data?.message || t('menu.assignFailed'))
  } finally {
    assigning.value = false
  }
}

onMounted(async () => {
  await loadMenus()
  await loadRoles()
})
</script>

<style scoped>
.menu-page {
  padding: var(--space-6);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-header > span {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text);
}

.header-actions {
  display: flex;
  gap: var(--space-3);
  align-items: center;
}

.data-table {
  width: 100%;
}

.menu-name-cell {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.menu-icon {
  font-size: 16px;
  color: var(--color-text-secondary);
}

/* 折叠按钮位置 - 确保在菜单图标之前 */
:deep(.el-table__expand-icon) {
  margin-right: var(--space-2);
  order: -1;
}

.icon-option {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.text-muted {
  color: var(--color-text-muted);
}

/* 子菜单缩进 */
:deep(.el-table__row .el-table__expand-icon) {
  color: var(--color-text-secondary);
}

:deep(.el-table__row.el-table__row--level-1 .cell) {
  padding-left: 48px !important;
}

:deep(.el-table__row.el-table__row--level-2 .cell) {
  padding-left: 72px !important;
}

:deep(.el-table__row.el-table__row--level-3 .cell) {
  padding-left: 96px !important;
}

:deep(.el-table__row) {
  cursor: pointer;
}

:deep(.el-table__row:hover) {
  background: var(--color-bg-alt);
}
</style>

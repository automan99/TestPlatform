<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <el-icon :size="24"><Monitor /></el-icon>
          <span>测试管理平台</span>
        </div>
      </template>

      <!-- 第一步：输入用户名密码 -->
      <el-form v-if="step === 1" :model="form" :rules="rules" ref="formRef">
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="用户名"
            :prefix-icon="'User'"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            :prefix-icon="'Lock'"
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleLogin" :loading="loading" style="width: 100%">
            下一步
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 第二步：选择租户 -->
      <div v-else-if="step === 2" class="tenant-select">
        <div class="tenant-title">请选择租户</div>
        <div class="tenant-list">
          <div
            v-for="tenant in tenantList"
            :key="tenant.id"
            class="tenant-item"
            :class="{ selected: selectedTenantId === tenant.id }"
            @click="selectedTenantId = tenant.id"
          >
            <div class="tenant-info">
              <el-icon :size="24" class="tenant-icon"><OfficeBuilding /></el-icon>
              <div class="tenant-details">
                <div class="tenant-name">{{ tenant.name }}</div>
                <div class="tenant-code">{{ tenant.code }}</div>
              </div>
            </div>
            <el-icon v-if="selectedTenantId === tenant.id" :size="20" class="check-icon">
              <Check />
            </el-icon>
          </div>
        </div>
        <el-button
          type="primary"
          @click="handleSelectTenant"
          :loading="loading"
          :disabled="!selectedTenantId"
          style="width: 100%; margin-top: 20px"
        >
          进入系统
        </el-button>
        <el-button @click="step = 1" style="width: 100%; margin-top: 10px">
          返回
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Monitor, OfficeBuilding, Check } from '@element-plus/icons-vue'
import { authApi } from '@/api/auth'
import { useTenantStore } from '@/store/tenant'

const router = useRouter()
const tenantStore = useTenantStore()
const formRef = ref()
const loading = ref(false)
const step = ref(1)
const tenantList = ref([])
const selectedTenantId = ref(null)

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

async function handleLogin() {
  formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        // 登录获取token和租户列表
        const loginRes = await authApi.login({
          username: form.username,
          password: form.password
        })

        const { token, user, tenants } = loginRes.data

        // 保存token和用户信息
        localStorage.setItem('token', token)
        localStorage.setItem('user', JSON.stringify(user))

        // 保存租户列表
        tenantList.value = tenants || []
        tenantStore.tenantList = tenants || []

        // 根据租户数量决定下一步
        if (tenants && tenants.length === 1) {
          // 只有一个租户，直接选择
          await selectTenantAndEnter(tenants[0])
        } else if (tenants && tenants.length > 1) {
          // 多个租户，显示选择界面
          step.value = 2
          loading.value = false
        } else {
          ElMessage.error('没有可用的租户')
          loading.value = false
        }
      } catch (error) {
        ElMessage.error(error.response?.data?.message || '登录失败')
        loading.value = false
      }
    }
  })
}

async function handleSelectTenant() {
  if (!selectedTenantId.value) {
    ElMessage.warning('请选择租户')
    return
  }
  const tenant = tenantList.value.find(t => t.id === selectedTenantId.value)
  if (tenant) {
    await selectTenantAndEnter(tenant)
  }
}

async function selectTenantAndEnter(tenant) {
  loading.value = true
  try {
    // 选择租户
    const selectRes = await authApi.selectTenant(tenant.id)

    // 保存租户信息
    localStorage.setItem('currentTenantId', tenant.id)
    tenantStore.currentTenant = selectRes.data || tenant

    ElMessage.success('登录成功')
    router.push('/')
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '选择租户失败')
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 400px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 20px;
  font-weight: bold;
}

.tenant-select {
  padding: 10px 0;
}

.tenant-title {
  text-align: center;
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 20px;
  color: #303133;
}

.tenant-list {
  max-height: 300px;
  overflow-y: auto;
}

.tenant-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px;
  margin-bottom: 10px;
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.tenant-item:hover {
  border-color: #409eff;
  background: #f5f7fa;
}

.tenant-item.selected {
  border-color: #409eff;
  background: #ecf5ff;
}

.tenant-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.tenant-icon {
  color: #409eff;
}

.tenant-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.tenant-name {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.tenant-code {
  font-size: 12px;
  color: #909399;
}

.check-icon {
  color: #409eff;
}
</style>

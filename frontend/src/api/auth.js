import request from './index'

// 认证相关API
export const authApi = {
  // 登录
  login: (data) => request.post('/auth/login', data),

  // 获取用户的租户列表
  getMyTenants: () => request.get('/auth/tenants'),

  // 选择租户
  selectTenant: (tenantId) => request.post('/auth/select-tenant', { tenant_id: tenantId })
}

import request from './index'

// 租户管理API
export const tenantApi = {
  // 获取租户列表
  getList: (params) => request.get('/tenants', { params }),

  // 获取租户详情
  getDetail: (id) => request.get(`/tenants/${id}`),

  // 创建租户
  create: (data) => request.post('/tenants', data),

  // 更新租户
  update: (id, data) => request.put(`/tenants/${id}`, data),

  // 删除租户
  delete: (id) => request.delete(`/tenants/${id}`),

  // 获取租户用户列表
  getUsers: (tenantId) => request.get(`/tenants/${tenantId}/users`),

  // 切换租户
  switch: (tenantId) => request.post('/tenants/switch', { tenant_id: tenantId }),

  // 获取我的租户列表
  getMyTenants: () => request.get('/tenants/my')
}

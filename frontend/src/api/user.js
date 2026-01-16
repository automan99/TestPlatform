import request from './index'

// 用户管理API
export const userApi = {
  // 获取用户列表
  getList: (params) => request.get('/users', { params }),

  // 获取用户详情
  getDetail: (id) => request.get(`/users/${id}`),

  // 创建用户
  create: (data) => request.post('/users', data),

  // 更新用户
  update: (id, data) => request.put(`/users/${id}`, data),

  // 删除用户
  delete: (id) => request.delete(`/users/${id}`),

  // 重置密码
  resetPassword: (id) => request.post(`/users/${id}/reset-password`)
}

import request from './index'

// 测试环境API
export const environmentApi = {
  // 获取测试环境列表
  getList: (params) => request.get('/environments', { params }),

  // 获取测试环境详情
  getDetail: (id) => request.get(`/environments/${id}`),

  // 创建测试环境
  create: (data) => request.post('/environments', data),

  // 更新测试环境
  update: (id, data) => request.put(`/environments/${id}`, data),

  // 删除测试环境
  delete: (id) => request.delete(`/environments/${id}`)
}

// 环境资源API
export const resourceApi = {
  // 获取环境资源列表
  getList: (params) => request.get('/environment-resources', { params }),

  // 获取环境资源详情
  getDetail: (id) => request.get(`/environment-resources/${id}`),

  // 创建环境资源
  create: (data) => request.post('/environment-resources', data),

  // 更新环境资源
  update: (id, data) => request.put(`/environment-resources/${id}`, data),

  // 删除环境资源
  delete: (id) => request.delete(`/environment-resources/${id}`),

  // 更新资源状态
  updateStatus: (id, data) => request.put(`/environment-resources/${id}/status`, data)
}

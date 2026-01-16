import request from './index'

// 测试计划API
export const testPlanApi = {
  // 获取测试计划列表
  getList: (params) => request.get('/test-plans', { params }),

  // 获取测试计划详情
  getDetail: (id) => request.get(`/test-plans/${id}`),

  // 创建测试计划
  create: (data) => request.post('/test-plans', data),

  // 更新测试计划
  update: (id, data) => request.put(`/test-plans/${id}`, data),

  // 删除测试计划
  delete: (id) => request.delete(`/test-plans/${id}`),

  // 添加用例到计划
  addCases: (id, data) => request.post(`/test-plans/${id}/add-cases`, data),

  // 从计划移除用例
  removeCases: (id, data) => request.post(`/test-plans/${id}/remove-cases`, data),

  // 执行测试计划
  execute: (id, data) => request.post(`/test-plans/${id}/execute`, data)
}

// 测试执行API
export const testExecutionApi = {
  // 获取测试执行列表
  getList: (params) => request.get('/test-executions', { params }),

  // 获取测试执行详情
  getDetail: (id) => request.get(`/test-executions/${id}`),

  // 创建测试执行
  create: (data) => request.post('/test-executions', data),

  // 更新测试执行
  update: (id, data) => request.put(`/test-executions/${id}`, data)
}

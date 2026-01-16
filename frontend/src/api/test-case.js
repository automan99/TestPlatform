import request from './index'

// 测试套件API
export const testSuiteApi = {
  // 获取测试套件树
  getTree: (params) => request.get('/test-suites', { params }),

  // 创建测试套件
  create: (data) => request.post('/test-suites', data),

  // 更新测试套件
  update: (id, data) => request.put(`/test-suites/${id}`, data),

  // 删除测试套件
  delete: (id) => request.delete(`/test-suites/${id}`)
}

// 测试用例API
export const testCaseApi = {
  // 获取测试用例列表
  getList: (params) => request.get('/test-cases', { params }),

  // 获取测试用例详情
  getDetail: (id) => request.get(`/test-cases/${id}`),

  // 创建测试用例
  create: (data) => request.post('/test-cases', data),

  // 更新测试用例
  update: (id, data) => request.put(`/test-cases/${id}`, data),

  // 删除测试用例
  delete: (id) => request.delete(`/test-cases/${id}`),

  // 批量删除测试用例
  batchDelete: (data) => request.post('/test-cases/batch-delete', data),

  // 批量移动测试用例
  batchMove: (data) => request.post('/test-cases/batch-move', data)
}

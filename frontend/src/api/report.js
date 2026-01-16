import request from './index'

// 测试报告API
export const reportApi = {
  // 获取测试报告列表
  getList: (params) => request.get('/test-reports', { params }),

  // 获取测试报告详情
  getDetail: (id) => request.get(`/test-reports/${id}`),

  // 创建测试报告
  create: (data) => request.post('/test-reports', data),

  // 更新测试报告
  update: (id, data) => request.put(`/test-reports/${id}`, data),

  // 删除测试报告
  delete: (id) => request.delete(`/test-reports/${id}`),

  // 导出报告
  export: (id, data) => request.post(`/test-reports/${id}/export`, data),

  // 获取报告模板列表
  getTemplates: (params) => request.get('/test-reports/templates', { params }),

  // 创建报告模板
  createTemplate: (data) => request.post('/test-reports/templates', data)
}

// 报告度量指标API
export const reportMetricApi = {
  // 获取度量指标列表
  getList: (params) => request.get('/report-metrics', { params }),

  // 创建度量指标
  create: (data) => request.post('/report-metrics', data),

  // 更新度量指标
  update: (id, data) => request.put(`/report-metrics/${id}`, data),

  // 删除度量指标
  delete: (id) => request.delete(`/report-metrics/${id}`),

  // 批量创建度量指标
  batchCreate: (data) => request.post('/report-metrics/batch', data)
}

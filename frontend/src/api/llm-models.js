/**
 * LLM模型配置管理 API
 */
import request from './index'

export const llmModelApi = {
  // 获取模型列表
  getList(params) {
    return request.get('/llm-models', { params })
  },

  // 获取模型详情
  getById(id) {
    return request.get(`/llm-models/${id}`)
  },

  // 创建模型
  create(data) {
    return request.post('/llm-models', data)
  },

  // 更新模型
  update(id, data) {
    return request.put(`/llm-models/${id}`, data)
  },

  // 删除模型
  delete(id) {
    return request.delete(`/llm-models/${id}`)
  },

  // 测试模型连接
  test(id) {
    return request.post(`/llm-models/${id}/test`)
  },

  // 获取支持的提供商列表
  getProviders() {
    return request.get('/llm-models/providers')
  }
}

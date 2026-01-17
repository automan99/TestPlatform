import request from './index'

// AI测试执行API
export const aiExecutionApi = {
  // 启动AI执行
  start: (data) => request.post('/ai-execution/start', data),

  // 获取执行状态
  getStatus: (executionId) => request.get(`/ai-execution/${executionId}/status`),

  // 停止执行
  stop: (executionId) => request.post(`/ai-execution/${executionId}/stop`)
}

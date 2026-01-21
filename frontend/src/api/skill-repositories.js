import request from './index'

// Git凭证 API
export const gitCredentialApi = {
  // 获取Git凭证列表
  getList: () => request.get('/skill-repositories/credentials'),

  // 获取Git凭证详情
  getDetail: (id) => request.get(`/skill-repositories/credentials/${id}`),

  // 创建Git凭证
  create: (data) => request.post('/skill-repositories/credentials', data),

  // 更新Git凭证
  update: (id, data) => request.put(`/skill-repositories/credentials/${id}`, data),

  // 删除Git凭证
  delete: (id) => request.delete(`/skill-repositories/credentials/${id}`)
}

// 技能仓库 API
export const skillRepositoryApi = {
  // 获取技能仓库列表
  getList: (params) => request.get('/skill-repositories', { params }),

  // 获取技能仓库详情
  getDetail: (id) => request.get(`/skill-repositories/${id}`),

  // 创建技能仓库
  create: (data) => request.post('/skill-repositories', data),

  // 更新技能仓库
  update: (id, data) => request.put(`/skill-repositories/${id}`, data),

  // 删除技能仓库
  delete: (id) => request.delete(`/skill-repositories/${id}`),

  // 同步技能仓库
  sync: (id, user) => request.post(`/skill-repositories/${id}/sync`, {}, { params: { user } }),

  // 获取同步日志
  getSyncLogs: (id, params) => request.get(`/skill-repositories/${id}/sync-logs`, { params }),

  // 触发Webhook
  triggerWebhook: (id) => request.post(`/skill-repositories/webhook/${id}`)
}

// Git技能 API
export const gitSkillApi = {
  // 获取Git技能列表
  getList: (params) => request.get('/git-skills', { params }),

  // 获取Git技能详情
  getDetail: (id) => request.get(`/git-skills/${id}`),

  // 更新Git技能
  update: (id, data) => request.put(`/git-skills/${id}`, data),

  // 执行Git技能
  execute: (id, data) => request.post(`/git-skills/${id}/execute`, data)
}

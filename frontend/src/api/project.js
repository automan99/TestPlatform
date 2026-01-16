import request from './index'

// 项目管理API
export const projectApi = {
  // 获取项目列表
  getList: (params) => request.get('/projects/', { params }),

  // 获取项目详情
  getDetail: (id) => request.get(`/projects/${id}`),

  // 创建项目
  create: (data) => request.post('/projects/', data),

  // 更新项目
  update: (id, data) => request.put(`/projects/${id}`, data),

  // 删除项目
  delete: (id) => request.delete(`/projects/${id}`),

  // 获取项目统计信息
  getStatistics: (id) => request.get(`/projects/${id}/statistics`),

  // 切换项目
  switch: (projectId) => request.post('/projects/switch', { project_id: projectId })
}

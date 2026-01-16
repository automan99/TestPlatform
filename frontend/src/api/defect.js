import request from './index'

// 缺陷工作流API
export const defectWorkflowApi = {
  // 获取工作流状态列表
  getList: (params) => request.get('/defect-workflows', { params }),

  // 创建工作流状态
  create: (data) => request.post('/defect-workflows', data),

  // 更新工作流状态
  update: (id, data) => request.put(`/defect-workflows/${id}`, data),

  // 删除工作流状态
  delete: (id) => request.delete(`/defect-workflows/${id}`)
}

// 缺陷API
export const defectApi = {
  // 获取缺陷列表
  getList: (params) => request.get('/defects', { params }),

  // 获取缺陷详情
  getDetail: (id) => request.get(`/defects/${id}`),

  // 创建缺陷
  create: (data) => request.post('/defects', data),

  // 更新缺陷
  update: (id, data) => request.put(`/defects/${id}`, data),

  // 删除缺陷
  delete: (id) => request.delete(`/defects/${id}`),

  // 分配缺陷
  assign: (id, data) => request.post(`/defects/${id}/assign`, data)
}

// 缺陷评论API
export const defectCommentApi = {
  // 获取缺陷评论列表
  getList: (params) => request.get('/defect-comments', { params }),

  // 创建评论
  create: (data) => request.post('/defect-comments', data),

  // 更新评论
  update: (id, data) => request.put(`/defect-comments/${id}`, data),

  // 删除评论
  delete: (id) => request.delete(`/defect-comments/${id}`)
}

import request from './index'

// MCP Server API
export const mcpServerApi = {
  // 获取MCP Server列表
  getList: (params) => request.get('/mcp-servers', { params }),

  // 获取MCP Server详情
  getDetail: (id) => request.get(`/mcp-servers/${id}`),

  // 创建MCP Server
  create: (data) => request.post('/mcp-servers', data),

  // 更新MCP Server
  update: (id, data) => request.put(`/mcp-servers/${id}`, data),

  // 删除MCP Server
  delete: (id) => request.delete(`/mcp-servers/${id}`),

  // 测试MCP连接
  testConnection: (id) => request.post(`/mcp-servers/${id}/test`),

  // 同步MCP工具和资源
  sync: (id) => request.post(`/mcp-servers/${id}/sync`),

  // 获取MCP Server工具列表
  getTools: (id) => request.get(`/mcp-servers/${id}/tools`),

  // 调用MCP Server工具
  invokeTool: (id, toolName, data) => request.post(`/mcp-servers/${id}/tools/${toolName}/invoke`, data),

  // 获取MCP Server资源列表
  getResources: (id) => request.get(`/mcp-servers/${id}/resources`)
}

// Skill API
export const skillApi = {
  // 获取Skill列表
  getList: (params) => request.get('/skills', { params }),

  // 获取Skill详情
  getDetail: (id) => request.get(`/skills/${id}`),

  // 创建Skill
  create: (data) => request.post('/skills', data),

  // 更新Skill
  update: (id, data) => request.put(`/skills/${id}`, data),

  // 删除Skill
  delete: (id) => request.delete(`/skills/${id}`),

  // 执行Skill
  execute: (id, data) => request.post(`/skills/${id}/execute`, data),

  // 获取版本历史
  getVersionHistory: (id) => request.get(`/skills/${id}/version-history`)
}

import request from './index'

// OAuth2 认证API
export const oauthApi = {
  // 获取OAuth配置
  getConfig: () => request.get('/oauth/config'),

  // 更新OAuth配置
  updateConfig: (data) => request.post('/oauth/config', data),

  // 获取授权URL
  getAuthorizeUrl: (provider) => request.get(`/oauth/${provider}/authorize`),

  // OAuth回调
  callback: (provider, params) => request.get(`/oauth/${provider}/callback`, { params })
}

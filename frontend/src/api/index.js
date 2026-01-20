import axios from 'axios'
import { ElMessage } from 'element-plus'
import QS from 'qs'

let errorMessageShown = false
let redirecting = false

const request = axios.create({
  baseURL: '/api',
  timeout: 30000,
  paramsSerializer: (params) => {
    return QS.stringify(params, { arrayFormat: 'comma' })
  }
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 可以在这里添加token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // 添加租户ID到请求头
    const tenantId = localStorage.getItem('currentTenantId')
    if (tenantId) {
      config.headers['X-Tenant-ID'] = tenantId
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    const res = response.data

    if (res.success === false) {
      ElMessage.error(res.message || '请求失败')
      return Promise.reject(new Error(res.message || '请求失败'))
    }

    return res
  },
  (error) => {
    // 防止多个错误消息同时显示
    if (!errorMessageShown) {
      const message = error.response?.data?.message || error.message || '网络错误'
      ElMessage.error(message)
      errorMessageShown = true
      setTimeout(() => {
        errorMessageShown = false
      }, 1000)
    }

    // 处理401未授权
    if (error.response?.status === 401 && !redirecting) {
      redirecting = true
      localStorage.removeItem('token')
      setTimeout(() => {
        window.location.href = '/login'
      }, 100)
    }

    return Promise.reject(error)
  }
)

export default request

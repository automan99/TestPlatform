import axios from 'axios'
import { ElMessage } from 'element-plus'

let errorMessageShown = false
let redirecting = false

// Custom params serializer to handle arrays as comma-separated values
function serializeParams(params) {
  const parts = []
  for (const key in params) {
    const value = params[key]
    if (value === null || value === undefined) {
      continue
    }
    if (Array.isArray(value)) {
      // Serialize arrays as comma-separated: key=1,2,3
      parts.push(`${encodeURIComponent(key)}=${encodeURIComponent(value.join(','))}`)
    } else {
      parts.push(`${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
    }
  }
  return parts.join('&')
}

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000,
  paramsSerializer: serializeParams,
  headers: {
    'Content-Type': 'application/json'
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

import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  withCredentials: true  // 重要：发送Cookie用于Session认证
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('API Error:', error)
    
    // 处理401未授权错误
    if (error.response && error.response.status === 401) {
      // 如果不是登录页，跳转到登录页
      if (window.location.pathname !== '/login') {
        localStorage.removeItem('user')
        window.location.href = '/login'
      }
    }
    
    return Promise.reject(error)
  }
)

// API 接口
export default {
  // 认证相关
  login(credentials) {
    return api.post('/auth/login/', credentials)
  },
  logout() {
    return api.post('/auth/logout/')
  },
  getCurrentUser() {
    return api.get('/auth/me/')
  },
  register(userData) {
    return api.post('/auth/register/', userData)
  },
  
  // 抽奖相关
  getLotteries(page = 1) {
    return api.get('/lotteries/', {
      params: { page }
    })
  },
  getActiveLotteries() {
    return api.get('/lotteries/active/')
  },
  getLottery(id) {
    return api.get(`/lotteries/${id}/`)
  },
  createLottery(data) {
    // 检查是否为 FormData（包含文件上传）
    const isFormData = data instanceof FormData
    return api.post('/lotteries/', data, {
      headers: isFormData ? { 'Content-Type': 'multipart/form-data' } : {}
    })
  },
  updateLottery(id, data) {
    // 检查是否为 FormData（包含文件上传）
    const isFormData = data instanceof FormData
    return api.put(`/lotteries/${id}/`, data, {
      headers: isFormData ? { 'Content-Type': 'multipart/form-data' } : {}
    })
  },
  cancelLottery(id) {
    return api.post(`/lotteries/${id}/cancel/`)
  },
  drawLottery(id) {
    return api.post(`/lotteries/${id}/draw/`)
  },
  
  // 统计相关
  getStatistics() {
    return api.get('/lotteries/statistics/')
  },
  
  // 用户相关
  getOrCreateUser(data) {
    return api.post('/users/get_or_create/', data)
  }
}

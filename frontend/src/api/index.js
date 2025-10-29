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
        
        // 检查是否是会话超时
        const errorData = error.response.data
        if (errorData && errorData.code === 'SESSION_TIMEOUT') {
          // 会话超时，显示提示
          import('element-plus').then(ElementPlus => {
            ElementPlus.ElMessage.warning({
              message: '会话已超时（1小时无活动），请重新登录',
              duration: 3000
            })
          })
          
          // 延迟跳转，让用户看到提示
          setTimeout(() => {
            window.location.href = '/login'
          }, 1000)
        } else {
          // 其他401错误，直接跳转
          window.location.href = '/login'
        }
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
  changePassword(data) {
    return api.post('/auth/change-password/', data)
  },
  
  // Bot配置相关
  getBotConfig() {
    return api.get('/bot-config/')
  },
  updateBotConfig(data) {
    return api.put('/bot-config/', data)
  },
  deleteBotConfig() {
    return api.delete('/bot-config/')
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
  },
  
  // 登录记录相关
  getLoginRecords() {
    return api.get('/login-records/')
  },
  getLoginRecord(id) {
    return api.get(`/login-records/${id}/`)
  }
}

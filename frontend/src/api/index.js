import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
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
    return Promise.reject(error)
  }
)

// API 接口
export default {
  // 抽奖相关
  getLotteries() {
    return api.get('/lotteries/')
  },
  getActiveLotteries() {
    return api.get('/lotteries/active/')
  },
  getLottery(id) {
    return api.get(`/lotteries/${id}/`)
  },
  createLottery(data) {
    return api.post('/lotteries/', data)
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

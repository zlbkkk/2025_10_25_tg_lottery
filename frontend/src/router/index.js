import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import LotteryList from '../views/LotteryList.vue'
import LotteryDetail from '../views/LotteryDetail.vue'
import CreateLottery from '../views/CreateLottery.vue'
import Statistics from '../views/Statistics.vue'
import Login from '../views/Login.vue'
import BotConfig from '../views/BotConfig.vue'
import LoginRecords from '../views/LoginRecords.vue'
import api from '../api'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { public: true }  // 公开页面，不需要登录
  },
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/lotteries',
    name: 'LotteryList',
    component: LotteryList
  },
  {
    path: '/lotteries/:id',
    name: 'LotteryDetail',
    component: LotteryDetail
  },
  {
    path: '/create',
    name: 'CreateLottery',
    component: CreateLottery
  },
  {
    path: '/create/:id',
    name: 'EditLottery',
    component: CreateLottery
  },
  {
    path: '/statistics',
    name: 'Statistics',
    component: Statistics
  },
  {
    path: '/bot-config',
    name: 'BotConfig',
    component: BotConfig
  },
  {
    path: '/login-records',
    name: 'LoginRecords',
    component: LoginRecords,
    meta: { requiresAdmin: true }  // 需要管理员权限
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫：检查登录状态和管理员权限
router.beforeEach(async (to, from, next) => {
  // 公开页面直接放行（包括登录页）
  if (to.meta.public) {
    next()
    return
  }
  
  // 如果要跳转到登录页，直接放行，不检查登录状态
  if (to.path === '/login') {
    next()
    return
  }
  
  // 检查是否登录
  try {
    const user = await api.getCurrentUser()
    
    // 检查是否需要管理员权限
    if (to.meta.requiresAdmin && user.username !== 'admin') {
      // 非管理员尝试访问管理员页面，重定向到首页
      next('/')
      return
    }
    
    next()
  } catch (error) {
    // 未登录，跳转到登录页
    next('/login')
  }
})

export default router

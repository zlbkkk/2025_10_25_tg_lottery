import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import LotteryList from '../views/LotteryList.vue'
import LotteryDetail from '../views/LotteryDetail.vue'
import CreateLottery from '../views/CreateLottery.vue'
import Statistics from '../views/Statistics.vue'
import Login from '../views/Login.vue'
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
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫：检查登录状态
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
    await api.getCurrentUser()
    next()
  } catch (error) {
    // 未登录，跳转到登录页
    next('/login')
  }
})

export default router

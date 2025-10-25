import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import LotteryList from '../views/LotteryList.vue'
import LotteryDetail from '../views/LotteryDetail.vue'
import CreateLottery from '../views/CreateLottery.vue'
import Statistics from '../views/Statistics.vue'

const routes = [
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
    path: '/statistics',
    name: 'Statistics',
    component: Statistics
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

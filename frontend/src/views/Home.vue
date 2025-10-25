<template>
  <div class="home">
    <el-card class="welcome-card">
      <h2>欢迎使用抽奖管理系统</h2>
      <p>这是一个功能完整的 Telegram 抽奖机器人管理系统</p>
      
      <el-row :gutter="20" style="margin-top: 30px;">
        <el-col :span="6">
          <el-statistic title="总抽奖数" :value="statistics.total_lotteries">
            <template #prefix>
              <el-icon><Trophy /></el-icon>
            </template>
          </el-statistic>
        </el-col>
        <el-col :span="6">
          <el-statistic title="进行中" :value="statistics.active_lotteries">
            <template #prefix>
              <el-icon><Timer /></el-icon>
            </template>
          </el-statistic>
        </el-col>
        <el-col :span="6">
          <el-statistic title="总参与人次" :value="statistics.total_participants">
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-statistic>
        </el-col>
        <el-col :span="6">
          <el-statistic title="总中奖人数" :value="statistics.total_winners">
            <template #prefix>
              <el-icon><Star /></el-icon>
            </template>
          </el-statistic>
        </el-col>
      </el-row>
    </el-card>

    <el-card style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>快速操作</span>
        </div>
      </template>
      <el-row :gutter="20">
        <el-col :span="8">
          <el-button type="primary" size="large" @click="$router.push('/create')" style="width: 100%;">
            <el-icon><Plus /></el-icon>
            创建新抽奖
          </el-button>
        </el-col>
        <el-col :span="8">
          <el-button type="success" size="large" @click="$router.push('/lotteries')" style="width: 100%;">
            <el-icon><List /></el-icon>
            查看抽奖列表
          </el-button>
        </el-col>
        <el-col :span="8">
          <el-button type="info" size="large" @click="$router.push('/statistics')" style="width: 100%;">
            <el-icon><DataAnalysis /></el-icon>
            数据统计
          </el-button>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script>
import api from '../api'

export default {
  name: 'Home',
  data() {
    return {
      statistics: {
        total_lotteries: 0,
        active_lotteries: 0,
        finished_lotteries: 0,
        total_participants: 0,
        total_winners: 0
      }
    }
  },
  mounted() {
    this.loadStatistics()
  },
  methods: {
    async loadStatistics() {
      try {
        this.statistics = await api.getStatistics()
      } catch (error) {
        console.error('加载统计数据失败:', error)
      }
    }
  }
}
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-card {
  text-align: center;
}

.welcome-card h2 {
  color: #409EFF;
  margin-bottom: 10px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>

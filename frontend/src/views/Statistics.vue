<template>
  <div class="statistics">
    <el-card>
      <template #header>
        <span>数据统计</span>
      </template>

      <el-row :gutter="20">
        <el-col :span="8">
          <el-card shadow="hover">
            <el-statistic title="总抽奖数" :value="statistics.total_lotteries">
              <template #prefix>
                <el-icon style="vertical-align: middle"><Trophy /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card shadow="hover">
            <el-statistic title="进行中" :value="statistics.active_lotteries">
              <template #prefix>
                <el-icon style="vertical-align: middle"><Timer /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card shadow="hover">
            <el-statistic title="已结束" :value="statistics.finished_lotteries">
              <template #prefix>
                <el-icon style="vertical-align: middle"><Check /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="12">
          <el-card shadow="hover">
            <el-statistic title="总参与人次" :value="statistics.total_participants">
              <template #prefix>
                <el-icon style="vertical-align: middle"><User /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card shadow="hover">
            <el-statistic title="总中奖人数" :value="statistics.total_winners">
              <template #prefix>
                <el-icon style="vertical-align: middle"><Star /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script>
import api from '../api'

export default {
  name: 'Statistics',
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
        this.$message.error('加载统计数据失败')
      }
    }
  }
}
</script>

<style scoped>
.statistics {
  max-width: 1200px;
  margin: 0 auto;
}
</style>

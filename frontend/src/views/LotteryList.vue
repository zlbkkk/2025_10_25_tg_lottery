<template>
  <div class="lottery-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>抽奖列表</span>
          <el-button type="primary" @click="loadLotteries">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>

      <el-table :data="lotteries" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="标题" width="150" />
        <el-table-column prop="prize_name" label="奖品" width="120" />
        <el-table-column prop="prize_count" label="数量" width="80" />
        <el-table-column label="参与人数" width="110">
          <template #default="scope">
            {{ scope.row.participant_count }}
            <span v-if="scope.row.max_participants > 0">
              / {{ scope.row.max_participants }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" sortable>
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="start_time" label="开始时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.start_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="end_time" label="结束时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.end_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button
              v-if="scope.row.status === 'active'"
              type="primary"
              size="small"
              @click="drawLottery(scope.row.id)"
            >
              开奖
            </el-button>
            <el-button
              type="info"
              size="small"
              @click="viewDetails(scope.row.id)"
            >
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
import api from '../api'

export default {
  name: 'LotteryList',
  data() {
    return {
      lotteries: [],
      loading: false
    }
  },
  mounted() {
    this.loadLotteries()
  },
  methods: {
    async loadLotteries() {
      this.loading = true
      try {
        let lotteries = await api.getLotteries()
        // 按创建时间倒序排列（最新创建的在最前面）
        this.lotteries = lotteries.sort((a, b) => {
          return new Date(b.created_at) - new Date(a.created_at)
        })
      } catch (error) {
        this.$message.error('加载失败')
      } finally {
        this.loading = false
      }
    },
    async drawLottery(id) {
      try {
        await this.$confirm('确定要开奖吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        await api.drawLottery(id)
        this.$message.success('开奖成功')
        this.loadLotteries()
      } catch (error) {
        if (error !== 'cancel') {
          this.$message.error('开奖失败')
        }
      }
    },
    viewDetails(id) {
      this.$router.push(`/lotteries/${id}`)
    },
    getStatusType(status) {
      const types = {
        'pending': 'info',
        'active': 'success',
        'finished': '',
        'cancelled': 'danger'
      }
      return types[status] || ''
    },
    getStatusText(status) {
      const texts = {
        'pending': '待开始',
        'active': '进行中',
        'finished': '已结束',
        'cancelled': '已取消'
      }
      return texts[status] || status
    },
    formatDate(dateString) {
      return new Date(dateString).toLocaleString('zh-CN')
    }
  }
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>

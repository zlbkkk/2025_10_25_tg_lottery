<template>
  <div class="lottery-detail">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <el-button @click="$router.back()" :icon="ArrowLeft">返回</el-button>
          <span style="margin-left: 20px; font-size: 20px; font-weight: bold;">抽奖详情</span>
        </div>
      </template>

      <div v-if="lottery">
        <!-- 基本信息 -->
        <el-descriptions title="基本信息" :column="2" border>
          <el-descriptions-item label="抽奖ID">{{ lottery.id }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(lottery.status)">
              {{ getStatusText(lottery.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="抽奖标题" :span="2">{{ lottery.title }}</el-descriptions-item>
          <el-descriptions-item label="抽奖说明" :span="2">
            {{ lottery.description || '无' }}
          </el-descriptions-item>
          <el-descriptions-item label="奖品名称">{{ lottery.prize_name }}</el-descriptions-item>
          <el-descriptions-item label="奖品数量">{{ lottery.prize_count }}</el-descriptions-item>
          <el-descriptions-item label="参与人数">
            {{ lottery.participant_count }}
            <span v-if="lottery.max_participants > 0">
              / {{ lottery.max_participants }}
            </span>
            <span v-else>
              (不限制)
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="中奖人数">{{ lottery.winner_count }}</el-descriptions-item>
          <el-descriptions-item label="开始时间">{{ formatDate(lottery.start_time) }}</el-descriptions-item>
          <el-descriptions-item label="结束时间">{{ formatDate(lottery.end_time) }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(lottery.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ formatDate(lottery.updated_at) }}</el-descriptions-item>
        </el-descriptions>

        <!-- 操作按钮 -->
        <div style="margin-top: 20px; text-align: center;">
          <el-button
            v-if="lottery.status === 'active'"
            type="primary"
            size="large"
            @click="drawLottery"
          >
            <el-icon><Trophy /></el-icon>
            立即开奖
          </el-button>
        </div>

        <!-- 参与者列表 -->
        <el-divider />
        <h3>参与者列表 ({{ lottery.participations.length }}人)</h3>
        <el-table
          :data="lottery.participations"
          style="width: 100%; margin-top: 20px;"
          :empty-text="'暂无参与者'"
        >
          <el-table-column type="index" label="序号" width="80" />
          <el-table-column prop="user.first_name" label="用户名" width="200">
            <template #default="scope">
              {{ scope.row.user.first_name || scope.row.user.username || '匿名用户' }}
            </template>
          </el-table-column>
          <el-table-column prop="user.username" label="Telegram用户名" width="200">
            <template #default="scope">
              @{{ scope.row.user.username || '无' }}
            </template>
          </el-table-column>
          <el-table-column prop="user.telegram_id" label="Telegram ID" width="150" />
          <el-table-column prop="participated_at" label="参与时间">
            <template #default="scope">
              {{ formatDate(scope.row.participated_at) }}
            </template>
          </el-table-column>
        </el-table>

        <!-- 中奖者列表 -->
        <el-divider />
        <h3>中奖者列表 ({{ lottery.winners.length }}人)</h3>
        <el-table
          :data="lottery.winners"
          style="width: 100%; margin-top: 20px;"
          :empty-text="lottery.status === 'finished' ? '暂无中奖者' : '尚未开奖'"
        >
          <el-table-column type="index" label="序号" width="80" />
          <el-table-column prop="user.first_name" label="用户名" width="200">
            <template #default="scope">
              {{ scope.row.user.first_name || scope.row.user.username || '匿名用户' }}
            </template>
          </el-table-column>
          <el-table-column prop="user.username" label="Telegram用户名" width="200">
            <template #default="scope">
              @{{ scope.row.user.username || '无' }}
            </template>
          </el-table-column>
          <el-table-column prop="prize_name" label="奖品" width="200" />
          <el-table-column prop="won_at" label="中奖时间">
            <template #default="scope">
              {{ formatDate(scope.row.won_at) }}
            </template>
          </el-table-column>
          <el-table-column prop="claimed" label="领奖状态" width="120">
            <template #default="scope">
              <el-tag :type="scope.row.claimed ? 'success' : 'warning'">
                {{ scope.row.claimed ? '已领取' : '未领取' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script>
import api from '../api'
import { ArrowLeft } from '@element-plus/icons-vue'

export default {
  name: 'LotteryDetail',
  data() {
    return {
      lottery: null,
      loading: false,
      ArrowLeft
    }
  },
  mounted() {
    this.loadLotteryDetail()
  },
  methods: {
    async loadLotteryDetail() {
      this.loading = true
      try {
        const id = this.$route.params.id
        this.lottery = await api.getLottery(id)
      } catch (error) {
        console.error('加载抽奖详情失败:', error)
        this.$message.error('加载失败')
        this.$router.back()
      } finally {
        this.loading = false
      }
    },
    async drawLottery() {
      try {
        await this.$confirm('确定要开奖吗？开奖后将无法撤销！', '提示', {
          confirmButtonText: '确定开奖',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        this.loading = true
        await api.drawLottery(this.lottery.id)
        this.$message.success('开奖成功！')
        
        // 重新加载详情
        await this.loadLotteryDetail()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('开奖失败:', error)
          this.$message.error('开奖失败')
        }
      } finally {
        this.loading = false
      }
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
      if (!dateString) return '-'
      return new Date(dateString).toLocaleString('zh-CN')
    }
  }
}
</script>

<style scoped>
.lottery-detail {
  max-width: 1400px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  align-items: center;
}

h3 {
  margin: 20px 0 10px 0;
  color: #409EFF;
}
</style>

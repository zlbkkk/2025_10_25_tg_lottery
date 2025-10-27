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
        <el-descriptions title="基本信息" :column="2" border size="small">
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
          
          <!-- 旧格式兼容：如果没有prizes数组，显示旧字段 -->
          <template v-if="!lottery.prizes || lottery.prizes.length === 0">
            <el-descriptions-item label="奖品名称">{{ lottery.prize_name }}</el-descriptions-item>
            <el-descriptions-item label="奖品数量">{{ lottery.prize_count }}</el-descriptions-item>
            <el-descriptions-item label="奖品图片" :span="2">
              <el-image
                v-if="lottery.prize_image"
                :src="getImageUrl(lottery.prize_image)"
                :preview-src-list="[getImageUrl(lottery.prize_image)]"
                fit="cover"
                style="width: 150px; height: 150px; border-radius: 8px; cursor: pointer;"
                :alt="lottery.prize_name"
              />
              <span v-else style="color: #999;">--</span>
            </el-descriptions-item>
          </template>
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
          
          <!-- 全局奖品图片 -->
          <el-descriptions-item label="奖品图片" :span="2" v-if="lottery.prize_image">
            <div style="display: flex; align-items: center; gap: 10px;">
              <el-image
                :src="getImageUrl(lottery.prize_image)"
                :preview-src-list="[getImageUrl(lottery.prize_image)]"
                fit="cover"
                style="width: 120px; height: 120px; border-radius: 8px; cursor: pointer; border: 2px solid #e4e7ed;"
                :alt="lottery.title"
                :preview-teleported="true"
              >
                <template #error>
                  <div class="image-slot">
                    <el-icon><Picture /></el-icon>
                  </div>
                </template>
              </el-image>
              <span style="color: #909399; font-size: 12px;">点击图片可放大查看</span>
            </div>
          </el-descriptions-item>
        </el-descriptions>

        <!-- 奖品设置详情（新格式） -->
        <div v-if="lottery.prizes && lottery.prizes.length > 0" style="margin-top: 20px;">
          <el-divider content-position="left" style="margin: 15px 0;">
            <span style="font-weight: bold; color: #409EFF; font-size: 15px;">🏆 奖品设置</span>
          </el-divider>
          
          <el-row :gutter="15">
            <el-col 
              v-for="prize in lottery.prizes" 
              :key="prize.id" 
              :span="8"
              style="margin-bottom: 15px;"
            >
              <el-card class="prize-card" shadow="hover">
                <template #header>
                  <div class="prize-card-header">
                    <span class="prize-level">{{ getLevelText(prize.level) }}</span>
                    <el-tag size="small" type="success">
                      {{ prize.winner_list_count || 0 }}/{{ prize.winner_count }} 人已抽取
                    </el-tag>
                  </div>
                </template>
                
                <div class="prize-card-body">
                  <div class="prize-info-item">
                    <span class="label">🎁 奖品名称：</span>
                    <span class="value">{{ prize.name }}</span>
                  </div>
                  
                  <div class="prize-info-item" v-if="prize.description">
                    <span class="label">📝 奖品描述：</span>
                    <span class="value">{{ prize.description }}</span>
                  </div>
                  
                  <div class="prize-info-item">
                    <span class="label">👥 中奖人数：</span>
                    <span class="value">{{ prize.winner_count }} 人</span>
                  </div>
                  
                  <div class="prize-info-item" v-if="prize.image">
                    <span class="label">🖼️ 奖品图片：</span>
                    <div style="margin-top: 10px;">
                      <el-image
                        :src="getImageUrl(prize.image)"
                        :preview-src-list="[getImageUrl(prize.image)]"
                        fit="cover"
                        style="width: 100px; height: 100px; border-radius: 6px; cursor: pointer; border: 2px solid #e4e7ed;"
                        :preview-teleported="true"
                      >
                        <template #error>
                          <div class="image-slot" style="font-size: 20px;">
                            <el-icon><Picture /></el-icon>
                          </div>
                        </template>
                      </el-image>
                      <div style="color: #909399; font-size: 11px; margin-top: 3px;">点击放大</div>
                    </div>
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>

        <!-- 操作按钮 -->
        <div style="margin: 15px 0; text-align: center;">
          <el-button
            v-if="lottery.status === 'active'"
            type="primary"
            @click="drawLottery"
          >
            <el-icon style="margin-right: 5px;"><Trophy /></el-icon>
            立即开奖
          </el-button>
        </div>

        <!-- 参与者列表 -->
        <el-divider style="margin: 15px 0;" />
        <h3 style="margin: 10px 0;">参与者列表 ({{ lottery.participations.length }}人)</h3>
        <el-table
          :data="lottery.participations"
          style="width: 100%; margin-top: 10px;"
          :empty-text="'暂无参与者'"
          size="small"
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
        <el-divider style="margin: 15px 0;" />
        <h3 style="margin: 10px 0;">中奖者列表 ({{ lottery.winners.length }}人)</h3>
        <el-table
          :data="lottery.winners"
          style="width: 100%; margin-top: 10px;"
          :empty-text="lottery.status === 'finished' ? '暂无中奖者' : '尚未开奖'"
          size="small"
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
import { ArrowLeft, Picture, Trophy } from '@element-plus/icons-vue'

export default {
  name: 'LotteryDetail',
  components: {
    ArrowLeft,
    Picture,
    Trophy
  },
  data() {
    return {
      lottery: null,
      loading: false
    }
  },
  mounted() {
    this.loadLotteryDetail()
  },
  methods: {
    getLevelText(level) {
      const map = {
        1: '🥇一等奖',
        2: '🥈二等奖',
        3: '🥉三等奖',
        4: '4️⃣四等奖',
        5: '5️⃣五等奖'
      }
      return map[level] || `第${level}等奖`
    },
    
    async loadLotteryDetail() {
      this.loading = true
      try {
        const id = this.$route.params.id
        this.lottery = await api.getLottery(id)
        console.log('抽奖详情:', this.lottery)
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
        'cancelled': '已作废'
      }
      return texts[status] || status
    },
    formatDate(dateString) {
      if (!dateString) return '-'
      return new Date(dateString).toLocaleString('zh-CN')
    },
    getImageUrl(imagePath) {
      // 如果是完整 URL，直接返回
      if (imagePath.startsWith('http')) {
        return imagePath
      }
      // 否则拼接后端地址
      return `http://localhost:8000${imagePath}`
    }
  }
}
</script>

<style scoped>
.lottery-detail {
  max-width: 1200px;
  margin: 0 auto;
}

.lottery-detail :deep(.el-card__body) {
  padding: 15px;
}

.card-header {
  display: flex;
  align-items: center;
}

h3 {
  margin: 10px 0;
  color: #409EFF;
  font-size: 16px;
}

/* 奖品卡片样式 */
.prize-card {
  height: 100%;
  border: 2px solid #e4e7ed;
  transition: all 0.3s;
}

.prize-card :deep(.el-card__header) {
  padding: 12px 15px;
}

.prize-card :deep(.el-card__body) {
  padding: 12px 15px;
}

.prize-card:hover {
  border-color: #409EFF;
  transform: translateY(-2px);
}

.prize-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.prize-level {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.prize-card-body {
  padding: 5px 0;
}

.prize-info-item {
  margin-bottom: 8px;
  line-height: 1.6;
  font-size: 14px;
}

.prize-info-item .label {
  font-weight: 500;
  color: #606266;
}

.prize-info-item .value {
  color: #303133;
  margin-left: 5px;
}

/* 图片加载失败占位符 */
.image-slot {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  background: #f5f7fa;
  color: #909399;
  font-size: 30px;
}

/* 图片悬浮效果 */
.el-image:hover {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
  transform: scale(1.02);
  transition: all 0.3s;
}
</style>

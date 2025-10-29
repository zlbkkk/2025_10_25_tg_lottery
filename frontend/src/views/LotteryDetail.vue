<template>
  <div class="lottery-detail">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <div style="display: flex; align-items: center;">
            <el-button @click="$router.back()" :icon="ArrowLeft">返回</el-button>
            <span style="margin-left: 20px; font-size: 20px; font-weight: bold;">抽奖详情</span>
          </div>
          <div style="display: flex; gap: 10px;">
            <el-button
              v-if="lottery && lottery.status === 'active'"
              type="primary"
              @click="showManualDrawDialog"
            >
              <el-icon style="margin-right: 5px;"><User /></el-icon>
              手动指定
            </el-button>
            <el-button
              v-if="lottery && lottery.status === 'active'"
              type="success"
              @click="randomDrawLottery"
            >
              <el-icon style="margin-right: 5px;"><Trophy /></el-icon>
              随机开奖
            </el-button>
          </div>
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
        <div v-if="lottery.prizes && lottery.prizes.length > 0">
          <el-divider style="margin: 15px 0;" />
          <h3 style="margin: 10px 0;">奖品设置</h3>
          
          <el-row :gutter="15" style="margin-top: 10px;">
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
          <el-table-column label="奖项" width="120">
            <template #default="scope">
              <el-tag type="success" effect="dark">
                {{ scope.row.prize_level_text || '-' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="prize_name" label="奖品" width="180" />
          <el-table-column prop="won_at" label="中奖时间" width="180">
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

    <!-- 手动指定中奖人对话框 -->
    <el-dialog
      v-model="manualDrawDialogVisible"
      title="手动指定中奖人"
      width="700px"
      :close-on-click-modal="false"
    >
      <div v-loading="participantsLoading">
        <el-alert
          type="info"
          :closable="false"
          style="margin-bottom: 15px;"
        >
          <template #title>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>请选择中奖人（将按奖品等级依次分配：一等奖、二等奖...）</span>
              <span style="color: #409eff;">已选择：{{ selectedWinners.length }} 人</span>
            </div>
          </template>
        </el-alert>

        <div v-if="participants.length === 0 && !participantsLoading" style="text-align: center; padding: 40px; color: #999;">
          <el-icon :size="60"><UserFilled /></el-icon>
          <p style="margin-top: 15px;">暂无参与者</p>
        </div>

        <el-table
          v-else
          :data="participants"
          :max-height="400"
          @selection-change="handleSelectionChange"
          ref="participantTable"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="display_name" label="用户名" width="180">
            <template #default="scope">
              <div>
                <strong>{{ scope.row.display_name }}</strong>
                <div style="font-size: 12px; color: #999;">@{{ scope.row.username || 'N/A' }}</div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="telegram_id" label="Telegram ID" width="130" />
          <el-table-column prop="participated_at" label="参与时间" width="170">
            <template #default="scope">
              {{ formatDate(scope.row.participated_at) }}
            </template>
          </el-table-column>
        </el-table>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="manualDrawDialogVisible = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="confirmManualDraw"
            :disabled="selectedWinners.length === 0"
            :loading="drawLoading"
          >
            确定开奖（已选 {{ selectedWinners.length }} 人）
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import api from '../api'
import { ArrowLeft, Picture, Trophy, User, UserFilled } from '@element-plus/icons-vue'

export default {
  name: 'LotteryDetail',
  components: {
    ArrowLeft,
    Picture,
    Trophy,
    User,
    UserFilled
  },
  data() {
    return {
      lottery: null,
      loading: false,
      // 手动指定中奖人相关
      manualDrawDialogVisible: false,
      participantsLoading: false,
      drawLoading: false,
      participants: [],
      selectedWinners: []
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
    // 显示手动指定中奖人对话框
    async showManualDrawDialog() {
      this.manualDrawDialogVisible = true
      this.participants = []
      this.selectedWinners = []
      
      // 加载参与者列表
      await this.loadParticipants(this.lottery.id)
    },
    // 加载参与者列表
    async loadParticipants(lotteryId) {
      try {
        this.participantsLoading = true
        const data = await api.getParticipants(lotteryId)
        this.participants = data.participants || []
        
        if (this.participants.length === 0) {
          this.$message.warning('该抽奖暂无参与者')
        }
      } catch (error) {
        console.error('加载参与者失败:', error)
        this.$message.error('加载参与者失败')
      } finally {
        this.participantsLoading = false
      }
    },
    // 选择变化时的处理
    handleSelectionChange(selection) {
      // 直接保存选择，后端会验证总名额
      this.selectedWinners = selection
    },
    // 确认手动指定开奖
    async confirmManualDraw() {
      if (this.selectedWinners.length === 0) {
        this.$message.warning('请至少选择一个中奖人')
        return
      }
      
      try {
        await this.$confirm(
          `确定将以下 ${this.selectedWinners.length} 人指定为中奖者吗？\n将按奖品等级依次分配（一等奖、二等奖...）\n\n${this.selectedWinners.map((w, i) => `${i + 1}. ${w.display_name}`).join('\n')}`,
          '确认手动指定开奖',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        this.drawLoading = true
        const winnerIds = this.selectedWinners.map(w => w.id)
        await api.manualDrawLottery(this.lottery.id, winnerIds)
        
        this.$message.success('手动指定开奖成功！')
        this.manualDrawDialogVisible = false
        // 重新加载详情
        await this.loadLotteryDetail()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('手动指定开奖失败:', error)
          const errorMsg = error.response?.data?.error || '手动指定开奖失败'
          this.$message.error(errorMsg)
        }
      } finally {
        this.drawLoading = false
      }
    },
    // 随机开奖
    async randomDrawLottery() {
      try {
        await this.$confirm('确定要随机开奖吗？开奖后将无法撤销！', '提示', {
          confirmButtonText: '确定开奖',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        this.loading = true
        await api.drawLottery(this.lottery.id)
        this.$message.success('随机开奖成功！')
        
        // 重新加载详情
        await this.loadLotteryDetail()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('随机开奖失败:', error)
          const errorMsg = error.response?.data?.error || '随机开奖失败'
          this.$message.error(errorMsg)
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
  justify-content: space-between;
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

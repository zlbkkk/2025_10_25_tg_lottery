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

      <el-table 
        :data="lotteries" 
        style="width: 100%" 
        v-loading="loading"
        class="compact-table"
        :max-height="700"
      >
        <el-table-column label="序号" width="60">
          <template #default="scope">
            {{ (currentPage - 1) * pageSize + scope.$index + 1 }}
          </template>
        </el-table-column>
        <el-table-column label="标题" width="120">
          <template #default="scope">
            <el-tooltip
              v-if="scope.row.title && scope.row.title.length > 10"
              :content="scope.row.title"
              placement="top"
            >
              <span class="ellipsis-text">{{ scope.row.title }}</span>
            </el-tooltip>
            <span v-else>{{ scope.row.title }}</span>
          </template>
        </el-table-column>
        <el-table-column label="奖品图片" width="90">
          <template #default="scope">
            <el-image
              v-if="scope.row.prize_image"
              :src="getImageUrl(scope.row.prize_image)"
              fit="cover"
              style="width: 60px; height: 60px; border-radius: 4px; cursor: pointer;"
              :alt="scope.row.prize_name"
              @click="previewImage(getImageUrl(scope.row.prize_image))"
              :preview-disabled="true"
            />
            <span v-else style="color: #999;">-</span>
          </template>
        </el-table-column>
        <el-table-column label="奖品" width="100">
          <template #default="scope">
            <el-tooltip
              v-if="scope.row.prize_name && scope.row.prize_name.length > 10"
              :content="scope.row.prize_name"
              placement="top"
            >
              <span class="ellipsis-text">{{ scope.row.prize_name }}</span>
            </el-tooltip>
            <span v-else>{{ scope.row.prize_name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="prize_count" label="奖品数量" width="90" />
        <el-table-column label="参与人数" width="100">
          <template #default="scope">
            {{ scope.row.participant_count }}
            <span v-if="scope.row.max_participants > 0">
              / {{ scope.row.max_participants }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="90">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="165" sortable>
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="start_time" label="开奖时间" width="165">
          <template #default="scope">
            {{ formatDate(scope.row.start_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="end_time" label="结束时间" width="165">
          <template #default="scope">
            {{ formatDate(scope.row.end_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="320" fixed="right">
          <template #default="scope">
            <div class="action-buttons">
              <el-button
                v-if="scope.row.status === 'active'"
                type="primary"
                size="small"
                @click="showManualDrawDialog(scope.row)"
              >
                手动指定
              </el-button>
              <el-button
                v-if="scope.row.status === 'active'"
                type="success"
                size="small"
                @click="randomDrawLottery(scope.row.id)"
              >
                随机开奖
              </el-button>
              <el-button
                v-if="scope.row.status !== 'finished' && scope.row.status !== 'cancelled'"
                type="warning"
                size="small"
                @click="editLottery(scope.row.id)"
              >
                编辑
              </el-button>
              <el-button
                v-if="scope.row.status !== 'finished' && scope.row.status !== 'cancelled'"
                type="danger"
                size="small"
                @click="cancelLottery(scope.row.id)"
              >
                作废
              </el-button>
              <el-button
                type="info"
                size="small"
                @click="viewDetails(scope.row.id)"
              >
                详情
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页组件 -->
      <div class="pagination-container">
        <el-pagination
          :current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next, jumper"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 自定义图片预览对话框 -->
    <el-dialog
      v-model="imagePreviewVisible"
      title="图片预览"
      width="80%"
      :modal="true"
      :close-on-click-modal="true"
      :close-on-press-escape="true"
      center
    >
      <div class="image-preview-container">
        <img :src="previewImageUrl" alt="预览图片" class="preview-image" />
      </div>
    </el-dialog>

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

export default {
  name: 'LotteryList',
  data() {
    return {
      lotteries: [],
      loading: false,
      imagePreviewVisible: false,
      previewImageUrl: '',
      // 手动指定中奖人相关
      manualDrawDialogVisible: false,
      participantsLoading: false,
      drawLoading: false,
      currentLottery: null,
      participants: [],
      selectedWinners: [],
      // 分页数据
      currentPage: 1,
      pageSize: 10,
      total: 0
    }
  },
  mounted() {
    this.loadLotteries()
  },
  methods: {
    async loadLotteries() {
      this.loading = true
      try {
        // 直接使用后端返回的排序（进行中 > 已结束 > 已作废，每组内按创建时间倒序）
        const response = await api.getLotteries(this.currentPage)
        
        // 兼容分页和非分页两种数据格式
        if (response.results) {
          // 分页数据格式: { count, next, previous, results }
          this.lotteries = response.results
          this.total = response.count
        } else if (Array.isArray(response)) {
          // 非分页数据格式: 直接是数组
          this.lotteries = response
          this.total = response.length
        }
      } catch (error) {
        this.$message.error('加载失败')
      } finally {
        this.loading = false
      }
    },
    handlePageChange(page) {
      this.currentPage = page
      this.loadLotteries()
    },
    // 显示手动指定中奖人对话框
    async showManualDrawDialog(lottery) {
      this.currentLottery = lottery
      this.manualDrawDialogVisible = true
      this.participants = []
      this.selectedWinners = []
      
      // 加载参与者列表
      await this.loadParticipants(lottery.id)
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
        await api.manualDrawLottery(this.currentLottery.id, winnerIds)
        
        this.$message.success('手动指定开奖成功！')
        this.manualDrawDialogVisible = false
        this.loadLotteries()
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
    async randomDrawLottery(id) {
      try {
        await this.$confirm('确定要随机开奖吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        await api.drawLottery(id)
        this.$message.success('随机开奖成功')
        this.loadLotteries()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('随机开奖失败:', error)
          const errorMsg = error.response?.data?.error || '随机开奖失败'
          this.$message.error(errorMsg)
        }
      }
    },
    async cancelLottery(id) {
      try {
        await this.$confirm('确定要作废此抽奖吗？作废后将不会开奖和通知用户。', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        await api.cancelLottery(id)
        this.$message.success('作废成功')
        this.loadLotteries()
      } catch (error) {
        if (error !== 'cancel') {
          this.$message.error('作废失败')
        }
      }
    },
    editLottery(id) {
      this.$router.push(`/create/${id}`)
    },
    viewDetails(id) {
      this.$router.push(`/lotteries/${id}`)
    },
    previewImage(imageUrl) {
      this.previewImageUrl = imageUrl
      this.imagePreviewVisible = true
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
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.image-preview-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
  background: #f5f5f5;
  border-radius: 8px;
}

.preview-image {
  max-width: 100%;
  max-height: 70vh;
  object-fit: contain;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* 紧凑表格样式 */
.compact-table :deep(.el-table__cell) {
  padding: 8px 4px !important;
}

/* 操作按钮样式 - 强制一行显示 */
.action-buttons {
  display: flex;
  gap: 2px;
  flex-wrap: nowrap;
  white-space: nowrap;
}

.action-buttons .el-button {
  padding: 4px 8px !important;
  font-size: 12px;
  margin: 0 !important;
  flex-shrink: 0;
  min-width: auto;
}

.action-buttons .el-button + .el-button {
  margin-left: 0 !important;
}

/* 文本截断样式 */
.ellipsis-text {
  display: inline-block;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  cursor: pointer;
}

/* 分页容器样式 */
.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 6px;
}

/* 优化滚动条样式 */
.compact-table :deep(.el-scrollbar__wrap) {
  overflow-x: auto;
  scroll-behavior: smooth;
}

.compact-table :deep(.el-table__body-wrapper) {
  overflow-x: auto;
  scroll-behavior: smooth;
}

/* 自定义滚动条样式（仅Webkit内核浏览器） */
.compact-table :deep(.el-scrollbar__wrap)::-webkit-scrollbar,
.compact-table :deep(.el-table__body-wrapper)::-webkit-scrollbar {
  height: 12px;
  width: 12px;
}

.compact-table :deep(.el-scrollbar__wrap)::-webkit-scrollbar-track,
.compact-table :deep(.el-table__body-wrapper)::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 6px;
}

.compact-table :deep(.el-scrollbar__wrap)::-webkit-scrollbar-thumb,
.compact-table :deep(.el-table__body-wrapper)::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 6px;
  transition: background 0.3s;
}

.compact-table :deep(.el-scrollbar__wrap)::-webkit-scrollbar-thumb:hover,
.compact-table :deep(.el-table__body-wrapper)::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>

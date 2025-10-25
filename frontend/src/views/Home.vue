<template>
  <div class="home">
    <!-- 顶部标题区 -->
    <div class="page-header">
      <h1>抽奖管理系统</h1>
      <p>Telegram 抽奖机器人管理平台</p>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-container">
      <div class="stat-card" v-for="(stat, index) in statsConfig" :key="index">
        <div class="stat-icon">{{ stat.icon }}</div>
        <div class="stat-info">
          <div class="stat-number">{{ statistics[stat.key] }}</div>
          <div class="stat-label">{{ stat.label }}</div>
        </div>
      </div>
    </div>

    <!-- 快速操作 -->
    <div class="section">
      <h2 class="section-title">快速操作</h2>
      <div class="actions-grid">
        <div class="action-card" v-for="(action, index) in actions" :key="index" @click="$router.push(action.path)">
          <div class="action-header">
            <div class="action-icon">{{ action.icon }}</div>
            <h3>{{ action.title }}</h3>
          </div>
          <p class="action-desc">{{ action.desc }}</p>
        </div>
      </div>
    </div>

    <!-- 系统概览 -->
    <div class="section">
      <h2 class="section-title">系统概览</h2>
      <div class="overview-card">
        <div class="overview-item" v-for="(item, index) in overviewData" :key="index">
          <span class="overview-label">{{ item.label }}</span>
          <span class="overview-value" :class="{ highlight: item.highlight }">{{ item.value }}</span>
        </div>
      </div>
    </div>
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
      },
      statsConfig: [
        { key: 'total_lotteries', label: '总抽奖数', icon: '🏆' },
        { key: 'active_lotteries', label: '进行中', icon: '⏰' },
        { key: 'total_participants', label: '总参与人次', icon: '👥' },
        { key: 'total_winners', label: '总中奖人数', icon: '⭐' }
      ],
      actions: [
        {
          title: '创建新抽奖',
          desc: '快速创建一个新的抽奖活动',
          icon: '➕',
          path: '/create',
          gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
        },
        {
          title: '抽奖列表',
          desc: '查看所有抽奖活动详情',
          icon: '📋',
          path: '/lotteries',
          gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'
        },
        {
          title: '数据统计',
          desc: '查看详细的数据统计分析',
          icon: '📊',
          path: '/statistics',
          gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'
        }
      ]
    }
  },
  computed: {
    winRate() {
      if (this.statistics.total_participants === 0) return 0
      return ((this.statistics.total_winners / this.statistics.total_participants) * 100).toFixed(1)
    },
    overviewData() {
      return [
        { label: '今日创建', value: this.statistics.total_lotteries, highlight: false },
        { label: '进行中', value: this.statistics.active_lotteries, highlight: true },
        { label: '总参与', value: this.statistics.total_participants, highlight: false },
        { label: '中奖率', value: `${this.winRate}%`, highlight: false }
      ]
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
/* 现代简约风格 - 平衡设计 */
.home {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

/* 页面标题 */
.page-header {
  text-align: center;
  margin-bottom: 48px;
}

.page-header h1 {
  font-size: 28px;
  font-weight: 500;
  color: #262626;
  margin: 0 0 12px;
}

.page-header p {
  font-size: 14px;
  color: #8c8c8c;
  margin: 0;
}

/* 统计卡片 - 图标+数字 */
.stats-container {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 48px;
}

.stat-card {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.3s ease;
  cursor: default;
}

.stat-card:hover {
  border-color: #d9d9d9;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  transform: translateY(-2px);
}

.stat-icon {
  font-size: 32px;
  line-height: 1;
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 32px;
  font-weight: 500;
  color: #262626;
  line-height: 1.2;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 13px;
  color: #8c8c8c;
}

/* 区块 */
.section {
  margin-bottom: 48px;
}

.section-title {
  font-size: 16px;
  font-weight: 500;
  color: #262626;
  margin: 0 0 20px;
}

/* 快速操作卡片 */
.actions-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.action-card {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-card:hover {
  border-color: #1890ff;
  box-shadow: 0 4px 12px rgba(24,144,255,0.12);
  transform: translateY(-2px);
}

.action-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.action-icon {
  font-size: 24px;
  line-height: 1;
}

.action-header h3 {
  font-size: 16px;
  font-weight: 500;
  color: #262626;
  margin: 0;
}

.action-desc {
  font-size: 13px;
  color: #8c8c8c;
  line-height: 1.6;
  margin: 0;
}

/* 系统概览 */
.overview-card {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  overflow: hidden;
}

.overview-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid #f0f0f0;
  transition: background 0.2s ease;
}

.overview-item:last-child {
  border-bottom: none;
}

.overview-item:hover {
  background: #fafafa;
}

.overview-label {
  font-size: 14px;
  color: #595959;
}

.overview-value {
  font-size: 20px;
  font-weight: 500;
  color: #262626;
}

.overview-value.highlight {
  color: #1890ff;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .stats-container {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .actions-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .home {
    padding: 24px 16px;
  }
  
  .page-header {
    margin-bottom: 32px;
  }
  
  .page-header h1 {
    font-size: 24px;
  }
  
  .stats-container {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .stat-card {
    padding: 20px;
  }
  
  .stat-number {
    font-size: 28px;
  }
  
  .section {
    margin-bottom: 32px;
  }
}
</style>

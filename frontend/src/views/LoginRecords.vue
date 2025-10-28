<template>
  <div class="login-records-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>🔐 登录记录</span>
          <el-button 
            type="primary" 
            size="small" 
            @click="loadRecords"
            :loading="loading"
          >
            刷新
          </el-button>
        </div>
      </template>

      <div v-if="loading && records.length === 0" class="loading-container">
        <el-skeleton :rows="5" animated />
      </div>

      <div v-else-if="records.length === 0" class="empty-container">
        <el-empty description="暂无登录记录" />
      </div>

      <el-table 
        v-else
        :data="records" 
        style="width: 100%"
        stripe
        :default-sort="{prop: 'login_time', order: 'descending'}"
      >
        <el-table-column prop="username" label="用户名" width="120" sortable>
          <template #default="scope">
            <el-tag type="primary" size="small">{{ scope.row.username }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="full_name" label="姓名" width="120" sortable>
          <template #default="scope">
            {{ scope.row.full_name || scope.row.username }}
          </template>
        </el-table-column>

        <el-table-column prop="login_time" label="登录时间" width="180" sortable>
          <template #default="scope">
            {{ formatDateTime(scope.row.login_time) }}
          </template>
        </el-table-column>

        <el-table-column prop="logout_time" label="退出时间" width="180" sortable>
          <template #default="scope">
            <span v-if="scope.row.logout_time">
              {{ formatDateTime(scope.row.logout_time) }}
            </span>
            <el-tag v-else-if="scope.row.is_truly_active" type="success" size="small">在线中</el-tag>
            <el-tag v-else type="warning" size="small">已超时</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="session_duration" label="在线时长" width="120">
          <template #default="scope">
            <span v-if="scope.row.session_duration">
              {{ formatDuration(scope.row.session_duration) }}
            </span>
            <span v-else-if="scope.row.is_truly_active">
              {{ formatDuration(getActiveDuration(scope.row.login_time)) }}
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>

        <el-table-column prop="ip_address" label="IP地址" width="150">
          <template #default="scope">
            <el-tag type="info" size="small">{{ scope.row.ip_address || '未知' }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="device_type" label="设备" width="120">
          <template #default="scope">
            <el-tag 
              :type="getDeviceTagType(scope.row.device_type)" 
              size="small"
            >
              {{ getDeviceIcon(scope.row.device_type) }} {{ scope.row.device_type || '未知' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="browser" label="浏览器" width="120">
          <template #default="scope">
            <el-tag type="info" size="small">
              {{ getBrowserIcon(scope.row.browser) }} {{ scope.row.browser || '未知' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="user_agent" label="详细信息" min-width="200">
          <template #default="scope">
            <el-tooltip 
              :content="scope.row.user_agent || '无'" 
              placement="top"
              :disabled="!scope.row.user_agent"
            >
              <div class="user-agent-text">
                {{ scope.row.user_agent || '无' }}
              </div>
            </el-tooltip>
          </template>
        </el-table-column>

        <el-table-column prop="is_truly_active" label="状态" width="100" fixed="right">
          <template #default="scope">
            <el-tag 
              v-if="scope.row.logout_time"
              type="info" 
              size="small"
            >
              已结束
            </el-tag>
            <el-tag 
              v-else-if="scope.row.is_truly_active"
              type="success" 
              size="small"
            >
              在线
            </el-tag>
            <el-tag 
              v-else
              type="warning" 
              size="small"
            >
              超时离线
            </el-tag>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页（如果需要） -->
      <div v-if="records.length > 0" style="margin-top: 20px; text-align: right;">
        <el-text type="info" size="small">
          共 {{ records.length }} 条记录
        </el-text>
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/api'

export default {
  name: 'LoginRecords',
  setup() {
    const loading = ref(false)
    const records = ref([])

    const loadRecords = async () => {
      loading.value = true
      try {
        const data = await api.getLoginRecords()
        // DRF ViewSet 返回的是分页数据，需要从 results 中获取
        // 格式: { count: 1, results: [...] } 或直接是数组 [...]
        if (Array.isArray(data)) {
          records.value = data
        } else if (data && Array.isArray(data.results)) {
          records.value = data.results
        } else {
          records.value = []
        }
      } catch (error) {
        console.error('加载登录记录失败:', error)
        
        // 处理权限不足错误
        if (error.response && error.response.status === 403) {
          ElMessage.error({
            message: '权限不足：只有超级管理员（admin）才能查看登录记录',
            duration: 5000
          })
        } else {
          ElMessage.error('加载登录记录失败')
        }
      } finally {
        loading.value = false
      }
    }

    const formatDateTime = (datetime) => {
      if (!datetime) return '-'
      const date = new Date(datetime)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
      })
    }

    const formatDuration = (seconds) => {
      if (!seconds || seconds < 0) return '-'
      
      const hours = Math.floor(seconds / 3600)
      const minutes = Math.floor((seconds % 3600) / 60)
      const secs = seconds % 60
      
      if (hours > 0) {
        return `${hours}小时${minutes}分钟`
      } else if (minutes > 0) {
        return `${minutes}分钟${secs}秒`
      } else {
        return `${secs}秒`
      }
    }

    const getActiveDuration = (loginTime) => {
      if (!loginTime) return 0
      const now = new Date()
      const login = new Date(loginTime)
      return Math.floor((now - login) / 1000)
    }

    const getDeviceIcon = (device) => {
      if (!device) return '❓'
      const deviceLower = device.toLowerCase()
      if (deviceLower.includes('windows')) return '💻'
      if (deviceLower.includes('mac')) return '🖥️'
      if (deviceLower.includes('linux')) return '🐧'
      if (deviceLower.includes('iphone')) return '📱'
      if (deviceLower.includes('ipad')) return '📱'
      if (deviceLower.includes('android')) return '📱'
      return '🖥️'
    }

    const getBrowserIcon = (browser) => {
      if (!browser) return ''
      const browserLower = browser.toLowerCase()
      if (browserLower.includes('chrome')) return '🌐'
      if (browserLower.includes('firefox')) return '🦊'
      if (browserLower.includes('safari')) return '🧭'
      if (browserLower.includes('edge')) return '🌊'
      if (browserLower.includes('opera')) return '🎭'
      return '🌐'
    }

    const getDeviceTagType = (device) => {
      if (!device) return 'info'
      const deviceLower = device.toLowerCase()
      if (deviceLower.includes('windows') || deviceLower.includes('mac')) return 'primary'
      if (deviceLower.includes('iphone') || deviceLower.includes('android')) return 'success'
      if (deviceLower.includes('linux')) return 'warning'
      return 'info'
    }

    onMounted(() => {
      loadRecords()
    })

    return {
      loading,
      records,
      loadRecords,
      formatDateTime,
      formatDuration,
      getActiveDuration,
      getDeviceIcon,
      getBrowserIcon,
      getDeviceTagType
    }
  }
}
</script>

<style scoped>
.login-records-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 500;
  font-size: 16px;
}

.loading-container {
  padding: 20px;
}

.empty-container {
  padding: 40px 0;
}

.user-agent-text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
  font-size: 12px;
  color: #606266;
}
</style>


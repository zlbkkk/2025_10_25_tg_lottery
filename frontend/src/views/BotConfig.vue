<template>
  <div class="bot-config">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>🤖 Bot 配置</span>
        </div>
      </template>

      <el-alert
        type="info"
        :closable="false"
        show-icon
        style="margin-bottom: 20px;"
      >
        <template #title>
          <span style="font-size: 14px; font-weight: 500;">配置说明</span>
        </template>
        <div style="font-size: 13px; line-height: 1.6;">
          <p style="margin: 0 0 8px 0;">
            前往 Telegram 搜索 <strong>@BotFather</strong>，发送 <code>/newbot</code> 创建您的Bot，将返回的 Token 粘贴到下方保存即可。
          </p>
          <p style="margin: 0 0 8px 0; color: #67c23a;">
            <strong>✅ 自动获取：</strong>保存时会自动验证Token并获取Bot用户名
          </p>
          <p style="margin: 0; color: #e6a23c;">
            <strong>⚠️ 重要：</strong>不能配置与他人重复的token
          </p>
        </div>
      </el-alert>

      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="Bot Token" prop="bot_token">
          <el-input
            v-model="form.bot_token"
            type="password"
            show-password
            placeholder="例如：123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
          >
            <template #prefix>
              <el-icon><Key /></el-icon>
            </template>
          </el-input>
          <div class="form-tip">
            Token格式：数字:字母数字混合，例如 123456789:ABC-DEF...
            <span v-if="currentConfig && currentConfig.bot_token_preview" style="margin-left: 10px; color: #67c23a;">
              (当前: {{ currentConfig.bot_token_preview }})
            </span>
          </div>
        </el-form-item>

        <!-- <el-form-item label="Bot 用户名" prop="bot_username">
          <el-input
            v-model="form.bot_username"
            placeholder="例如：@MyLotteryBot"
          >
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
          <div class="form-tip">
            您的Bot用户名，以@开头（选填，用于显示）
          </div>
        </el-form-item> -->

        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="loading">
            <el-icon><Check /></el-icon>
            保存配置
          </el-button>
          <el-button @click="handleTest" :disabled="!form.bot_token || loading">
            <el-icon><Connection /></el-icon>
            测试连接
          </el-button>
        </el-form-item>
      </el-form>

      <el-divider />

      <div v-if="currentConfig" class="config-info">
        <h3>当前配置状态</h3>
        <el-table 
          :data="currentConfig.bot_token_preview || currentConfig.bot_username ? [currentConfig] : []" 
          border 
          size="small" 
          style="width: 100%"
        >
          <el-table-column prop="bot_username" label="Bot用户名" min-width="100">
            <template #default="scope">
              {{ scope.row.bot_username || '未设置' }}
            </template>
          </el-table-column>
          
          <el-table-column label="Token状态" width="100" align="center">
            <template #default="scope">
              <el-tag v-if="scope.row.bot_token_preview" type="success" size="small">
                已配置
              </el-tag>
              <el-tag v-else type="info" size="small">未配置</el-tag>
            </template>
          </el-table-column>
          
          <el-table-column label="启用状态" width="100" align="center">
            <template #default="scope">
              <el-tag v-if="scope.row.is_active" type="success" size="small">
                启用中
              </el-tag>
              <el-tag v-else type="warning" size="small">已禁用</el-tag>
            </template>
          </el-table-column>
          
          <el-table-column prop="updated_at" label="更新时间" width="160">
            <template #default="scope">
              {{ formatDate(scope.row.updated_at) }}
            </template>
          </el-table-column>
          
          <el-table-column label="操作" width="250" align="center">
            <template #default="scope">
              <div style="display: flex; gap: 8px; align-items: center; justify-content: center;">
                <!-- 启用/禁用开关 -->
                <el-switch
                  v-if="scope.row.bot_token_preview"
                  v-model="scope.row.is_active"
                  active-text="启用"
                  inactive-text="禁用"
                  @change="handleToggleStatus"
                  :loading="loading"
                  size="small"
                />
                <!-- 删除按钮 -->
                <el-button 
                  v-if="scope.row.bot_token_preview" 
                  type="danger" 
                  @click="handleDelete" 
                  :loading="loading"
                  plain
                  size="small"
                >
                  <el-icon><Delete /></el-icon>
                  删除配置
                </el-button>
                <span v-if="!scope.row.bot_token_preview" style="color: #909399; font-size: 12px;">-</span>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div style="margin-top: 15px; padding: 8px 12px; background: #fef0f0; border-left: 3px solid #f56c6c; border-radius: 4px; font-size: 12px; color: #606266;">
        <strong style="color: #f56c6c;">💡 提示：</strong>
        保存时自动验证Token并获取Bot用户名 · 修改后10秒内自动生效 · 一个账号一个Bot
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Key, User, Check, Connection, Delete } from '@element-plus/icons-vue'
import api from '@/api'

export default {
  name: 'BotConfig',
  components: {
    Key,
    User,
    Check,
    Connection,
    Delete
  },
  setup() {
    const formRef = ref(null)
    const loading = ref(false)
    const currentConfig = ref(null)
    
    const form = reactive({
      bot_token: '',
      bot_username: ''
    })
    
    const rules = {
      bot_token: [
        { required: true, message: '请输入Bot Token', trigger: 'blur' },
        { 
          pattern: /^\d+:[A-Za-z0-9_-]+$/,
          message: 'Token格式不正确，应为：数字:字母数字',
          trigger: 'blur'
        }
      ]
    }
    
    // 加载配置
    const loadConfig = async () => {
      try {
        const data = await api.getBotConfig()
        currentConfig.value = data
        
        // 只在未配置时填充表单（避免覆盖用户正在编辑的内容）
        if (data.bot_username) {
          form.bot_username = data.bot_username
        }
        
        // 不显示完整token，只显示预览
        form.bot_token = ''
      } catch (error) {
        console.error('加载配置失败:', error)
        ElMessage.error('加载配置失败')
      }
    }
    
    // 提交配置
    const handleSubmit = async () => {
      try {
        await formRef.value.validate()
        
        loading.value = true
        
        // 只发送填写了的字段
        const updateData = {}
        
        if (form.bot_token) {
          updateData.bot_token = form.bot_token
        }
        
        if (form.bot_username) {
          updateData.bot_username = form.bot_username
        }
        
        const result = await api.updateBotConfig(updateData)
        
        ElMessage.success(result.message || 'Bot配置已保存')
        
        // 重新加载配置
        await loadConfig()
        
        // 清空token输入框
        form.bot_token = ''
      } catch (error) {
        console.error('保存配置失败:', error)
        
        // 处理唯一性冲突错误
        if (error.response && error.response.data) {
          const errorData = error.response.data
          
          if (errorData.error && errorData.error.includes('Token冲突')) {
            // Token 冲突，显示详细信息
            ElMessage({
              message: errorData.detail || errorData.error,
              type: 'error',
              duration: 6000,
              dangerouslyUseHTMLString: true
            })
            
            // 额外显示帮助提示
            if (errorData.help) {
              setTimeout(() => {
                ElMessage({
                  message: `💡 ${errorData.help}`,
                  type: 'info',
                  duration: 5000
                })
              }, 500)
            }
          } else if (errorData.error) {
            ElMessage.error(errorData.error)
          } else {
            ElMessage.error('保存配置失败')
          }
        } else if (error !== false) {
          ElMessage.error('保存配置失败')
        }
      } finally {
        loading.value = false
      }
    }
    
    // 切换启用/禁用状态
    const handleToggleStatus = async (value) => {
      try {
        loading.value = true
        
        const result = await api.updateBotConfig({
          is_active: value
        })
        
        ElMessage.success(value ? 'Bot已启用' : 'Bot已禁用')
        
        // 重新加载配置
        await loadConfig()
      } catch (error) {
        console.error('更新状态失败:', error)
        ElMessage.error('更新状态失败')
        
        // 恢复原状态
        currentConfig.value.is_active = !value
      } finally {
        loading.value = false
      }
    }
    
    // 测试连接
    const handleTest = async () => {
      if (!form.bot_token) {
        ElMessage.warning('请先输入Bot Token')
        return
      }
      
      loading.value = true
      
      try {
        // 调用Telegram Bot API验证Token
        const response = await fetch(`https://api.telegram.org/bot${form.bot_token}/getMe`)
        const data = await response.json()
        
        if (data.ok) {
          ElMessage.success(`✓ 连接成功！Bot: @${data.result.username}`)
          // 自动填充用户名
          form.bot_username = `@${data.result.username}`
        } else {
          ElMessage.error('Token无效或连接失败')
        }
      } catch (error) {
        console.error('测试连接失败:', error)
        ElMessage.error('无法连接到Telegram服务器')
      } finally {
        loading.value = false
      }
    }
    
    // 删除配置
    const handleDelete = async () => {
      try {
        await ElMessageBox.confirm(
          '删除后，Bot 将停止工作，您可以重新配置新的 Bot Token。确定要删除吗？',
          '确认删除 Bot 配置',
          {
            confirmButtonText: '确定删除',
            cancelButtonText: '取消',
            type: 'warning',
            confirmButtonClass: 'el-button--danger'
          }
        )
        
        loading.value = true
        
        const result = await api.deleteBotConfig()
        
        ElMessage.success(result.message || 'Bot配置已删除')
        
        // 重新加载配置
        await loadConfig()
        
        // 清空表单
        form.bot_token = ''
        form.bot_username = ''
      } catch (error) {
        if (error !== 'cancel') {
          console.error('删除配置失败:', error)
          ElMessage.error('删除配置失败')
        }
      } finally {
        loading.value = false
      }
    }
    
    // 格式化日期
    const formatDate = (dateString) => {
      if (!dateString) return '-'
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN')
    }
    
    onMounted(() => {
      loadConfig()
    })
    
    return {
      formRef,
      loading,
      currentConfig,
      form,
      rules,
      handleSubmit,
      handleTest,
      handleToggleStatus,
      handleDelete,
      formatDate
    }
  }
}
</script>

<style scoped>
.bot-config {
  max-width: 800px;
  margin: 0 auto;
}

.card-header {
  font-size: 18px;
  font-weight: bold;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
  line-height: 1.5;
}

code {
  background-color: #f5f7fa;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: monospace;
  color: #e6a23c;
}

.config-info h3 {
  margin-bottom: 15px;
  color: #303133;
}

.el-alert p {
  margin: 5px 0;
  line-height: 1.8;
}
</style>


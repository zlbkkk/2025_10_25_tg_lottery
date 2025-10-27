<template>
  <div class="login-container">
    <el-card class="login-box">
      <template #header>
        <div class="login-header">
          <h2>🎉 抽奖管理系统</h2>
          <p>多租户管理平台</p>
        </div>
      </template>
      
      <el-form :model="form" :rules="rules" ref="formRef" @keyup.enter="handleLogin">
        <el-form-item prop="username">
          <el-input 
            v-model="form.username" 
            placeholder="请输入用户名"
            size="large"
          >
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input 
            v-model="form.password" 
            type="password"
            placeholder="请输入密码"
            size="large"
            show-password
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            @click="handleLogin"
            :loading="loading"
            size="large"
            style="width: 100%;"
          >
            {{ loading ? '登录中...' : '登录' }}
          </el-button>
        </el-form-item>
        
        <div class="login-tip">
          <el-alert
            title="默认账号"
            type="info"
            :closable="false"
            show-icon
          >
            <p>用户名：admin</p>
            <p>密码：admin123</p>
          </el-alert>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import { User, Lock } from '@element-plus/icons-vue'
import api from '../api'

export default {
  name: 'Login',
  components: {
    User,
    Lock
  },
  data() {
    return {
      form: {
        username: '',
        password: ''
      },
      rules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' }
        ]
      },
      loading: false
    }
  },
  mounted() {
    // 如果已登录，跳转到首页
    this.checkLogin()
  },
  methods: {
    async checkLogin() {
      try {
        await api.getCurrentUser()
        this.$router.push('/')
      } catch (error) {
        // 未登录，继续显示登录页
      }
    },
    
    async handleLogin() {
      try {
        await this.$refs.formRef.validate()
        this.loading = true
        
        const user = await api.login(this.form)
        
        // 存储用户信息
        localStorage.setItem('user', JSON.stringify(user))
        
        this.$message.success(`欢迎回来，${user.first_name || user.username}！`)
        
        // 跳转到首页
        this.$router.push('/')
      } catch (error) {
        console.error('登录失败:', error)
        if (error.response && error.response.status === 401) {
          this.$message.error('用户名或密码错误')
        } else {
          this.$message.error('登录失败，请重试')
        }
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-box {
  width: 420px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.login-header {
  text-align: center;
}

.login-header h2 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 26px;
}

.login-header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.login-tip {
  margin-top: 20px;
}

.login-tip :deep(.el-alert__content) {
  padding: 0;
}

.login-tip p {
  margin: 3px 0;
  font-size: 13px;
  color: #606266;
}
</style>

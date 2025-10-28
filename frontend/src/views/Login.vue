<template>
  <div class="login-container">
    <el-card class="login-box">
      <template #header>
        <div class="login-header">
          <h2>🎉 抽奖管理系统</h2>
          <p>多租户管理平台</p>
        </div>
      </template>
      
      <el-alert
        title="请使用用户名登录"
        type="info"
        :closable="false"
        show-icon
        style="margin-bottom: 20px;"
      />
      
      <el-form :model="form" :rules="rules" ref="formRef" @keyup.enter="handleLogin">
        <el-form-item prop="username">
          <el-input 
            v-model="form.username" 
            placeholder="请输入用户名（非姓名）"
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
        
        <div style="text-align: center; margin-top: 15px;">
          <el-link type="primary" @click="showRegisterDialog">
            还没有账号？立即注册
          </el-link>
        </div>
        
        
      </el-form>
    </el-card>
    
    <!-- 注册对话框 -->
    <el-dialog
      v-model="registerDialogVisible"
      title="用户注册"
      width="450px"
      :close-on-click-modal="false"
    >
      <el-alert
        type="warning"
        :closable="false"
        style="margin-bottom: 20px;"
      >
        <template #title>
          <div style="font-size: 13px;">
            <strong>请注意：</strong>用户名用于登录，姓名用于显示
          </div>
        </template>
      </el-alert>
      
      <el-form :model="registerForm" :rules="registerRules" ref="registerFormRef" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input 
            v-model="registerForm.username" 
            placeholder="登录用：字母数字，4-20位"
          >
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="姓名" prop="first_name">
          <el-input 
            v-model="registerForm.first_name" 
            placeholder="显示用：真实姓名"
          >
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input 
            v-model="registerForm.password" 
            type="password"
            placeholder="至少6位"
            show-password
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="确认密码" prop="confirm_password">
          <el-input 
            v-model="registerForm.confirm_password" 
            type="password"
            placeholder="再次输入密码"
            show-password
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="registerDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleRegister" :loading="registerLoading">
          注册
        </el-button>
      </template>
    </el-dialog>
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
      loading: false,
      
      // 注册相关
      registerDialogVisible: false,
      registerLoading: false,
      registerForm: {
        username: '',
        password: '',
        confirm_password: '',
        first_name: ''
      },
      registerRules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' },
          { min: 4, max: 20, message: '用户名长度为4-20位', trigger: 'blur' },
          { pattern: /^[a-zA-Z0-9_]+$/, message: '只能包含字母、数字和下划线', trigger: 'blur' }
        ],
        first_name: [
          { required: true, message: '请输入姓名', trigger: 'blur' },
          { min: 2, max: 20, message: '姓名长度为2-20位', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, message: '密码至少6位', trigger: 'blur' }
        ],
        confirm_password: [
          { required: true, message: '请再次输入密码', trigger: 'blur' },
          { 
            validator: (rule, value, callback) => {
              if (value !== this.registerForm.password) {
                callback(new Error('两次输入的密码不一致'))
              } else {
                callback()
              }
            }, 
            trigger: 'blur' 
          }
        ]
      }
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
    },
    
    showRegisterDialog() {
      this.registerDialogVisible = true
      // 重置表单
      this.registerForm = {
        username: '',
        password: '',
        confirm_password: '',
        first_name: ''
      }
      // 清除验证错误
      this.$nextTick(() => {
        this.$refs.registerFormRef?.clearValidate()
      })
    },
    
    async handleRegister() {
      try {
        await this.$refs.registerFormRef.validate()
        
        this.registerLoading = true
        
        // 调用注册API（后端会自动登录）
        const user = await api.register({
          username: this.registerForm.username,
          password: this.registerForm.password,
          first_name: this.registerForm.first_name
        })
        
        // 存储用户信息
        localStorage.setItem('user', JSON.stringify(user))
        
        this.$message.success(`注册成功！欢迎您，${user.first_name || user.username}！`)
        
        // 关闭对话框
        this.registerDialogVisible = false
        
        // 跳转到首页
        setTimeout(() => {
          this.$router.push('/')
        }, 500)
        
      } catch (error) {
        console.error('注册失败:', error)
        if (error.response && error.response.data && error.response.data.error) {
          this.$message.error(error.response.data.error)
        } else {
          this.$message.error('注册失败，请重试')
        }
      } finally {
        this.registerLoading = false
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

<template>
  <div class="create-lottery">
    <el-card>
      <template #header>
        <span>创建抽奖</span>
      </template>

      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="抽奖标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入抽奖标题" />
        </el-form-item>

        <el-form-item label="抽奖说明" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入抽奖说明"
          />
        </el-form-item>

        <el-form-item label="奖品名称" prop="prize_name">
          <el-input v-model="form.prize_name" placeholder="请输入奖品名称" />
        </el-form-item>

        <el-form-item label="奖品数量" prop="prize_count">
          <el-input-number v-model="form.prize_count" :min="1" />
        </el-form-item>

        <el-form-item label="最大参与人数" prop="max_participants">
          <el-input-number v-model="form.max_participants" :min="0" />
          <span style="margin-left: 10px; color: #999;">0表示不限制</span>
        </el-form-item>

        <el-form-item label="开始时间" prop="start_time">
          <el-date-picker
            v-model="form.start_time"
            type="datetime"
            placeholder="选择开始时间"
            format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>

        <el-form-item label="结束时间" prop="end_time">
          <el-date-picker
            v-model="form.end_time"
            type="datetime"
            placeholder="选择结束时间"
            format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="submitForm" :loading="submitting">
            创建抽奖
          </el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import api from '../api'

export default {
  name: 'CreateLottery',
  data() {
    return {
      form: {
        title: '',
        description: '',
        prize_name: '',
        prize_count: 1,
        max_participants: 0,
        start_time: '',
        end_time: ''
      },
      rules: {
        title: [
          { required: true, message: '请输入抽奖标题', trigger: 'blur' }
        ],
        prize_name: [
          { required: true, message: '请输入奖品名称', trigger: 'blur' }
        ],
        start_time: [
          { required: true, message: '请选择开始时间', trigger: 'change' }
        ],
        end_time: [
          { required: true, message: '请选择结束时间', trigger: 'change' }
        ]
      },
      submitting: false
    }
  },
  methods: {
    async submitForm() {
      try {
        await this.$refs.formRef.validate()
        
        this.submitting = true
        
        const data = {
          ...this.form,
          start_time: new Date(this.form.start_time).toISOString(),
          end_time: new Date(this.form.end_time).toISOString()
        }
        
        await api.createLottery(data)
        
        this.$message.success('创建成功')
        this.$router.push('/lotteries')
      } catch (error) {
        if (error !== false) {
          this.$message.error('创建失败')
        }
      } finally {
        this.submitting = false
      }
    },
    resetForm() {
      this.$refs.formRef.resetFields()
    }
  }
}
</script>

<style scoped>
.create-lottery {
  max-width: 800px;
  margin: 0 auto;
}
</style>

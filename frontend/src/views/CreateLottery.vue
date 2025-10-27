<template>
  <div class="create-lottery">
    <el-card>
      <template #header>
        <span>{{ isEditMode ? '编辑抽奖' : '创建抽奖' }}</span>
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

        <!-- 多奖品设置区域 -->
        <el-divider content-position="left">
          <span style="font-weight: bold; color: #409EFF;">🏆 奖品设置</span>
        </el-divider>

        <div class="prizes-section">
          <div v-for="(prize, index) in form.prizes" :key="`prize-${index}`" class="prize-item">
            <div class="prize-header">
              <span class="prize-title">
                {{ getLevelText(prize.level) }} {{ prize.name || '' }}
                <small style="color: #999; margin-left: 10px;">(level: {{ prize.level }})</small>
              </span>
              <el-button 
                type="danger" 
                size="small" 
                plain
                @click="removePrize(index)"
                :disabled="form.prizes.length === 1"
              >
                删除奖品
              </el-button>
            </div>

            <div class="prize-body">
              <!-- 第一行：奖品名称 -->
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item 
                    :label="`奖品名称`" 
                    :prop="`prizes.${index}.name`"
                    :rules="[{ required: true, message: '请输入奖品名称', trigger: 'blur' }]"
                  >
                    <el-input v-model="prize.name" placeholder="例如：iPhone 15 Pro" />
                  </el-form-item>
                </el-col>
              </el-row>
              
              <!-- 第二行：中奖人数 + 奖品等级 -->
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="中奖人数" :prop="`prizes.${index}.winner_count`">
                    <el-input-number 
                      v-model="prize.winner_count" 
                      :min="1"
                      :max="9999"
                      :controls="false"
                      placeholder="1"
                      style="width: 100%;"
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="奖品等级" :prop="`prizes.${index}.level`">
                    <el-select 
                      :model-value="prize.level"
                      @update:model-value="(val) => { prize.level = val }"
                      placeholder="选择等级" 
                      style="width: 100%;"
                    >
                      <el-option key="level-1" label="🥇 一等奖" :value="1" />
                      <el-option key="level-2" label="🥈 二等奖" :value="2" />
                      <el-option key="level-3" label="🥉 三等奖" :value="3" />
                      <el-option key="level-4" label="4️⃣ 四等奖" :value="4" />
                      <el-option key="level-5" label="5️⃣ 五等奖" :value="5" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>

              <el-form-item label="奖品描述" :prop="`prizes.${index}.description`">
                <el-input 
                  v-model="prize.description" 
                  type="textarea" 
                  :rows="2"
                  placeholder="描述奖品详情（选填）"
                />
              </el-form-item>

              <!-- 暂时移除每个奖品的单独图片上传，使用全局图片 -->
            </div>
          </div>

          <el-button 
            type="primary" 
            plain 
            @click="addPrize"
            style="width: 100%; margin-top: 10px;"
          >
            <el-icon><Plus /></el-icon>
            添加更多奖品
          </el-button>
        </div>

        <!-- 保留旧的单个奖品字段（隐藏，用于向后兼容） -->
        <el-form-item label="奖品名称" prop="prize_name" v-show="false">
          <el-input v-model="form.prize_name" />
        </el-form-item>
        <el-form-item label="奖品数量" prop="prize_count" v-show="false">
          <el-input-number v-model="form.prize_count" :min="1" />
        </el-form-item>

        <!-- 全局奖品图片（可选） -->
        <el-form-item label="奖品图片" prop="prize_image">
          <div class="image-upload-wrapper">
            <el-upload
              class="prize-image-uploader"
              :action="uploadUrl"
              :show-file-list="false"
              :on-success="handleImageSuccess"
              :before-upload="beforeImageUpload"
              :headers="uploadHeaders"
              accept="image/*"
            >
              <img v-if="imageUrl" :src="imageUrl" class="prize-image" />
              <el-icon v-else class="prize-image-uploader-icon"><Plus /></el-icon>
            </el-upload>
            <button
              v-if="imageUrl"
              class="delete-image-btn"
              type="button"
              @click="deleteImage"
              title="删除图片"
            >
              ×
            </button>
          </div>
          <div class="upload-tip">支持jpg、png格式，大小不超过5MB（选填，仅用于展示）</div>
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
            :disabled-date="disabledStartDate"
            :disabled-hours="disabledStartHours"
            :disabled-minutes="disabledStartMinutes"
          />
        </el-form-item>

        <el-form-item label="结束时间" prop="end_time">
          <el-date-picker
            v-model="form.end_time"
            type="datetime"
            placeholder="选择结束时间"
            format="YYYY-MM-DD HH:mm:ss"
            :disabled-date="disabledEndDate"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="submitForm" :loading="submitting">
            {{ isEditMode ? '保存修改' : '创建抽奖' }}
          </el-button>
          <el-button @click="resetForm">重置</el-button>
          <el-button @click="goBack">返回</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import { Plus, Close } from '@element-plus/icons-vue'
import api from '../api'

export default {
  name: 'CreateLottery',
  components: {
    Plus,
    Close
  },
  data() {
    return {
      isEditMode: false,  // 是否为编辑模式
      lotteryId: null,    // 编辑的抽奖ID
      form: {
        title: '',
        description: '',
        prize_name: '',  // 保留用于向后兼容
        prize_image: null,  // 存储图片文件
        prize_count: 1,  // 保留用于向后兼容
        max_participants: 0,
        start_time: '',
        end_time: '',
        prizes: [  // 新增：多奖品数组
          {
            name: '',
            description: '',
            winner_count: 1,
            level: 1
          }
        ]
      },
      imageUrl: '',  // 图片预览 URL
      imageDeleted: false,  // 标记图片是否被删除
      uploadUrl: 'http://localhost:8000/api/lotteries/',  // 临时上传地址
      uploadHeaders: {},
      rules: {
        title: [
          { required: true, message: '请输入抽奖标题', trigger: 'blur' }
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
  mounted() {
    // 检查是否为编辑模式
    const id = this.$route.params.id
    if (id) {
      this.isEditMode = true
      this.lotteryId = id
      this.loadLotteryData(id)
    }
  },
  methods: {
    // 获取等级文本
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
    
    // 添加奖品
    addPrize() {
      const nextLevel = this.form.prizes.length + 1
      this.form.prizes.push({
        name: '',
        description: '',
        winner_count: 1,
        level: nextLevel <= 5 ? nextLevel : 5
      })
    },
    
    // 删除奖品
    removePrize(index) {
      if (this.form.prizes.length === 1) {
        this.$message.warning('至少需要保留一个奖品')
        return
      }
      this.$confirm('确定要删除这个奖品吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.form.prizes.splice(index, 1)
        this.$message.success('奖品已删除')
      }).catch(() => {})
    },
    
    // 加载抽奖数据（编辑模式）
    async loadLotteryData(id) {
      try {
        const data = await api.getLottery(id)
        console.log('加载的抽奖数据:', data)
        
        // 基本信息
        this.form = {
          title: data.title,
          description: data.description,
          prize_name: data.prize_name,
          prize_image: null,  // 不预加载文件，只显示图片
          prize_count: data.prize_count,
          max_participants: data.max_participants,
          start_time: new Date(data.start_time),
          end_time: new Date(data.end_time),
          prizes: []
        }
        
        // 如果有新格式的奖品数组，加载它
        if (data.prizes && data.prizes.length > 0) {
          const prizesData = data.prizes.map(prize => ({
            name: prize.name,
            description: prize.description || '',
            winner_count: Number(prize.winner_count),
            level: Number(prize.level),  // 确保是数字类型
            image: null  // 图片不预加载，只用于显示
          }))
          // Vue 3 中直接赋值即可
          this.form.prizes = prizesData
          console.log('加载的奖品列表:', this.form.prizes)
          // 验证每个奖品的 level 值
          this.form.prizes.forEach((p, i) => {
            console.log(`奖品 ${i}: level=${p.level}, type=${typeof p.level}`)
          })
        } else {
          // 如果是旧格式，用单个奖品初始化
          this.form.prizes = [{
            name: data.prize_name || '',
            description: '',
            winner_count: Number(data.prize_count) || 1,
            level: 1,
            image: null
          }]
        }
        
        // 如果有图片，设置预览URL
        if (data.prize_image) {
          // 如果是完整URL，直接使用；否则拼接后端地址
          this.imageUrl = data.prize_image.startsWith('http') 
            ? data.prize_image 
            : `http://localhost:8000${data.prize_image}`
        }
      } catch (error) {
        console.error('加载抽奖数据失败:', error)
        this.$message.error('加载抽奖数据失败')
        this.$router.push('/lotteries')
      }
    },
    
    // 图片上传前的校验
    beforeImageUpload(file) {
      const isImage = file.type.startsWith('image/')
      const isLt5M = file.size / 1024 / 1024 < 5

      if (!isImage) {
        this.$message.error('只能上传图片文件！')
        return false
      }
      if (!isLt5M) {
        this.$message.error('图片大小不能超过 5MB！')
        return false
      }
      
      // 保存文件到 form
      this.form.prize_image = file
      
      // 生成预览 URL
      this.imageUrl = URL.createObjectURL(file)
      
      // 重置删除标记
      this.imageDeleted = false
      
      // 阻止自动上传
      return false
    },
    
    // 图片上传成功（实际不会触发，因为我们用手动上传）
    handleImageSuccess(response, file) {
      this.imageUrl = URL.createObjectURL(file.raw)
    },
    
    // 删除图片
    deleteImage() {
      this.$confirm('确定要删除图片吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.imageUrl = ''
        this.form.prize_image = null
        this.imageDeleted = true
        this.$message.success('图片已删除')
      }).catch(() => {
        // 取消删除
      })
    },
    
    // 禁用开始时间：不能选择今天之前的日期
    disabledStartDate(date) {
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      return date.getTime() < today.getTime()
    },
    
    // 禁用开始时间的小时
    disabledStartHours() {
      const selectedDate = this.form.start_time ? new Date(this.form.start_time) : null
      const now = new Date()
      
      if (!selectedDate) return []
      
      // 如果选择的是今天，禁用当前时间之前的小时
      if (this.isSameDay(selectedDate, now)) {
        const currentHour = now.getHours()
        return Array.from({ length: currentHour }, (_, i) => i)
      }
      
      return []
    },
    
    // 禁用开始时间的分钟
    disabledStartMinutes(hour) {
      const selectedDate = this.form.start_time ? new Date(this.form.start_time) : null
      const now = new Date()
      
      if (!selectedDate) return []
      
      // 如果选择的是今天且是当前小时，禁用当前分钟之前的分钟
      if (this.isSameDay(selectedDate, now) && hour === now.getHours()) {
        const currentMinute = now.getMinutes()
        return Array.from({ length: currentMinute }, (_, i) => i)
      }
      
      return []
    },
    
    // 禁用结束时间：不能早于开始时间
    disabledEndDate(date) {
      if (!this.form.start_time) {
        // 如果没有选择开始时间，至少不能选今天之前
        const today = new Date()
        today.setHours(0, 0, 0, 0)
        return date.getTime() < today.getTime()
      }
      
      // 不能早于开始时间
      const startDate = new Date(this.form.start_time)
      startDate.setHours(0, 0, 0, 0)
      return date.getTime() < startDate.getTime()
    },
    
    // 判断是否为同一天
    isSameDay(date1, date2) {
      return date1.getFullYear() === date2.getFullYear() &&
             date1.getMonth() === date2.getMonth() &&
             date1.getDate() === date2.getDate()
    },
    
    // 格式化日期时间为本地时间字符串 (YYYY-MM-DD HH:MM:SS)
    formatDateTime(date) {
      const d = new Date(date)
      const year = d.getFullYear()
      const month = String(d.getMonth() + 1).padStart(2, '0')
      const day = String(d.getDate()).padStart(2, '0')
      const hours = String(d.getHours()).padStart(2, '0')
      const minutes = String(d.getMinutes()).padStart(2, '0')
      const seconds = String(d.getSeconds()).padStart(2, '0')
      return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
    },
    
    async submitForm() {
      try {
        await this.$refs.formRef.validate()
        
        // 额外验证：确保结束时间晚于开始时间
        if (new Date(this.form.end_time) <= new Date(this.form.start_time)) {
          this.$message.error('结束时间必须晚于开始时间')
          return
        }
        
        // 验证奖品信息
        if (!this.form.prizes || this.form.prizes.length === 0) {
          this.$message.error('至少需要设置一个奖品')
          return
        }
        
        for (let i = 0; i < this.form.prizes.length; i++) {
          if (!this.form.prizes[i].name || !this.form.prizes[i].name.trim()) {
            this.$message.error(`第${i + 1}个奖品的名称不能为空`)
            return
          }
        }
        
        this.submitting = true
        
        // 使用 FormData 支持文件上传
        const formData = new FormData()
        formData.append('title', this.form.title)
        formData.append('description', this.form.description)
        
        // 为了向后兼容，同时发送旧字段和新字段
        // 旧字段使用第一个奖品的信息
        formData.append('prize_name', this.form.prizes[0].name)
        formData.append('prize_count', this.form.prizes[0].winner_count)
        
        formData.append('max_participants', this.form.max_participants)
        formData.append('start_time', this.formatDateTime(this.form.start_time))
        formData.append('end_time', this.formatDateTime(this.form.end_time))
        
        // 新增：发送奖品数组（JSON格式）
        formData.append('prizes', JSON.stringify(this.form.prizes))
        
        // 处理图片上传
        if (this.form.prize_image) {
          formData.append('prize_image', this.form.prize_image)
        } else if (this.isEditMode && this.imageDeleted) {
          formData.append('prize_image', '')
        }
        
        // 根据模式调用不同的API
        if (this.isEditMode) {
          await api.updateLottery(this.lotteryId, formData)
          this.$message.success('修改成功')
        } else {
          await api.createLottery(formData)
          this.$message.success('创建成功')
        }
        
        this.$router.push('/lotteries')
      } catch (error) {
        console.error('提交失败:', error)
        if (error !== false) {
          this.$message.error(this.isEditMode ? '修改失败' : '创建失败')
        }
      } finally {
        this.submitting = false
      }
    },
    goBack() {
      this.$router.push('/lotteries')
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

/* 图片上传组件样式 */
.image-upload-wrapper {
  position: relative;
  display: inline-block;
}

.prize-image-uploader {
  display: inline-block;
}

.prize-image-uploader :deep(.el-upload) {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.3s;
  width: 178px;
  height: 178px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.prize-image-uploader :deep(.el-upload:hover) {
  border-color: #1890ff;
}

.prize-image-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.prize-image {
  width: 178px;
  height: 178px;
  object-fit: cover;
  display: block;
}

.upload-tip {
  font-size: 12px;
  color: #8c8c8c;
  margin-top: 8px;
  line-height: 1.5;
}

/* 删除图片按钮样式 */
.delete-image-btn {
  position: absolute;
  top: -8px;
  right: -8px;
  z-index: 10;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  border: 2px solid white;
  font-size: 20px;
  font-weight: bold;
  line-height: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  transition: all 0.3s;
  padding: 0;
}

.delete-image-btn:hover {
  transform: scale(1.15);
  background: rgba(0, 0, 0, 0.8);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.delete-image-btn:active {
  transform: scale(1.05);
}

/* 奖品设置区域样式 */
.prizes-section {
  margin: 20px 0;
}

.prize-item {
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  background: #fafafa;
  transition: all 0.3s;
}

.prize-item:hover {
  border-color: #409EFF;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.1);
}

.prize-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px dashed #e4e7ed;
}

.prize-title {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.prize-body {
  padding-top: 10px;
}
</style>

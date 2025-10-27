# 🖼️ 奖品图片上传功能说明

## 📋 功能概述

新增了**奖品图片上传功能**，管理员在创建抽奖时可以选择性上传奖品图片（非必填）。

---

## ✨ 功能特性

| 特性 | 说明 |
|------|------|
| **是否必填** | ❌ 否（可选字段） |
| **支持格式** | ✅ jpg、png、jpeg、gif 等所有图片格式 |
| **文件大小限制** | ✅ 最大 5MB |
| **图片预览** | ✅ 上传前本地预览 |
| **列表显示** | ✅ 抽奖列表中显示缩略图（60x60） |
| **详情显示** | ✅ 抽奖详情中显示大图（150x150，可点击放大） |
| **通知携带** | ✅ 开奖时如果有图片，会发送图片到 Telegram |

---

## 🎯 使用场景

### 1️⃣ **创建抽奖时上传**

在"创建抽奖"页面，奖品名称下方有"奖品图片"上传区域：

- 点击虚线框选择图片
- 上传后会显示预览
- 支持 jpg、png 等常见格式
- 大小不超过 5MB
- **非必填项**，可以不上传

### 2️⃣ **抽奖列表展示**

在"抽奖列表"页面：

- 新增"奖品图片"列
- 显示 60x60 的缩略图
- 点击图片可查看大图
- 无图片显示"无图片"

### 3️⃣ **抽奖详情展示**

在"抽奖详情"页面：

- 基本信息中显示"奖品图片"字段
- 显示 150x150 的图片
- 点击可以放大查看
- 无图片显示"无图片"

### 4️⃣ **中奖通知携带图片**

用户中奖时：

- **有图片**：发送带图片的 Telegram 消息（使用 sendPhoto API）
- **无图片**：只发送文字消息（使用 sendMessage API）

---

## 🔧 技术实现

### 后端（Django）

#### 1. 数据库字段

```python
# backend/lottery/models.py
class Lottery(models.Model):
    # ... 其他字段 ...
    prize_image = models.ImageField(
        upload_to='prizes/',  # 上传到 media/prizes/ 目录
        null=True,            # 允许为空
        blank=True,           # 表单可以不填
        verbose_name='奖品图片'
    )
```

#### 2. 序列化器

```python
# backend/lottery/serializers.py
class LotteryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lottery
        fields = [
            'title', 'description', 'prize_name', 'prize_count', 'prize_image',  # ← 包含图片字段
            'max_participants', 'start_time', 'end_time'
        ]
```

#### 3. 媒体文件配置

```python
# backend/lottery_backend/settings.py
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# 支持文件上传的 Parser
REST_FRAMEWORK = {
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',  # ← 文件上传
        'rest_framework.parsers.FormParser',       # ← 表单数据
    ],
}
```

#### 4. URL 配置

```python
# backend/lottery_backend/urls.py
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ...
]

# 开发环境下提供媒体文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

#### 5. 通知逻辑

```python
# backend/lottery/models.py
def _send_winner_notifications(self, winner_users):
    for user in winner_users:
        message = "🎉 恭喜您中奖啦！..."
        
        # 如果有图片，发送图片消息
        if self.prize_image:
            url = f'https://api.telegram.org/bot{bot_token}/sendPhoto'
            data = {
                'chat_id': user.telegram_id,
                'photo': f"http://localhost:8000{self.prize_image.url}",  # 图片 URL
                'caption': message,  # 图片说明
                'parse_mode': 'HTML'
            }
        else:
            # 只发送文字
            url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
            data = {
                'chat_id': user.telegram_id,
                'text': message,
                'parse_mode': 'HTML'
            }
        
        requests.post(url, json=data, timeout=10)
```

---

### 前端（Vue + Element Plus）

#### 1. 创建抽奖页面

```vue
<!-- frontend/src/views/CreateLottery.vue -->
<template>
  <el-form-item label="奖品图片" prop="prize_image">
    <el-upload
      class="prize-image-uploader"
      :action="uploadUrl"
      :show-file-list="false"
      :on-success="handleImageSuccess"
      :before-upload="beforeImageUpload"
      accept="image/*"
    >
      <!-- 预览图片 -->
      <img v-if="imageUrl" :src="imageUrl" class="prize-image" />
      <!-- 上传图标 -->
      <el-icon v-else class="prize-image-uploader-icon"><Plus /></el-icon>
    </el-upload>
    <div class="upload-tip">支持jpg、png格式，大小不超过5MB（非必填）</div>
  </el-form-item>
</template>

<script>
export default {
  methods: {
    // 上传前校验
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
      
      // 保存文件
      this.form.prize_image = file
      // 生成预览
      this.imageUrl = URL.createObjectURL(file)
      
      return false  // 阻止自动上传
    },
    
    // 提交表单
    async submitForm() {
      // 使用 FormData 支持文件上传
      const formData = new FormData()
      formData.append('title', this.form.title)
      formData.append('description', this.form.description)
      // ... 其他字段 ...
      
      // 如果有图片，添加到 FormData
      if (this.form.prize_image) {
        formData.append('prize_image', this.form.prize_image)
      }
      
      await api.createLottery(formData)
    }
  }
}
</script>

<style scoped>
.prize-image-uploader :deep(.el-upload) {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  width: 178px;
  height: 178px;
  cursor: pointer;
  transition: all 0.3s;
}

.prize-image-uploader :deep(.el-upload:hover) {
  border-color: #1890ff;
}

.prize-image {
  width: 178px;
  height: 178px;
  object-fit: cover;
}
</style>
```

#### 2. API 配置

```javascript
// frontend/src/api/index.js
createLottery(data) {
  // 检查是否为 FormData（包含文件上传）
  const isFormData = data instanceof FormData
  return api.post('/lotteries/', data, {
    headers: isFormData ? { 'Content-Type': 'multipart/form-data' } : {}
  })
}
```

#### 3. 抽奖列表页面

```vue
<!-- frontend/src/views/LotteryList.vue -->
<el-table-column label="奖品图片" width="100">
  <template #default="scope">
    <el-image
      v-if="scope.row.prize_image"
      :src="getImageUrl(scope.row.prize_image)"
      :preview-src-list="[getImageUrl(scope.row.prize_image)]"
      fit="cover"
      style="width: 60px; height: 60px; border-radius: 4px; cursor: pointer;"
    />
    <span v-else style="color: #999;">无图片</span>
  </template>
</el-table-column>

<script>
export default {
  methods: {
    getImageUrl(imagePath) {
      if (imagePath.startsWith('http')) {
        return imagePath
      }
      return `http://localhost:8000${imagePath}`
    }
  }
}
</script>
```

#### 4. 抽奖详情页面

```vue
<!-- frontend/src/views/LotteryDetail.vue -->
<el-descriptions-item label="奖品图片" :span="2">
  <el-image
    v-if="lottery.prize_image"
    :src="getImageUrl(lottery.prize_image)"
    :preview-src-list="[getImageUrl(lottery.prize_image)]"
    fit="cover"
    style="width: 150px; height: 150px; border-radius: 8px; cursor: pointer;"
  />
  <span v-else style="color: #999;">无图片</span>
</el-descriptions-item>
```

---

## 📁 文件存储

### 存储位置

```
tg_choujiang/
├── backend/
│   ├── media/              ← 媒体文件根目录
│   │   └── prizes/         ← 奖品图片存储目录
│   │       ├── image1.jpg
│   │       ├── image2.png
│   │       └── ...
│   └── ...
```

### 访问 URL

- **开发环境**: `http://localhost:8000/media/prizes/image1.jpg`
- **生产环境**: 需要配置 Nginx 或 CDN 提供静态文件服务

---

## 🎨 UI 效果

### 创建抽奖页面

```
┌─────────────────────────────────────┐
│  奖品图片                            │
│  ┌─────────────────┐                │
│  │                 │                │
│  │     📷 +        │  ← 虚线框，点击上传  │
│  │                 │                │
│  └─────────────────┘                │
│  支持jpg、png格式，大小不超过5MB（非必填）│
└─────────────────────────────────────┘

上传后：
┌─────────────────────────────────────┐
│  奖品图片                            │
│  ┌─────────────────┐                │
│  │                 │                │
│  │   [奖品图片]     │  ← 显示预览    │
│  │                 │                │
│  └─────────────────┘                │
│  支持jpg、png格式，大小不超过5MB（非必填）│
└─────────────────────────────────────┘
```

### 抽奖列表

```
┌──────┬─────────┬────────┬─────────┬────┐
│ ID   │ 标题     │ 奖品图片│ 奖品    │... │
├──────┼─────────┼────────┼─────────┼────┤
│ 1    │ iPhone  │ [图片] │ iPhone  │... │
│ 2    │ 现金    │ 无图片  │ 1000元  │... │
└──────┴─────────┴────────┴─────────┴────┘
```

### Telegram 通知

**有图片时**：
```
┌──────────────────────────────┐
│  [奖品图片]                   │
│                              │
│  🎉 恭喜您中奖啦！            │
│                              │
│  📋 抽奖活动：iPhone 15 抽奖 │
│  🎁 奖品：iPhone 15 Pro Max  │
│  📝 说明：...                │
│                              │
│  请联系管理员领取奖品！       │
└──────────────────────────────┘
```

**无图片时**：
```
┌──────────────────────────────┐
│  🎉 恭喜您中奖啦！            │
│                              │
│  📋 抽奖活动：现金抽奖        │
│  🎁 奖品：1000元现金         │
│  📝 说明：...                │
│                              │
│  请联系管理员领取奖品！       │
└──────────────────────────────┘
```

---

## ✅ 测试清单

### 功能测试

- [ ] **上传图片**：选择图片后能正常预览
- [ ] **文件类型校验**：上传非图片文件时提示错误
- [ ] **文件大小校验**：上传超过 5MB 的图片时提示错误
- [ ] **创建抽奖**：带图片创建成功，数据库正确保存
- [ ] **列表显示**：抽奖列表中正确显示缩略图
- [ ] **详情显示**：抽奖详情中正确显示大图
- [ ] **图片预览**：点击图片能放大查看
- [ ] **无图片情况**：不上传图片也能正常创建
- [ ] **通知测试**：有图片时发送 sendPhoto，无图片时发送 sendMessage

### 兼容性测试

- [ ] **浏览器兼容**：Chrome、Firefox、Safari、Edge
- [ ] **移动端适配**：手机浏览器正常显示
- [ ] **Telegram 客户端**：图片消息正常显示

---

## 🐛 常见问题

### 1. 图片上传后不显示？

**原因**：Django 媒体文件路由未配置

**解决**：
```python
# backend/lottery_backend/urls.py
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### 2. 前端显示图片 404？

**原因**：图片 URL 拼接错误

**解决**：
```javascript
getImageUrl(imagePath) {
  if (imagePath.startsWith('http')) {
    return imagePath
  }
  return `http://localhost:8000${imagePath}`  // 确保以 / 开头
}
```

### 3. Telegram 通知图片不显示？

**原因**：Telegram 无法访问 localhost

**解决**：
- **开发环境**：使用内网穿透（ngrok、frp）
- **生产环境**：使用公网域名 + Nginx

### 4. 上传大图片很慢？

**原因**：文件太大

**建议**：
- 前端添加图片压缩（使用 `compressorjs` 库）
- 后端添加图片缩略图生成（使用 Pillow）

---

## 🚀 优化建议

### 1. 图片压缩

```javascript
// 前端压缩
import Compressor from 'compressorjs'

beforeImageUpload(file) {
  return new Promise((resolve, reject) => {
    new Compressor(file, {
      quality: 0.8,
      maxWidth: 1024,
      maxHeight: 1024,
      success(result) {
        resolve(result)
      },
      error(err) {
        reject(err)
      }
    })
  })
}
```

### 2. 缩略图生成

```python
# 后端生成缩略图
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

def save(self, *args, **kwargs):
    if self.prize_image:
        # 生成缩略图
        img = Image.open(self.prize_image)
        img.thumbnail((300, 300))
        # 保存缩略图
        # ...
    super().save(*args, **kwargs)
```

### 3. CDN 加速

```python
# 使用七牛云、阿里云 OSS 等
MEDIA_URL = 'https://cdn.example.com/media/'
```

### 4. 图片懒加载

```vue
<el-image
  :src="imageUrl"
  lazy
  :scroll-container="scrollContainer"
/>
```

---

## 📝 总结

✅ **已完成**：
- ✅ 后端 Model 添加 `prize_image` 字段
- ✅ 后端配置文件上传支持
- ✅ 后端媒体文件路由配置
- ✅ 前端创建页面添加图片上传
- ✅ 前端列表页面显示图片
- ✅ 前端详情页面显示图片
- ✅ 通知消息携带图片

🎯 **功能特点**：
- ✅ 非必填，灵活使用
- ✅ 完整的文件校验
- ✅ 美观的 UI 设计
- ✅ 完善的预览功能
- ✅ 智能的通知逻辑

🚀 **下一步**：
- 考虑添加图片压缩
- 考虑使用 CDN 加速
- 考虑添加图片裁剪功能
- 考虑添加多图上传（轮播展示）

---

**文档更新时间**: 2025-10-25

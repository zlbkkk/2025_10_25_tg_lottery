# 🎉 Telegram 抽奖机器人

一个功能完整的 Telegram 抽奖机器人系统，包含后端API、前端管理界面和Telegram Bot。

## ✨ 功能特性

- 🎁 **创建抽奖** - 灵活设置抽奖规则和奖品
- 🎟️ **用户参与** - 通过 Telegram Bot 一键参与
- 🎊 **自动开奖** - 随机抽取中奖者并自动通知
- 📊 **数据统计** - 实时查看抽奖数据和参与情况
- 🔐 **管理后台** - 完善的 Django Admin 管理界面

## 🚀 快速启动

### 方式1：一键启动（推荐）

双击 `START_ALL.bat` 即可启动所有服务！

### 方式2：分别启动

```bash
# 1. 启动后端
cd backend
python manage.py runserver

# 2. 启动前端
cd frontend
npm run serve

# 3. 启动 Bot（需要先配置 Token）
cd bot
python bot.py
```

## 📁 项目结构

```
tg_choujiang/
├── backend/          # Django 后端
├── frontend/         # Vue 前端
├── bot/             # Telegram Bot
├── START_ALL.bat    # 一键启动脚本
└── README.md        # 本文件
```

## 🛠️ 技术栈

- **后端**: Django 3.2 + Django REST Framework
- **前端**: Vue 3 + Element Plus
- **Bot**: python-telegram-bot 20.7
- **数据库**: MySQL 5.7+

## 🔧 环境要求

- Python 3.8+
- Node.js 14+
- MySQL 5.7+

## 📝 配置说明

**⚠️ 重要：所有配置统一在 `bot/config.py` 文件中管理！**

### 1. Bot Token 配置（必须）

编辑 `bot/config.py`，修改 `BOT_TOKEN`：

```python
# Telegram Bot Token
BOT_TOKEN = 'your_bot_token_here'
```

**获取 Bot Token：**
1. 在 Telegram 搜索 @BotFather
2. 发送 `/newbot` 创建机器人
3. 复制获得的 Token 并填入上面的配置

### 2. 数据库配置（可选）

如需修改数据库配置，编辑 `bot/config.py` 中的 `DATABASE_CONFIG`：

```python
DATABASE_CONFIG = {
    'ENGINE': 'django.db.backends.mysql',
    'NAME': 'lottery_db',
    'USER': 'root',
    'PASSWORD': '123456',
    'HOST': 'localhost',
    'PORT': '3306',
}
```

**默认配置：**
- 主机：localhost
- 端口：3306
- 数据库：lottery_db
- 用户：root
- 密码：123456

### 3. API URL 配置（可选）

如果后端地址不是 `http://localhost:8000`，需要修改 `bot/config.py` 中的 `API_URL`：

```python
API_URL = 'http://your-backend-url/api'
```

## 🌐 访问地址

- **前端界面**: http://localhost:8080
- **管理后台**: http://localhost:8000/admin (admin/admin123)
- **后端 API**: http://localhost:8000/api

## 🎯 使用流程

### 管理员操作

1. 访问前端界面 http://localhost:8080
2. 点击"创建抽奖"
3. 填写抽奖信息并提交
4. 等待用户参与
5. 在"抽奖列表"中点击"开奖"

### 用户操作

1. 在 Telegram 搜索你的 Bot
2. 发送 `/start` 注册
3. 点击"🎟️ 参与抽奖"
4. 选择想参与的抽奖
5. 等待开奖通知

## 📊 数据库初始化

首次运行需要初始化数据库：

```bash
cd backend
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser  # 创建管理员账号
```

## 🔒 安全提示

- 生产环境请修改 `SECRET_KEY`
- 修改数据库密码
- 配置 `ALLOWED_HOSTS`
- 使用 HTTPS

## 📮 问题反馈

如有问题，请检查：
- 后端服务是否启动（端口 8000）
- 前端服务是否启动（端口 8080）
- Bot Token 是否正确配置
- 数据库是否正常连接

## 📄 许可证

MIT License

---

⭐ 如果这个项目对你有帮助，请给个 Star！

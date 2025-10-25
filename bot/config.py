"""
统一配置文件
所有服务（Bot、Backend）都从这里读取配置
"""

# ================================
# Telegram Bot 配置
# ================================

# Telegram Bot Token
# 从 @BotFather 获取
BOT_TOKEN = '8057896490:AAHyuY9GnXIAqWsdwSoRO_SSsE3x4xIVsZ8'

# Backend API URL
# Bot 调用后端 API 的地址
API_URL = 'http://localhost:8000/api'

# ================================
# 数据库配置（后端使用）
# ================================

DATABASE_CONFIG = {
    'ENGINE': 'django.db.backends.mysql',
    'NAME': 'lottery_db',
    'USER': 'root',
    'PASSWORD': '123456',
    'HOST': 'localhost',
    'PORT': '3306',
    'OPTIONS': {
        'charset': 'utf8mb4',
    }
}

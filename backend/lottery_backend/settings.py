"""
Django settings for lottery_backend project.
"""

from pathlib import Path
import os
import sys

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# 添加 bot 目录到 Python 路径，以便导入统一配置
sys.path.insert(0, str(BASE_DIR.parent / 'bot'))

# 从统一配置文件导入配置
try:
    from config import BOT_TOKEN, DATABASE_CONFIG
except ImportError:
    # 如果导入失败，使用默认配置
    BOT_TOKEN = None
    DATABASE_CONFIG = {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'lottery_db',
        'USER': 'root',
        'PASSWORD': '123456',
        'HOST': 'localhost',
        'PORT': '3306',
    }


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-your-secret-key-change-in-production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'lottery',  # 抽奖应用
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'lottery.middleware.UpdateLastActivityMiddleware',  # 更新最后活动时间
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'lottery_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'lottery_backend.wsgi.application'


# Database（从统一配置文件读取）
DATABASES = {
    'default': {
        **DATABASE_CONFIG,
        'OPTIONS': {
            **DATABASE_CONFIG.get('OPTIONS', {}),
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

# 设置为 False：数据库直接存储本地时间（北京时间），不进行UTC转换
USE_TZ = False


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True  # 开发环境允许所有来源
CORS_ALLOW_CREDENTIALS = True

# CSRF settings - 豁免 API 路径（前后端分离）
CSRF_TRUSTED_ORIGINS = ['http://localhost:8080', 'http://127.0.0.1:8080']
CSRF_COOKIE_HTTPONLY = False  # 允许 JavaScript 读取 CSRF token
CSRF_COOKIE_SAMESITE = 'Lax'

# Session 配置
SESSION_COOKIE_AGE = 86400 * 7  # 7天
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'lottery.authentication.CsrfExemptSessionAuthentication',  # 自定义认证类，不检查 CSRF
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',  # 支持文件上传
        'rest_framework.parsers.FormParser',  # 支持表单数据
    ],
    # 时区设置：返回本地化时间
    'DATETIME_FORMAT': '%Y-%m-%d %H:%M:%S',
}

# Telegram Bot 配置（从统一配置文件读取）
TELEGRAM_BOT_TOKEN = BOT_TOKEN

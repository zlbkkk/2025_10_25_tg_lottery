"""
Lottery 应用 URL 配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TelegramUserViewSet,
    LotteryViewSet,
    ParticipationViewSet,
    WinnerViewSet
)
from .auth_views import (
    login_view,
    logout_view,
    get_current_user,
    register_view,
    change_password_view,
    bot_config_view,
    LoginRecordViewSet
)

router = DefaultRouter()
router.register(r'users', TelegramUserViewSet, basename='user')
router.register(r'lotteries', LotteryViewSet, basename='lottery')
router.register(r'participations', ParticipationViewSet, basename='participation')
router.register(r'winners', WinnerViewSet, basename='winner')
router.register(r'login-records', LoginRecordViewSet, basename='login-record')

urlpatterns = [
    # 认证相关路由
    path('auth/login/', login_view, name='login'),
    path('auth/logout/', logout_view, name='logout'),
    path('auth/me/', get_current_user, name='current-user'),
    path('auth/register/', register_view, name='register'),
    path('auth/change-password/', change_password_view, name='change-password'),
    
    # Bot配置路由
    path('bot-config/', bot_config_view, name='bot-config'),
    
    # ViewSet 路由
    path('', include(router.urls)),
]

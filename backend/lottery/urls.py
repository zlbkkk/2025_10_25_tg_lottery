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
    register_view
)

router = DefaultRouter()
router.register(r'users', TelegramUserViewSet, basename='user')
router.register(r'lotteries', LotteryViewSet, basename='lottery')
router.register(r'participations', ParticipationViewSet, basename='participation')
router.register(r'winners', WinnerViewSet, basename='winner')

urlpatterns = [
    # 认证相关路由
    path('auth/login/', login_view, name='login'),
    path('auth/logout/', logout_view, name='logout'),
    path('auth/me/', get_current_user, name='current-user'),
    path('auth/register/', register_view, name='register'),
    
    # ViewSet 路由
    path('', include(router.urls)),
]

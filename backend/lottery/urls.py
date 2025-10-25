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

router = DefaultRouter()
router.register(r'users', TelegramUserViewSet, basename='user')
router.register(r'lotteries', LotteryViewSet, basename='lottery')
router.register(r'participations', ParticipationViewSet, basename='participation')
router.register(r'winners', WinnerViewSet, basename='winner')

urlpatterns = [
    path('', include(router.urls)),
]

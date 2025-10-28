"""
中间件 - 自动更新用户最后活动时间
"""
from django.utils import timezone
from .models import LoginRecord


class UpdateLastActivityMiddleware:
    """
    中间件：自动更新登录用户的最后活动时间
    每次API请求都会更新 last_activity
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 请求前处理
        if request.user.is_authenticated:
            # 更新该用户当前活跃会话的最后活动时间
            LoginRecord.objects.filter(
                user=request.user,
                is_active=True,
                logout_time__isnull=True
            ).update(last_activity=timezone.now())
        
        # 继续处理请求
        response = self.get_response(request)
        
        return response


"""
中间件 - 自动更新用户最后活动时间和检测超时
"""
from django.utils import timezone
from django.contrib.auth import logout
from datetime import timedelta
from .models import LoginRecord


class UpdateLastActivityMiddleware:
    """
    中间件：自动更新登录用户的最后活动时间并检测超时
    - 每次API请求都会更新 last_activity
    - 检测用户是否超过1小时无活动，如是则自动登出
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.timeout_duration = timedelta(hours=1)  # 1小时超时

    def __call__(self, request):
        # 请求前处理
        if request.user.is_authenticated:
            now = timezone.now()
            
            # 查找当前用户的活跃登录记录
            active_record = LoginRecord.objects.filter(
                user=request.user,
                is_active=True,
                logout_time__isnull=True,
                session_key=request.session.session_key
            ).first()
            
            if active_record:
                # 检查是否超时（距离上次活动超过1小时）
                if active_record.last_activity:
                    time_since_last_activity = now - active_record.last_activity
                    
                    if time_since_last_activity > self.timeout_duration:
                        # 超时，标记登录记录为结束
                        active_record.logout_time = now
                        active_record.is_active = False
                        active_record.save()
                        
                        # 清除session，强制用户重新登录
                        logout(request)
                        
                        # 不继续处理请求，返回401未授权
                        from django.http import JsonResponse
                        return JsonResponse({
                            'error': '会话已超时，请重新登录',
                            'code': 'SESSION_TIMEOUT'
                        }, status=401)
                
                # 未超时，更新最后活动时间
                active_record.last_activity = now
                active_record.save()
        
        # 继续处理请求
        response = self.get_response(request)
        
        return response


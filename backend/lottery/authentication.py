"""
自定义认证类 - 禁用 CSRF 检查的 Session 认证
"""
from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    Session 认证，但不进行 CSRF 检查
    适用于前后端分离架构
    """
    def enforce_csrf(self, request):
        """
        重写此方法，不执行 CSRF 检查
        """
        return  # 不做任何检查

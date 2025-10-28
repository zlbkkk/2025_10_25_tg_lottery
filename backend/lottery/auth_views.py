"""
用户认证视图 - 多租户管理员登录
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils import timezone
from .models import BotConfig, LoginRecord
from .serializers import BotConfigSerializer, LoginRecordSerializer
import re


def get_client_ip(request):
    """获取客户端真实IP地址"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def parse_user_agent(user_agent_string):
    """解析User-Agent字符串，提取设备类型和浏览器信息"""
    if not user_agent_string:
        return None, None
    
    device_type = None
    browser = None
    
    # 检测设备类型
    if re.search(r'Mobile|Android|iPhone|iPad', user_agent_string, re.I):
        if re.search(r'iPad', user_agent_string, re.I):
            device_type = 'iPad'
        elif re.search(r'iPhone', user_agent_string, re.I):
            device_type = 'iPhone'
        elif re.search(r'Android', user_agent_string, re.I):
            device_type = 'Android'
        else:
            device_type = 'Mobile'
    elif re.search(r'Windows', user_agent_string, re.I):
        device_type = 'Windows'
    elif re.search(r'Macintosh|Mac OS X', user_agent_string, re.I):
        device_type = 'Mac'
    elif re.search(r'Linux', user_agent_string, re.I):
        device_type = 'Linux'
    else:
        device_type = 'Unknown'
    
    # 检测浏览器
    if re.search(r'Edg/', user_agent_string, re.I):
        browser = 'Edge'
    elif re.search(r'Chrome/', user_agent_string, re.I):
        browser = 'Chrome'
    elif re.search(r'Firefox/', user_agent_string, re.I):
        browser = 'Firefox'
    elif re.search(r'Safari/', user_agent_string, re.I) and not re.search(r'Chrome/', user_agent_string, re.I):
        browser = 'Safari'
    elif re.search(r'Opera|OPR/', user_agent_string, re.I):
        browser = 'Opera'
    else:
        browser = 'Unknown'
    
    return device_type, browser


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    管理员登录
    POST /api/auth/login/
    Body: {"username": "admin", "password": "password"}
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': '用户名和密码不能为空'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        login(request, user)
        
        # 记录登录信息
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        device_type, browser = parse_user_agent(user_agent)
        
        # 创建登录记录
        login_record = LoginRecord.objects.create(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            device_type=device_type,
            browser=browser,
            session_key=request.session.session_key,
            last_activity=timezone.now(),  # 记录最后活动时间
            is_active=True
        )
        
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        })
    else:
        return Response(
            {'error': '用户名或密码错误'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    管理员登出
    POST /api/auth/logout/
    """
    # 记录登出时间
    session_key = request.session.session_key
    if session_key:
        # 找到当前会话的登录记录并更新登出时间
        LoginRecord.objects.filter(
            user=request.user,
            session_key=session_key,
            is_active=True
        ).update(
            logout_time=timezone.now(),
            is_active=False
        )
    
    logout(request)
    return Response({'message': '登出成功'})


@api_view(['GET'])
@ensure_csrf_cookie
def get_current_user(request):
    """
    获取当前登录用户信息
    GET /api/auth/me/
    """
    if request.user.is_authenticated:
        return Response({
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
        })
    else:
        return Response(
            {'error': '未登录'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    """
    修改当前用户密码
    POST /api/auth/change-password/
    Body: {
        "old_password": "旧密码",
        "new_password": "新密码"
    }
    """
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    
    if not old_password or not new_password:
        return Response(
            {'error': '旧密码和新密码不能为空'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # 验证旧密码
    if not request.user.check_password(old_password):
        return Response(
            {'error': '旧密码不正确'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # 设置新密码
    request.user.set_password(new_password)
    request.user.save()
    
    return Response({
        'message': '密码修改成功，请重新登录'
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """
    管理员注册
    POST /api/auth/register/
    Body: {
        "username": "admin",
        "password": "password",
        "email": "admin@example.com",
        "first_name": "管理员",
        "last_name": "账号"
    }
    """
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')
    first_name = request.data.get('first_name', '')
    last_name = request.data.get('last_name', '')
    
    if not username or not password:
        return Response(
            {'error': '用户名和密码不能为空'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if User.objects.filter(username=username).exists():
        return Response(
            {'error': '用户名已存在'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = User.objects.create_user(
        username=username,
        password=password,
        email=email,
        first_name=first_name,
        last_name=last_name
    )
    
    # 自动登录
    login(request, user)
    
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
    }, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def bot_config_view(request):
    """
    获取或更新当前用户的Bot配置
    GET /api/bot-config/  - 获取配置
    PUT /api/bot-config/  - 更新配置
    Body: {
        "bot_token": "123456:ABC-DEF...",
        "bot_username": "@MyLotteryBot",
        "is_active": true
    }
    """
    # 获取或创建Bot配置
    bot_config, created = BotConfig.objects.get_or_create(
        admin_user=request.user
    )
    
    if request.method == 'GET':
        serializer = BotConfigSerializer(bot_config)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        # 验证 Bot Token 唯一性
        new_token = request.data.get('bot_token')
        if new_token:
            # 检查是否有其他用户使用了相同的 Token
            duplicate_config = BotConfig.objects.filter(
                bot_token=new_token
            ).exclude(admin_user=request.user).first()
            
            if duplicate_config:
                return Response({
                    'error': 'Token冲突：该 Bot Token 已被其他管理员使用',
                    'detail': f'该 Token 已被用户 "{duplicate_config.admin_user.username}" 使用。每个管理员必须创建自己独立的 Bot。',
                    'help': '请前往 Telegram 搜索 @BotFather，发送 /newbot 创建一个新的 Bot。'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = BotConfigSerializer(bot_config, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Bot配置已更新',
                'data': serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginRecordViewSet(ReadOnlyModelViewSet):
    """
    登录记录 ViewSet - 只读（仅超级管理员可访问）
    GET /api/login-records/  - 获取所有用户的登录记录列表
    GET /api/login-records/{id}/  - 获取单个登录记录详情
    """
    serializer_class = LoginRecordSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None  # 禁用分页，直接返回所有记录
    
    def get_queryset(self):
        """只有超级管理员（username=admin）可以查看所有用户的登录记录"""
        user = self.request.user
        
        # 检查是否是超级管理员
        if user.username != 'admin':
            # 非管理员返回空结果
            return LoginRecord.objects.none()
        
        # 超级管理员可以看到所有登录记录
        return LoginRecord.objects.all()
    
    def list(self, request, *args, **kwargs):
        """重写list方法，增加权限检查"""
        if request.user.username != 'admin':
            return Response({
                'error': '权限不足',
                'detail': '只有超级管理员才能查看登录记录'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        """重写retrieve方法，增加权限检查"""
        if request.user.username != 'admin':
            return Response({
                'error': '权限不足',
                'detail': '只有超级管理员才能查看登录记录'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().retrieve(request, *args, **kwargs)

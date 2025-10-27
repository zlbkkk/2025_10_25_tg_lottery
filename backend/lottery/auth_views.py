"""
用户认证视图 - 多租户管理员登录
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import ensure_csrf_cookie


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

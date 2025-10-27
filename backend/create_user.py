"""
快速创建新的管理员账号
用法：python create_user.py
"""
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lottery_backend.settings')
django.setup()

from django.contrib.auth.models import User

print("=" * 60)
print("创建新管理员账号")
print("=" * 60)

# 从命令行参数获取或交互式输入
if len(sys.argv) >= 3:
    # 命令行模式：python create_user.py boss1 password123 老板1
    username = sys.argv[1]
    password = sys.argv[2]
    first_name = sys.argv[3] if len(sys.argv) >= 4 else username
    email = sys.argv[4] if len(sys.argv) >= 5 else f"{username}@example.com"
else:
    # 交互式模式
    print("\n请输入新用户信息（直接回车使用默认值）\n")
    username = input("用户名: ").strip()
    if not username:
        print("❌ 用户名不能为空！")
        exit(1)
    
    password = input("密码: ").strip()
    if not password:
        print("❌ 密码不能为空！")
        exit(1)
    
    first_name = input(f"姓名（默认: {username}）: ").strip() or username
    email = input(f"邮箱（默认: {username}@example.com）: ").strip() or f"{username}@example.com"

# 检查用户名是否已存在
if User.objects.filter(username=username).exists():
    print(f"\n❌ 错误：用户名 '{username}' 已存在！")
    print("\n现有用户列表：")
    for user in User.objects.all():
        print(f"  - {user.username} ({user.first_name or '无姓名'})")
    exit(1)

# 创建用户
try:
    user = User.objects.create_user(
        username=username,
        password=password,
        email=email,
        first_name=first_name
    )
    
    print("\n" + "=" * 60)
    print("✅ 管理员账号创建成功！")
    print("=" * 60)
    print(f"用户名: {username}")
    print(f"密码: {password}")
    print(f"姓名: {first_name}")
    print(f"邮箱: {email}")
    print("\n📝 请将登录信息发送给对应的管理员")
    print("⚠️  请妥善保管登录信息！")
    
    # 显示当前所有用户
    total_users = User.objects.count()
    print(f"\n当前系统共有 {total_users} 个管理员账号")
    
except Exception as e:
    print(f"\n❌ 创建用户失败: {str(e)}")
    exit(1)

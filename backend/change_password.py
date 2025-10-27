"""
修改管理员密码
用法：python change_password.py
"""
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lottery_backend.settings')
django.setup()

from django.contrib.auth.models import User

print("=" * 60)
print("修改管理员密码")
print("=" * 60)

# 从命令行参数获取或交互式输入
if len(sys.argv) >= 3:
    # 命令行模式：python change_password.py boss1 newpassword123
    username = sys.argv[1]
    new_password = sys.argv[2]
else:
    # 交互式模式
    print("\n当前管理员列表：")
    users = User.objects.all().order_by('username')
    for user in users:
        print(f"  - {user.username} ({user.first_name or '无姓名'})")
    
    print()
    username = input("请输入要修改密码的用户名: ").strip()
    if not username:
        print("❌ 用户名不能为空！")
        exit(1)
    
    new_password = input("请输入新密码: ").strip()
    if not new_password:
        print("❌ 密码不能为空！")
        exit(1)

# 查找用户
try:
    user = User.objects.get(username=username)
except User.DoesNotExist:
    print(f"\n❌ 错误：用户 '{username}' 不存在！")
    print("\n当前存在的用户：")
    for u in User.objects.all():
        print(f"  - {u.username}")
    exit(1)

# 修改密码
try:
    user.set_password(new_password)
    user.save()
    
    print("\n" + "=" * 60)
    print("✅ 密码修改成功！")
    print("=" * 60)
    print(f"用户名: {username}")
    print(f"新密码: {new_password}")
    print("\n📝 请将新密码告知用户")
    print("⚠️  建议用户登录后自行修改密码")
    
except Exception as e:
    print(f"\n❌ 修改密码失败: {str(e)}")
    exit(1)

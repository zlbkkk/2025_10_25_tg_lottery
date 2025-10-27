"""
创建初始管理员账号
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lottery_backend.settings')
django.setup()

from django.contrib.auth.models import User

print("=" * 60)
print("创建管理员账号")
print("=" * 60)

username = input("请输入用户名（默认: admin）: ").strip() or "admin"
email = input("请输入邮箱（默认: admin@example.com）: ").strip() or "admin@example.com"
password = input("请输入密码（默认: admin123）: ").strip() or "admin123"
first_name = input("请输入姓名（默认: 管理员）: ").strip() or "管理员"

if User.objects.filter(username=username).exists():
    print(f"\n❌ 用户名 '{username}' 已存在！")
    print("请使用其他用户名或删除现有用户。")
else:
    user = User.objects.create_user(
        username=username,
        password=password,
        email=email,
        first_name=first_name
    )
    print(f"\n✅ 管理员账号创建成功！")
    print(f"用户名: {username}")
    print(f"密码: {password}")
    print(f"邮箱: {email}")
    print(f"姓名: {first_name}")
    print("\n请妥善保管您的登录信息！")

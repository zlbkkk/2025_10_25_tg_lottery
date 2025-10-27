"""
查看所有管理员账号
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lottery_backend.settings')
django.setup()

from django.contrib.auth.models import User
from lottery.models import Lottery

print("=" * 80)
print("系统管理员账号列表")
print("=" * 80)

users = User.objects.all().order_by('-date_joined')

if not users.exists():
    print("\n暂无管理员账号")
else:
    print(f"\n共有 {users.count()} 个管理员账号:\n")
    
    for i, user in enumerate(users, 1):
        # 统计该用户的抽奖数量
        lottery_count = Lottery.objects.filter(admin_user=user).count()
        
        print(f"{i}. 用户名: {user.username}")
        print(f"   姓名: {user.first_name or '（未设置）'}")
        print(f"   邮箱: {user.email or '（未设置）'}")
        print(f"   抽奖数: {lottery_count} 个")
        print(f"   创建时间: {user.date_joined.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   最后登录: {user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else '从未登录'}")
        print("-" * 80)

print("\n💡 提示：")
print("  - 创建新用户：python create_user.py")
print("  - 修改密码：python change_password.py")

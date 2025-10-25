"""
测试 Bot 与后端 API 的连接
"""
import requests
from config import API_URL

def test_api_connection():
    """测试 API 连接"""
    print("=" * 50)
    print("测试 Telegram Bot 与后端 API 连接")
    print("=" * 50)
    
    # 测试 1: 获取统计数据
    print("\n1. 测试获取统计数据...")
    try:
        response = requests.get(f'{API_URL}/lotteries/statistics/')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 成功！统计数据：{data}")
        else:
            print(f"❌ 失败！状态码：{response.status_code}")
    except Exception as e:
        print(f"❌ 错误：{e}")
    
    # 测试 2: 获取进行中的抽奖
    print("\n2. 测试获取进行中的抽奖...")
    try:
        response = requests.get(f'{API_URL}/lotteries/active/')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 成功！进行中的抽奖数量：{len(data)}")
            for lottery in data:
                print(f"   - {lottery['title']} (ID: {lottery['id']})")
        else:
            print(f"❌ 失败！状态码：{response.status_code}")
    except Exception as e:
        print(f"❌ 错误：{e}")
    
    # 测试 3: 注册测试用户
    print("\n3. 测试注册用户...")
    try:
        test_user = {
            'telegram_id': 123456789,
            'username': 'test_user',
            'first_name': '测试用户',
            'last_name': 'Test'
        }
        response = requests.post(f'{API_URL}/users/get_or_create/', json=test_user)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 成功！用户信息：{data}")
        else:
            print(f"❌ 失败！状态码：{response.status_code}")
    except Exception as e:
        print(f"❌ 错误：{e}")
    
    print("\n" + "=" * 50)
    print("测试完成！")
    print("=" * 50)

if __name__ == '__main__':
    test_api_connection()

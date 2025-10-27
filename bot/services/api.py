"""
API 服务封装模块
统一管理所有后端 API 调用
"""
import logging
import requests
from typing import Dict, List, Optional, Any
from config import API_URL

logger = logging.getLogger(__name__)


class APIService:
    """API 服务类，封装所有后端接口调用"""
    
    def __init__(self):
        self.api_url = API_URL
    
    # ==================== 用户相关 ====================
    
    def register_user(self, user_data: Dict[str, Any]) -> Optional[Dict]:
        """
        注册或更新用户
        
        Args:
            user_data: 用户信息字典
                {
                    'telegram_id': int,
                    'username': str,
                    'first_name': str,
                    'last_name': str
                }
        
        Returns:
            用户信息或 None
        """
        try:
            response = requests.post(
                f'{self.api_url}/users/get_or_create/',
                json=user_data
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"注册用户失败: {e}")
            return None
    
    # ==================== 抽奖相关 ====================
    
    def get_active_lotteries(self) -> List[Dict]:
        """
        获取进行中的抽奖列表
        
        Returns:
            抽奖列表
        """
        try:
            response = requests.get(f'{self.api_url}/lotteries/active/')
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"获取抽奖列表失败: {e}")
            return []
    
    def participate_lottery(self, lottery_id: int, telegram_id: int) -> Dict[str, Any]:
        """
        参与抽奖
        
        Args:
            lottery_id: 抽奖活动 ID
            telegram_id: 用户 Telegram ID
        
        Returns:
            {'success': bool, 'data': dict, 'error': str}
        """
        try:
            response = requests.post(
                f'{self.api_url}/lotteries/{lottery_id}/participate/',
                json={'telegram_id': telegram_id}
            )
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'data': response.json(),
                    'error': None
                }
            else:
                return {
                    'success': False,
                    'data': None,
                    'error': response.json().get('error', '未知错误')
                }
        except Exception as e:
            logger.error(f"参与抽奖失败: {e}")
            return {
                'success': False,
                'data': None,
                'error': str(e)
            }
    
    def draw_lottery(self, lottery_id: int) -> Dict[str, Any]:
        """
        执行开奖
        
        Args:
            lottery_id: 抽奖活动 ID
        
        Returns:
            {'success': bool, 'data': dict, 'error': str}
        """
        try:
            response = requests.post(f'{self.api_url}/lotteries/{lottery_id}/draw/')
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'data': response.json(),
                    'error': None
                }
            else:
                return {
                    'success': False,
                    'data': None,
                    'error': response.json().get('error', '未知错误')
                }
        except Exception as e:
            logger.error(f"开奖失败: {e}")
            return {
                'success': False,
                'data': None,
                'error': str(e)
            }
    
    # ==================== 参与记录相关 ====================
    
    def get_my_participations(self, telegram_id: int) -> List[Dict]:
        """
        获取用户参与的抽奖列表
        
        Args:
            telegram_id: 用户 Telegram ID
        
        Returns:
            参与记录列表
        """
        try:
            response = requests.get(
                f'{self.api_url}/participations/my_participations/',
                params={'telegram_id': telegram_id}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"获取参与记录失败: {e}")
            return []
    
    def get_my_wins(self, telegram_id: int) -> List[Dict]:
        """
        获取用户中奖记录
        
        Args:
            telegram_id: 用户 Telegram ID
        
        Returns:
            中奖记录列表
        """
        try:
            response = requests.get(
                f'{self.api_url}/winners/my_wins/',
                params={'telegram_id': telegram_id}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"获取中奖记录失败: {e}")
            return []

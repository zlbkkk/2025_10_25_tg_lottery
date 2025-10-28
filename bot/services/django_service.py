"""
Django 数据服务模块
Bot直接访问Django模型进行数据查询（多租户隔离版本）
"""
import os
import sys
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime

# 添加Django路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lottery_backend.settings')

import django
django.setup()

from lottery.models import TelegramUser, Lottery, Prize, Participation, Winner
from django.utils import timezone

logger = logging.getLogger(__name__)


class DjangoService:
    """
    Django数据服务类
    每个租户一个实例，自动根据admin_user_id过滤数据
    """
    
    def __init__(self, admin_user_id: int):
        """
        初始化服务
        
        Args:
            admin_user_id: 租户的管理员用户ID
        """
        self.admin_user_id = admin_user_id
        logger.info(f"初始化 DjangoService for admin_user_id={admin_user_id}")
    
    # ==================== 用户相关 ====================
    
    def register_user(self, user_data: Dict[str, Any]) -> Optional[Dict]:
        """
        注册或更新Telegram用户
        
        Args:
            user_data: 用户信息字典
        
        Returns:
            用户信息字典
        """
        try:
            user, created = TelegramUser.objects.get_or_create(
                telegram_id=user_data['telegram_id'],
                defaults={
                    'username': user_data.get('username'),
                    'first_name': user_data.get('first_name'),
                    'last_name': user_data.get('last_name'),
                }
            )
            
            # 如果用户已存在，更新信息
            if not created:
                user.username = user_data.get('username')
                user.first_name = user_data.get('first_name')
                user.last_name = user_data.get('last_name')
                user.save()
            
            return {
                'id': user.id,
                'telegram_id': user.telegram_id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
        except Exception as e:
            logger.error(f"注册用户失败: {e}")
            return None
    
    # ==================== 抽奖相关 ====================
    
    def get_active_lotteries(self) -> List[Dict]:
        """
        获取当前租户的进行中的抽奖列表
        
        Returns:
            抽奖列表
        """
        try:
            # 只查询当前租户的抽奖
            lotteries = Lottery.objects.filter(
                admin_user_id=self.admin_user_id,
                status='active'
            ).prefetch_related('prizes').order_by('-created_at')
            
            result = []
            for lottery in lotteries:
                # 序列化奖品信息
                prizes_data = []
                for prize in lottery.prizes.all():
                    prizes_data.append({
                        'id': prize.id,
                        'name': prize.name,
                        'description': prize.description,
                        'winner_count': prize.winner_count,
                        'level': prize.level,
                    })
                
                result.append({
                    'id': lottery.id,
                    'title': lottery.title,
                    'description': lottery.description,
                    'prize_name': lottery.prize_name,  # 向后兼容
                    'prize_count': lottery.prize_count,  # 向后兼容
                    'prizes': prizes_data,  # 新格式
                    'participant_count': lottery.participations.count(),
                    'max_participants': lottery.max_participants,
                    'start_time': lottery.start_time.isoformat(),
                    'end_time': lottery.end_time.isoformat(),
                    'status': lottery.status,
                })
            
            return result
        except Exception as e:
            logger.error(f"获取抽奖列表失败: {e}")
            return []
    
    def participate_lottery(self, lottery_id: int, telegram_id: int) -> Dict[str, Any]:
        """
        参与抽奖
        
        Args:
            lottery_id: 抽奖活动ID
            telegram_id: 用户Telegram ID
        
        Returns:
            {'success': bool, 'data': dict, 'error': str}
        """
        try:
            # 验证抽奖是否存在且属于当前租户
            lottery = Lottery.objects.get(
                id=lottery_id,
                admin_user_id=self.admin_user_id
            )
            
            # 获取用户
            user = TelegramUser.objects.get(telegram_id=telegram_id)
            
            # 检查抽奖状态
            if lottery.status != 'active':
                return {
                    'success': False,
                    'data': None,
                    'error': '抽奖活动未开始或已结束'
                }
            
            # 检查是否已参与
            if Participation.objects.filter(lottery=lottery, user=user).exists():
                return {
                    'success': False,
                    'data': None,
                    'error': '您已经参与过这个抽奖了'
                }
            
            # 检查人数限制
            if lottery.max_participants > 0:
                current_count = lottery.participations.count()
                if current_count >= lottery.max_participants:
                    return {
                        'success': False,
                        'data': None,
                        'error': '抽奖人数已满'
                    }
            
            # 创建参与记录
            participation = Participation.objects.create(
                lottery=lottery,
                user=user
            )
            
            return {
                'success': True,
                'data': {
                    'participation_id': participation.id,
                    'lottery_title': lottery.title,
                },
                'error': None
            }
        except Lottery.DoesNotExist:
            return {
                'success': False,
                'data': None,
                'error': '抽奖活动不存在'
            }
        except TelegramUser.DoesNotExist:
            return {
                'success': False,
                'data': None,
                'error': '用户不存在，请先发送 /start'
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
        执行开奖（仅管理后台调用，Bot端不应该调用此方法）
        
        Args:
            lottery_id: 抽奖活动ID
        
        Returns:
            {'success': bool, 'data': dict, 'error': str}
        """
        try:
            # 验证抽奖是否存在且属于当前租户
            lottery = Lottery.objects.get(
                id=lottery_id,
                admin_user_id=self.admin_user_id
            )
            
            # 调用模型的开奖方法
            success = lottery.draw_winners()
            
            if success:
                # 获取中奖记录
                winners = Winner.objects.filter(lottery=lottery).select_related('user', 'prize')
                
                winners_data = []
                for winner in winners:
                    winners_data.append({
                        'user': {
                            'telegram_id': winner.user.telegram_id,
                            'first_name': winner.user.first_name,
                            'username': winner.user.username,
                        },
                        'prize_name': winner.prize.name if winner.prize else winner.prize_name,
                    })
                
                return {
                    'success': True,
                    'data': {
                        'lottery_title': lottery.title,
                        'winners': winners_data,
                    },
                    'error': None
                }
            else:
                return {
                    'success': False,
                    'data': None,
                    'error': '开奖失败'
                }
        except Lottery.DoesNotExist:
            return {
                'success': False,
                'data': None,
                'error': '抽奖活动不存在'
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
        获取用户在当前租户的参与记录
        
        Args:
            telegram_id: 用户Telegram ID
        
        Returns:
            参与记录列表
        """
        try:
            user = TelegramUser.objects.get(telegram_id=telegram_id)
            
            # 只查询当前租户的抽奖
            participations = Participation.objects.filter(
                user=user,
                lottery__admin_user_id=self.admin_user_id
            ).select_related('lottery').order_by('-participated_at')
            
            result = []
            for p in participations:
                result.append({
                    'id': p.id,
                    'lottery_id': p.lottery.id,
                    'lottery_title': p.lottery.title,
                    'lottery_status': p.lottery.status,
                    'participated_at': p.participated_at.isoformat(),
                })
            
            return result
        except TelegramUser.DoesNotExist:
            return []
        except Exception as e:
            logger.error(f"获取参与记录失败: {e}")
            return []
    
    def get_my_wins(self, telegram_id: int) -> List[Dict]:
        """
        获取用户在当前租户的中奖记录
        
        Args:
            telegram_id: 用户Telegram ID
        
        Returns:
            中奖记录列表
        """
        try:
            user = TelegramUser.objects.get(telegram_id=telegram_id)
            
            # 只查询当前租户的中奖记录
            winners = Winner.objects.filter(
                user=user,
                lottery__admin_user_id=self.admin_user_id
            ).select_related('lottery', 'prize').order_by('-won_at')
            
            result = []
            for w in winners:
                result.append({
                    'id': w.id,
                    'lottery_id': w.lottery.id,
                    'lottery_title': w.lottery.title,
                    'prize_name': w.prize.name if w.prize else w.prize_name,
                    'won_at': w.won_at.isoformat(),
                    'claimed': w.claimed,
                })
            
            return result
        except TelegramUser.DoesNotExist:
            return []
        except Exception as e:
            logger.error(f"获取中奖记录失败: {e}")
            return []


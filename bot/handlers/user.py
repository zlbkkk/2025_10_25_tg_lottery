"""
用户处理模块
处理用户相关的业务逻辑
"""
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)


class UserHandler:
    """用户处理器"""
    
    def __init__(self, admin_user_id: int = None):
        self.admin_user_id = admin_user_id
        
        # 延迟导入DjangoService（避免在单机器人模式下报错）
        if admin_user_id:
            from services.django_service import DjangoService
            self.service = DjangoService(admin_user_id)
        else:
            # 向后兼容：单机器人模式
            from services.api import APIService
            self.service = APIService()
    
    def _get_level_emoji(self, level):
        """根据等级返回对应的emoji"""
        level_map = {
            1: '🥇',
            2: '🥈',
            3: '🥉',
        }
        return level_map.get(level, f'{level}️⃣')
    
    async def show_my_lotteries(self, query):
        """显示我的抽奖记录"""
        user = query.from_user
        
        try:
            # 获取我参与的抽奖（包含抽奖详情）
            participations = self.service.get_my_participations(user.id)
            
            # 获取我中奖的记录
            wins = self.service.get_my_wins(user.id)
            
            # 筛选出未开奖的抽奖（状态为 active）
            # 注意：DjangoService返回的格式不包含嵌套的lottery对象
            pending_count = sum(1 for p in participations if p.get('lottery_status') == 'active')
            
            # 构建消息 - 顶部统计卡片
            text = "━━━━━━━━━━━━━━━━━━━\n"
            text += "📊 我的抽奖统计\n"
            text += "━━━━━━━━━━━━━━━━━━━\n"
            text += f"🎟️ 参与总数：{len(participations)} 个\n"
            text += f"⏳ 等待开奖：{pending_count} 个\n"
            text += f"🏆 中奖次数：{len(wins)} 次\n"
            text += "━━━━━━━━━━━━━━━━━━━\n\n"
            
            # 显示最近参与的抽奖
            if participations:
                text += "📋 最近参与的抽奖\n\n"
                for p in participations[:5]:  # 只显示最近5个
                    status_emoji = "⏳" if p['lottery_status'] == 'active' else "✅"
                    text += f"{status_emoji} {p['lottery_title']}\n"
                if len(participations) > 5:
                    text += f"\n... 还有 {len(participations) - 5} 个\n"
                text += "\n"
            
            # 显示中奖记录
            if wins:
                text += "🎉 中奖记录\n"
                text += "━━━━━━━━━━━━━━━━━━━\n"
                for win in wins[:10]:  # 只显示最近10个
                    text += f"🏆 {win['lottery_title']}\n"
                    text += f"   奖品：{win['prize_name']}\n"
                if len(wins) > 10:
                    text += f"\n... 还有 {len(wins) - 10} 个\n"
                text += "━━━━━━━━━━━━━━━━━━━\n"
            
            keyboard = [[InlineKeyboardButton("🏠 返回主菜单", callback_data='main_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(text, reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"获取我的抽奖失败: {e}")
            keyboard = [[InlineKeyboardButton("🏠 返回主菜单", callback_data='main_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "❌ 获取失败，请稍后重试",
                reply_markup=reply_markup
            )

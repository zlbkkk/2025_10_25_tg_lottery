"""
用户处理模块
处理用户相关的业务逻辑
"""
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from services.api import APIService

logger = logging.getLogger(__name__)


class UserHandler:
    """用户处理器"""
    
    def __init__(self):
        self.api = APIService()
    
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
            participations = self.api.get_my_participations(user.id)
            
            # 获取我中奖的记录
            wins = self.api.get_my_wins(user.id)
            
            # 筛选出未开奖的抽奖（状态为 active）
            pending_lotteries = []
            for p in participations:
                lottery = p.get('lottery')
                if lottery and lottery.get('status') == 'active':
                    pending_lotteries.append(lottery)
            
            # 构建消息 - 顶部统计卡片
            text = "━━━━━━━━━━━━━━━━━━━\n"
            text += "📊 我的抽奖统计\n"
            text += "━━━━━━━━━━━━━━━━━━━\n"
            text += f"🎟️ 参与总数：{len(participations)} 个\n"
            text += f"⏳ 等待开奖：{len(pending_lotteries)} 个\n"
            text += f"🏆 中奖次数：{len(wins)} 次\n"
            text += "━━━━━━━━━━━━━━━━━━━\n\n"
            
            # 显示未开奖的抽奖列表 - 重点突出（支持多奖品）
            if pending_lotteries:
                text += "⏳ 正在参与的抽奖活动\n\n"
                for i, lottery in enumerate(pending_lotteries, 1):
                    text += f"┌─────────────────\n"
                    text += f"│ 🎁 【{lottery['title']}】\n"
                    text += f"├─────────────────\n"
                    
                    # 显示奖品（支持多奖品）
                    prizes = lottery.get('prizes', [])
                    if prizes:
                        # 多奖品格式
                        text += f"│ 🏆 奖品：\n"
                        for prize in prizes:
                            level_emoji = self._get_level_emoji(prize.get('level', 1))
                            text += f"│   {level_emoji} {prize['name']} x{prize['winner_count']}\n"
                    else:
                        # 向后兼容：单奖品
                        text += f"│ 🎯 奖品：{lottery['prize_name']}\n"
                        text += f"│ 🔢 数量：x{lottery['prize_count']}\n"
                    
                    text += f"│ 👥 参与："
                    if lottery['max_participants'] > 0:
                        text += f"{lottery['participant_count']}/{lottery['max_participants']} 人"
                    else:
                        text += f"{lottery['participant_count']} 人（不限）"
                    text += f"\n└─────────────────\n"
                    if i < len(pending_lotteries):  # 不是最后一个
                        text += "\n"
            
            # 显示中奖记录 - 突出显示（支持显示奖品等级）
            if wins:
                text += "\n🎉 中奖记录\n"
                text += "━━━━━━━━━━━━━━━━━━━\n"
                for win in wins:
                    # 优先使用 prize_display_name，否则使用 prize_name
                    prize_display = win.get('prize_display_name', win.get('prize_name', '未知奖品'))
                    text += f"✨ {prize_display}\n"
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

"""
抽奖处理模块
处理抽奖相关的所有业务逻辑，包括分页显示
"""
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.pagination import paginate, create_pagination_keyboard

logger = logging.getLogger(__name__)


class LotteryHandler:
    """抽奖处理器"""
    
    def __init__(self, admin_user_id: int = None):
        self.admin_user_id = admin_user_id
        self.page_size = 5  # 每页显示5个抽奖活动
        
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
    
    async def show_active_lotteries(self, query, page: int = 1):
        """
        显示进行中的抽奖（带分页）
        
        Args:
            query: CallbackQuery 对象
            page: 页码（从1开始）
        """
        try:
            # 获取所有进行中的抽奖
            lotteries = self.service.get_active_lotteries()
            
            if not lotteries:
                keyboard = [[InlineKeyboardButton("🏠 返回主菜单", callback_data='main_menu')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(
                    "😢 暂时没有进行中的抽奖活动",
                    reply_markup=reply_markup
                )
                return
            
            # 分页处理
            page_data = paginate(lotteries, page, self.page_size)
            current_lotteries = page_data['items']
            
            # 构建消息文本 - 优化显示样式（支持多奖品）
            text = "━━━━━━━━━━━━━━━━━━━\n"
            text += f"🎟️ 进行中的抽奖活动\n"
            text += "━━━━━━━━━━━━━━━━━━━\n\n"
            keyboard = []
            
            for i, lottery in enumerate(current_lotteries, 1):
                text += f"┏━━━ 第 {i} 个抽奖 ━━━┓\n"
                text += f"┃ 🎁 {lottery['title']}\n"
                text += f"┣━━━━━━━━━━━━━━━\n"
                
                # 显示奖品信息（支持多奖品）
                prizes = lottery.get('prizes', [])
                if prizes:
                    # 新格式：多奖品
                    text += f"┃ 🏆 奖品设置：\n"
                    for prize in prizes:
                        level_emoji = self._get_level_emoji(prize.get('level', 1))
                        text += f"┃   {level_emoji} {prize['name']} x{prize['winner_count']}\n"
                else:
                    # 向后兼容：旧格式单奖品
                    text += f"┃ 🎯 奖品：{lottery['prize_name']}\n"
                    text += f"┃ 🔢 数量：x{lottery['prize_count']}\n"
                
                text += f"┃ 👥 参与："
                if lottery['max_participants'] > 0:
                    text += f"{lottery['participant_count']}/{lottery['max_participants']} 人"
                else:
                    text += f"{lottery['participant_count']} 人（不限）"
                text += f"\n┗━━━━━━━━━━━━━━━┛\n\n"
                
                # 为每个抽奖添加参与按钮
                keyboard.append([
                    InlineKeyboardButton(
                        f"🎯 参与「{lottery['title']}」", 
                        callback_data=f"participate_{lottery['id']}"
                    )
                ])
            
            # 添加分页信息到文本
            if page_data['total_pages'] > 1:
                text += f"\n📄 第 {page_data['page']}/{page_data['total_pages']} 页"
            
            # 创建分页导航按钮
            nav_keyboard = create_pagination_keyboard(
                page=page_data['page'],
                total_pages=page_data['total_pages'],
                callback_prefix='lottery_page_'
            )
            
            # 合并按钮
            keyboard.extend(nav_keyboard)
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"获取抽奖列表失败: {e}")
            keyboard = [[InlineKeyboardButton("🏠 返回主菜单", callback_data='main_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "❌ 获取抽奖列表失败，请稍后重试",
                reply_markup=reply_markup
            )
    
    async def participate_lottery(self, query, lottery_id: int):
        """
        参与抽奖
        
        Args:
            query: CallbackQuery 对象
            lottery_id: 抽奖活动 ID
        """
        user = query.from_user
        
        try:
            result = self.service.participate_lottery(lottery_id, user.id)
            
            if result['success']:
                keyboard = [
                    [InlineKeyboardButton("🎟️ 继续参与其他抽奖", callback_data='join_lottery')],
                    [InlineKeyboardButton("🏠 返回主菜单", callback_data='main_menu')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    f"🎉 参与成功！\n\n"
                    f"您已成功参与抽奖活动\n"
                    f"开奖后会第一时间通知您！",
                    reply_markup=reply_markup
                )
            else:
                keyboard = [
                    [InlineKeyboardButton("🎟️ 返回抽奖列表", callback_data='join_lottery')],
                    [InlineKeyboardButton("🏠 返回主菜单", callback_data='main_menu')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    f"❌ 参与失败：{result['error']}",
                    reply_markup=reply_markup
                )
                
        except Exception as e:
            logger.error(f"参与抽奖异常: {e}")
            keyboard = [[InlineKeyboardButton("🏠 返回主菜单", callback_data='main_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "❌ 参与失败，请稍后重试",
                reply_markup=reply_markup
            )
    
    async def draw_lottery(self, query, lottery_id: int, context: ContextTypes.DEFAULT_TYPE):
        """
        执行开奖（管理员功能）
        
        Args:
            query: CallbackQuery 对象
            lottery_id: 抽奖活动 ID
            context: 上下文对象
        """
        try:
            result = self.service.draw_lottery(lottery_id)
            
            if result['success']:
                data = result['data']
                winners = data['winners']
                
                text = "🎊 开奖结果\n\n"
                text += "🏆 中奖者：\n"
                for winner in winners:
                    user = winner['user']
                    text += f"• {user['first_name']} (@{user['username']})\n"
                
                await query.edit_message_text(text)
                
                # 通知中奖者
                for winner in winners:
                    user_id = winner['user']['telegram_id']
                    try:
                        await context.bot.send_message(
                            chat_id=user_id,
                            text=f"🎉 恭喜您中奖啦！\n\n"
                                 f"奖品：{winner['prize_name']}\n"
                                 f"请联系管理员领取奖品"
                        )
                    except Exception as e:
                        logger.error(f"通知中奖者 {user_id} 失败: {e}")
            else:
                await query.edit_message_text(f"❌ 开奖失败：{result['error']}")
                
        except Exception as e:
            logger.error(f"开奖异常: {e}")
            await query.edit_message_text("❌ 开奖失败，请稍后重试")

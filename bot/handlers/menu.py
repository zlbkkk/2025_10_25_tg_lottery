"""
菜单处理模块
处理主菜单和帮助信息
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


class MenuHandler:
    """菜单处理器"""
    
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
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /start 命令"""
        user = update.effective_user
        
        # 注册或更新用户信息
        self.service.register_user({
            'telegram_id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name
        })
        
        keyboard = [
            [InlineKeyboardButton("🎟️ 参与抽奖", callback_data='join_lottery')],
            [InlineKeyboardButton("📊 我的抽奖", callback_data='my_lotteries')],
            [InlineKeyboardButton("❓ 帮助", callback_data='help')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = f"""
🎉 欢迎使用抽奖机器人！

你好 {user.first_name}！

请选择功能：
🎟️ 参与抽奖 - 查看并参与抽奖活动
📊 我的抽奖 - 查看我的参与记录和中奖情况
❓ 帮助 - 使用说明

💡 提示：抽奖活动由管理员创建
        """
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    
    async def show_main_menu(self, query):
        """显示主菜单"""
        user = query.from_user
        
        keyboard = [
            [InlineKeyboardButton("🎟️ 参与抽奖", callback_data='join_lottery')],
            [InlineKeyboardButton("📊 我的抽奖", callback_data='my_lotteries')],
            [InlineKeyboardButton("❓ 帮助", callback_data='help')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = f"""
🎉 欢迎使用抽奖机器人！

你好 {user.first_name}！

请选择功能：
🎟️ 参与抽奖 - 查看并参与抽奖活动
📊 我的抽奖 - 查看我的参与记录和中奖情况
❓ 帮助 - 使用说明

💡 提示：抽奖活动由管理员创建
        """
        
        try:
            await query.edit_message_text(welcome_text, reply_markup=reply_markup)
        except Exception as e:
            logger.info(f"无法编辑消息，删除并发送新消息: {e}")
            await query.message.delete()
            await query.message.reply_text(welcome_text, reply_markup=reply_markup)
    
    async def show_help(self, query):
        """显示帮助信息"""
        text = """
❓ 使用帮助

🎁 创建抽奖：
访问管理后台创建抽奖活动

🎟️ 参与抽奖：
1. 点击"参与抽奖"
2. 选择想要参与的活动
3. 点击"参与"按钮
4. 等待开奖通知

📊 我的抽奖：
查看参与记录和中奖情况

💡 提示：
• 每个抽奖只能参与一次
• 开奖后会自动通知中奖者
• 请注意抽奖的开始和结束时间

如有问题，请联系管理员
        """
        
        keyboard = [[InlineKeyboardButton("🏠 返回主菜单", callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup)

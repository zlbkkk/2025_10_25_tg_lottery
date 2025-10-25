"""
Telegram 抽奖机器人主程序
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)
import requests
from config import BOT_TOKEN, API_URL

# 配置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class LotteryBot:
    """抽奖机器人类"""
    
    def __init__(self):
        self.api_url = API_URL
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /start 命令"""
        user = update.effective_user
        
        # 注册或更新用户信息
        self.register_user(user)
        
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
    
    def register_user(self, user):
        """注册或更新用户"""
        try:
            response = requests.post(
                f'{self.api_url}/users/get_or_create/',
                json={
                    'telegram_id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            )
            return response.json()
        except Exception as e:
            logger.error(f"注册用户失败: {e}")
            return None
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理按钮回调"""
        query = update.callback_query
        await query.answer()
        
        if query.data == 'join_lottery':
            await self.show_active_lotteries(query)
        elif query.data == 'my_lotteries':
            await self.show_my_lotteries(query)
        elif query.data == 'help':
            await self.show_help(query)
        elif query.data.startswith('participate_'):
            lottery_id = query.data.split('_')[1]
            await self.participate_lottery(query, lottery_id)
        elif query.data.startswith('draw_'):
            lottery_id = query.data.split('_')[1]
            await self.draw_lottery(query, lottery_id)
    
    async def show_active_lotteries(self, query):
        """显示进行中的抽奖"""
        try:
            response = requests.get(f'{self.api_url}/lotteries/active/')
            lotteries = response.json()
            
            if not lotteries:
                await query.edit_message_text("😢 暂时没有进行中的抽奖活动")
                return
            
            text = "🎟️ 进行中的抽奖活动：\n\n"
            keyboard = []
            
            for lottery in lotteries:
                text += f"🎁 {lottery['title']}\n"
                text += f"   奖品：{lottery['prize_name']} x{lottery['prize_count']}\n"
                text += f"   参与人数：{lottery['participant_count']}"
                if lottery['max_participants'] > 0:
                    text += f"/{lottery['max_participants']}"
                text += "\n\n"
                
                keyboard.append([
                    InlineKeyboardButton(
                        f"🎯 参与 {lottery['title']}", 
                        callback_data=f"participate_{lottery['id']}"
                    )
                ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"获取抽奖列表失败: {e}")
            await query.edit_message_text("❌ 获取抽奖列表失败，请稍后重试")
    
    async def participate_lottery(self, query, lottery_id):
        """参与抽奖"""
        user = query.from_user
        
        try:
            response = requests.post(
                f'{self.api_url}/lotteries/{lottery_id}/participate/',
                json={'telegram_id': user.id}
            )
            
            if response.status_code == 200:
                data = response.json()
                await query.edit_message_text(
                    f"🎉 参与成功！\n\n"
                    f"您已成功参与抽奖活动\n"
                    f"开奖后会第一时间通知您！"
                )
            else:
                error = response.json().get('error', '未知错误')
                await query.edit_message_text(f"❌ 参与失败：{error}")
                
        except Exception as e:
            logger.error(f"参与抽奖失败: {e}")
            await query.edit_message_text("❌ 参与失败，请稍后重试")
    
    async def show_my_lotteries(self, query):
        """显示我的抽奖"""
        user = query.from_user
        
        try:
            # 获取我参与的抽奖
            response = requests.get(
                f'{self.api_url}/participations/my_participations/',
                params={'telegram_id': user.id}
            )
            participations = response.json()
            
            # 获取我中奖的记录
            response = requests.get(
                f'{self.api_url}/winners/my_wins/',
                params={'telegram_id': user.id}
            )
            wins = response.json()
            
            text = "📊 我的抽奖记录\n\n"
            text += f"🎟️ 参与的抽奖：{len(participations)} 个\n"
            text += f"🏆 中奖次数：{len(wins)} 次\n\n"
            
            if wins:
                text += "🎉 中奖记录：\n"
                for win in wins:
                    text += f"• {win['prize_name']}\n"
            
            await query.edit_message_text(text)
            
        except Exception as e:
            logger.error(f"获取我的抽奖失败: {e}")
            await query.edit_message_text("❌ 获取失败，请稍后重试")
    
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
        await query.edit_message_text(text)
    
    async def draw_lottery(self, query, lottery_id):
        """执行开奖（管理员功能）"""
        try:
            response = requests.post(f'{self.api_url}/lotteries/{lottery_id}/draw/')
            
            if response.status_code == 200:
                data = response.json()
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
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=f"🎉 恭喜您中奖啦！\n\n"
                             f"奖品：{winner['prize_name']}\n"
                             f"请联系管理员领取奖品"
                    )
            else:
                error = response.json().get('error', '未知错误')
                await query.edit_message_text(f"❌ 开奖失败：{error}")
                
        except Exception as e:
            logger.error(f"开奖失败: {e}")
            await query.edit_message_text("❌ 开奖失败，请稍后重试")
    
    def run(self):
        """运行机器人"""
        # 创建应用
        application = Application.builder().token(BOT_TOKEN).build()
        
        # 添加处理器
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # 启动机器人
        logger.info("机器人启动中...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    bot = LotteryBot()
    bot.run()

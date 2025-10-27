"""
Telegram 抽奖机器人主程序
职责：路由注册和应用启动
"""
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from config import BOT_TOKEN
from handlers import MenuHandler, LotteryHandler, UserHandler

# 配置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class LotteryBot:
    """抽奖机器人主类 - 负责路由和启动"""
    
    def __init__(self):
        self.menu_handler = MenuHandler()
        self.lottery_handler = LotteryHandler()
        self.user_handler = UserHandler()
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        统一的按钮回调路由
        根据 callback_data 分发到不同的处理器
        """
        query = update.callback_query
        await query.answer()
        
        callback_data = query.data
        
        # ==================== 菜单相关 ====================
        if callback_data == 'main_menu':
            await self.menu_handler.show_main_menu(query)
        
        elif callback_data == 'help':
            await self.menu_handler.show_help(query)
        
        # ==================== 抽奖相关 ====================
        elif callback_data == 'join_lottery':
            await self.lottery_handler.show_active_lotteries(query, page=1)
        
        elif callback_data.startswith('lottery_page_'):
            # 处理分页：lottery_page_2
            page = int(callback_data.split('_')[-1])
            await self.lottery_handler.show_active_lotteries(query, page=page)
        
        elif callback_data.startswith('participate_'):
            # 参与抽奖：participate_123
            lottery_id = int(callback_data.split('_')[1])
            await self.lottery_handler.participate_lottery(query, lottery_id)
        
        elif callback_data.startswith('draw_'):
            # 开奖：draw_123
            lottery_id = int(callback_data.split('_')[1])
            await self.lottery_handler.draw_lottery(query, lottery_id, context)
        
        # ==================== 用户相关 ====================
        elif callback_data == 'my_lotteries':
            await self.user_handler.show_my_lotteries(query)
        
        # ==================== 其他 ====================
        elif callback_data == 'page_info':
            # 页码指示器，不做任何操作
            pass
        
        else:
            logger.warning(f"未处理的回调数据: {callback_data}")
    
    def run(self):
        """启动机器人"""
        # 创建应用
        application = Application.builder().token(BOT_TOKEN).build()
        
        # 注册命令处理器
        application.add_handler(CommandHandler("start", self.menu_handler.start))
        
        # 注册回调处理器
        application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # 启动机器人
        logger.info("🤖 抽奖机器人启动中...")
        logger.info("📦 模块加载：菜单、抽奖、用户")
        logger.info("✅ 分页功能已启用（每页5个活动）")
        application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    bot = LotteryBot()
    bot.run()

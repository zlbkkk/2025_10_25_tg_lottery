"""
多租户多机器人启动脚本（Polling模式）
每个租户配置自己的Bot Token，系统为每个激活的配置启动独立的Bot进程
"""
import os
import sys
import logging
import asyncio
import multiprocessing
from typing import List, Dict

# 添加Django环境
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lottery_backend.settings')

import django
django.setup()

from django.contrib.auth.models import User
from lottery.models import BotConfig
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# 导入处理器
from handlers import MenuHandler, LotteryHandler, UserHandler

# 配置日志
logging.basicConfig(
    format='%(asctime)s - [%(process)d] %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class TenantLotteryBot:
    """
    单个租户的抽奖机器人
    每个租户一个独立的Bot实例
    """
    
    def __init__(self, admin_user_id: int, bot_token: str, bot_username: str = None):
        self.admin_user_id = admin_user_id
        self.bot_token = bot_token
        self.bot_username = bot_username or f"User_{admin_user_id}"
        
        # 初始化处理器（传入租户ID用于数据隔离）
        self.menu_handler = MenuHandler(admin_user_id=admin_user_id)
        self.lottery_handler = LotteryHandler(admin_user_id=admin_user_id)
        self.user_handler = UserHandler(admin_user_id=admin_user_id)
        
        logger.info(f"🤖 初始化租户Bot: {self.bot_username} (User ID: {admin_user_id})")
    
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
            logger.warning(f"[{self.bot_username}] 未处理的回调数据: {callback_data}")
    
    def run_sync(self):
        """同步启动机器人（适配 Windows multiprocessing）"""
        try:
            # 创建应用
            application = Application.builder().token(self.bot_token).build()
            
            # 注册命令处理器
            application.add_handler(CommandHandler("start", self.menu_handler.start))
            
            # 注册回调处理器
            application.add_handler(CallbackQueryHandler(self.button_callback))
            
            # 启动机器人
            logger.info(f"✅ [{self.bot_username}] Bot启动成功！")
            
            # 使用同步方式运行（自动管理事件循环）
            application.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True
            )
        except Exception as e:
            # 判断错误类型
            error_message = str(e)
            
            if 'InvalidToken' in str(type(e)) or 'rejected by the server' in error_message or 'Unauthorized' in error_message:
                # Token 无效错误 - 不应该重启
                logger.error(f"❌ [{self.bot_username}] Token 无效！请检查配置")
                logger.error(f"   错误详情: {error_message}")
                logger.error(f"   🔧 请前往后台管理页面更新正确的 Bot Token")
                
                # 标记为永久失败（通过退出码区分）
                import sys
                sys.exit(2)  # 退出码 2 表示 Token 无效
            else:
                # 其他错误 - 可能是临时问题
                logger.error(f"❌ [{self.bot_username}] Bot运行异常: {e}")
                import traceback
                traceback.print_exc()
                
                import sys
                sys.exit(1)  # 退出码 1 表示一般错误


def run_bot_instance(admin_user_id: int, bot_token: str, bot_username: str = None):
    """
    在独立进程中运行单个Bot实例
    每个租户一个进程
    """
    # 重新初始化Django（在子进程中）
    import django
    django.setup()
    
    # Windows 多进程需要设置事件循环策略
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    bot = TenantLotteryBot(admin_user_id, bot_token, bot_username)
    
    # 使用同步方式运行
    bot.run_sync()


def get_active_bot_configs() -> List[Dict]:
    """
    从数据库获取所有激活的Bot配置
    """
    configs = []
    
    # 查询所有激活且配置了token的租户
    active_configs = BotConfig.objects.filter(
        is_active=True,
        bot_token__isnull=False
    ).exclude(bot_token='').select_related('admin_user')
    
    for config in active_configs:
        configs.append({
            'admin_user_id': config.admin_user_id,
            'bot_token': config.bot_token,
            'bot_username': config.bot_username or config.admin_user.username,
        })
    
    return configs


def main():
    """
    主函数：启动所有租户的Bot（支持热重载）
    """
    import time
    
    logger.info("=" * 60)
    logger.info("🚀 多租户抽奖Bot系统启动中（热重载模式）...")
    logger.info("=" * 60)
    logger.info("💡 提示：系统会自动监控配置变化")
    logger.info("   - 新增配置 → 自动启动Bot")
    logger.info("   - 修改Token → 自动重启Bot")
    logger.info("   - 禁用配置 → 自动停止Bot")
    logger.info("=" * 60)
    
    # 存储当前运行的进程：{admin_user_id: (process, config_hash)}
    running_processes = {}
    
    # 存储失败的配置（Token 无效）：{admin_user_id: error_message}
    failed_configs = {}
    
    # 配置检查间隔（秒）
    check_interval = 10
    
    try:
        while True:
            # 获取当前激活的Bot配置
            current_configs = get_active_bot_configs()
            
            # 首次启动时的提示
            if not running_processes and not current_configs:
                logger.warning("⚠️  暂无激活的Bot配置")
                logger.info("📝 请通过后台管理页面配置Bot Token")
                logger.info(f"🔄 将在 {check_interval} 秒后重新检查...")
                time.sleep(check_interval)
                continue
            
            # 构建当前配置的映射：{admin_user_id: config}
            current_config_map = {
                config['admin_user_id']: config 
                for config in current_configs
            }
            
            # 1. 检查需要停止的Bot（配置被删除或禁用）
            user_ids_to_stop = set(running_processes.keys()) - set(current_config_map.keys())
            for user_id in user_ids_to_stop:
                p, old_hash = running_processes[user_id]
                logger.info(f"🛑 停止Bot: User ID {user_id} (配置已禁用或删除)")
                p.terminate()
                p.join(timeout=5)
                if p.is_alive():
                    p.kill()
                del running_processes[user_id]
            
            # 2. 检查需要启动或重启的Bot
            for user_id, config in current_config_map.items():
                username = config['bot_username']
                token = config['bot_token']
                
                # 计算配置哈希（用于检测变化）
                config_hash = hash(f"{token}_{username}")
                
                if user_id in running_processes:
                    # Bot已运行，检查配置是否变化
                    p, old_hash = running_processes[user_id]
                    
                    if config_hash != old_hash:
                        # 配置变化，重启Bot
                        logger.info(f"🔄 重启Bot: {username} (User ID: {user_id}) - 配置已更新")
                        p.terminate()
                        p.join(timeout=5)
                        if p.is_alive():
                            p.kill()
                        
                        # 启动新进程
                        new_p = multiprocessing.Process(
                            target=run_bot_instance,
                            args=(user_id, token, username)
                        )
                        new_p.start()
                        running_processes[user_id] = (new_p, config_hash)
                    
                    elif not p.is_alive():
                        # 进程退出，检查退出码
                        exit_code = p.exitcode
                        
                        if exit_code == 2:
                            # Token 无效错误 - 不重启
                            logger.error(f"🚫 [{username}] Token 无效，已停止自动重启")
                            logger.error(f"   请前往后台管理页面更新正确的 Bot Token")
                            failed_configs[user_id] = f"Token 无效 (退出码: {exit_code})"
                            del running_processes[user_id]
                        else:
                            # 其他错误 - 尝试重启
                            logger.warning(f"⚠️  Bot进程意外退出: {username} (User ID: {user_id}, 退出码: {exit_code})")
                            logger.info(f"🔄 重新启动: {username}")
                            new_p = multiprocessing.Process(
                                target=run_bot_instance,
                                args=(user_id, token, username)
                            )
                            new_p.start()
                            running_processes[user_id] = (new_p, config_hash)
                else:
                    # 新配置或之前失败的配置被更新
                    if user_id in failed_configs:
                        # 配置已更新，从失败列表中移除，重新尝试
                        logger.info(f"🔄 配置已更新，重新尝试启动: {username} (User ID: {user_id})")
                        del failed_configs[user_id]
                    else:
                        logger.info(f"🆕 发现新配置，启动Bot: {username} (User ID: {user_id})")
                    
                    p = multiprocessing.Process(
                        target=run_bot_instance,
                        args=(user_id, token, username)
                    )
                    p.start()
                    running_processes[user_id] = (p, config_hash)
            
            # 显示当前状态
            if running_processes or failed_configs:
                status_msg = f"📊 当前运行: {len(running_processes)} 个Bot"
                if failed_configs:
                    status_msg += f" | ❌ 失败: {len(failed_configs)} 个"
                status_msg += f" | 下次检查: {check_interval}秒后"
                logger.info(status_msg)
                
                # 显示失败的详情（每 60 秒提醒一次）
                if failed_configs and int(time.time()) % 60 < check_interval:
                    for user_id, error_msg in failed_configs.items():
                        logger.warning(f"   ⚠️  User ID {user_id}: {error_msg}")
            
            # 等待下次检查
            time.sleep(check_interval)
            
    except KeyboardInterrupt:
        logger.info("\n" + "=" * 60)
        logger.info("⏹️  收到停止信号，正在关闭所有Bot...")
        logger.info("=" * 60)
        
        for user_id, (p, _) in running_processes.items():
            logger.info(f"🛑 停止 Bot (User ID: {user_id})")
            p.terminate()
            p.join(timeout=3)
            if p.is_alive():
                logger.warning(f"⚠️  强制终止 Bot (User ID: {user_id})")
                p.kill()
        
        logger.info("=" * 60)
        logger.info("👋 所有Bot已停止")
        logger.info("=" * 60)


if __name__ == '__main__':
    # 设置多进程启动方式（Windows需要spawn，Linux默认fork更快）
    if sys.platform == 'win32':
        multiprocessing.set_start_method('spawn', force=True)
    else:
        # Linux/Mac 使用默认的 fork 方式（性能更好）
        try:
            multiprocessing.set_start_method('fork')
        except RuntimeError:
            # 如果已经设置过，忽略
            pass
    
    main()


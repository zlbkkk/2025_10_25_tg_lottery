"""
自动开奖守护进程 - 持续运行版本
每分钟自动检查一次是否有需要开奖的抽奖活动
"""
import os
import django
import time
from datetime import datetime

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lottery_backend.settings')
django.setup()

from django.utils import timezone
from lottery.models import Lottery
import logging

# 配置日志 - 同时输出到控制台和文件
import sys

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(current_dir, 'auto_draw.log')

# 配置日志格式
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
date_format = '%Y-%m-%d %H:%M:%S'

# 创建logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 控制台输出
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(log_format, date_format))

# 文件输出（追加模式）
file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter(log_format, date_format))

# 添加处理器
logger.addHandler(console_handler)
logger.addHandler(file_handler)


def auto_draw_lotteries():
    """自动开奖函数"""
    # 使用 datetime.now() 获取当前本地时间（兼容 USE_TZ = False）
    from datetime import datetime as dt
    now = dt.now()
    
    # 截断到分钟级别（秒和微秒设为0）
    now_minute = now.replace(second=0, microsecond=0)
    
    logger.info(f"当前时间: {now}（比对到分钟: {now_minute}）")
    
    # 查找所有进行中且未手动开奖的抽奖
    candidates = Lottery.objects.filter(
        status='active',
        manual_drawn=False
    )
    
    # 手动过滤：处理时区兼容问题
    lotteries_to_draw = []
    for lottery in candidates:
        end_time = lottery.end_time
        
        # 如果是 aware datetime，转换为 naive
        if timezone.is_aware(end_time):
            end_time = timezone.make_naive(end_time)
        
        # 截断到分钟级别（秒和微秒设为0）
        end_time_minute = end_time.replace(second=0, microsecond=0)
        
        logger.info(f"检查抽奖: {lottery.title} (ID: {lottery.id}), 结束时间: {end_time}")
        
        # 判断是否到达结束时间（分钟级别比对）
        if end_time_minute <= now_minute:
            lotteries_to_draw.append(lottery)
            logger.info(f"  → 需要开奖")
        else:
            # 计算还需等待的分钟数
            wait_minutes = int((end_time_minute - now_minute).total_seconds() / 60)
            logger.info(f"  → 未到结束时间，还需等待约 {wait_minutes} 分钟")
    
    draw_count = len(lotteries_to_draw)
    
    if draw_count > 0:
        logger.info(f"发现 {draw_count} 个需要自动开奖的活动")
        
        success_count = 0
        fail_count = 0
        
        for lottery in lotteries_to_draw:
            logger.info(f"正在自动开奖: {lottery.title} (ID: {lottery.id})")
            
            try:
                # 执行开奖
                success = lottery.draw_winners()
                
                if success:
                    success_count += 1
                    logger.info(f"✓ 自动开奖成功: {lottery.title} (ID: {lottery.id})")
                else:
                    fail_count += 1
                    logger.error(f"✗ 自动开奖失败: {lottery.title} (ID: {lottery.id})")
                    
            except Exception as e:
                fail_count += 1
                logger.error(f"✗ 自动开奖异常: {lottery.title} (ID: {lottery.id}) - {str(e)}")
        
        logger.info(f"本次任务完成: 成功 {success_count} 个, 失败 {fail_count} 个")
    
    return draw_count


def run_daemon():
    """运行守护进程"""
    logger.info("=" * 60)
    logger.info("自动开奖守护进程已启动")
    logger.info("检查间隔: 60秒")
    logger.info("=" * 60)
    
    check_count = 0
    
    try:
        while True:
            check_count += 1
            logger.info(f"[第 {check_count} 次检查] 开始扫描需要开奖的活动...")
            
            try:
                draw_count = auto_draw_lotteries()
                if draw_count == 0:
                    logger.info("暂无需要开奖的活动")
            except Exception as e:
                logger.error(f"执行自动开奖时出错: {str(e)}")
            
            # 等待60秒
            logger.info("等待60秒后进行下次检查...\n")
            time.sleep(60)
            
    except KeyboardInterrupt:
        logger.info("\n收到中断信号，停止守护进程...")
        logger.info("自动开奖守护进程已安全退出")


if __name__ == '__main__':
    print("=" * 60)
    print("自动开奖守护进程")
    print("=" * 60)
    print("程序将每60秒检查一次是否有需要开奖的活动")
    print("按 Ctrl+C 可以停止程序")
    print("=" * 60)
    print()
    
    run_daemon()

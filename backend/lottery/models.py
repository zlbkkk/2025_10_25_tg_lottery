"""
抽奖系统数据库模型
"""
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
import random
import requests
import logging

logger = logging.getLogger(__name__)


class BotConfig(models.Model):
    """Bot配置模型 - 每个租户配置自己的Bot Token"""
    admin_user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='bot_config',
        verbose_name='管理员',
        primary_key=True
    )
    bot_token = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Bot Token',
        help_text='Telegram Bot Token (从 @BotFather 获取)'
    )
    bot_username = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Bot 用户名',
        help_text='Bot的用户名 (例如: @MyLotteryBot)'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='是否启用',
        help_text='关闭后该Bot将停止工作'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'bot_configs'
        verbose_name = 'Bot配置'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.admin_user.username}'s Bot ({self.bot_username or 'Not configured'})"


class LoginRecord(models.Model):
    """登录记录模型 - 记录用户登录和退出信息"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='login_records',
        verbose_name='用户'
    )
    ip_address = models.GenericIPAddressField(
        verbose_name='IP地址',
        null=True,
        blank=True
    )
    user_agent = models.TextField(
        verbose_name='用户代理',
        help_text='浏览器和设备信息',
        null=True,
        blank=True
    )
    device_type = models.CharField(
        max_length=50,
        verbose_name='设备类型',
        help_text='例如：Windows, Mac, Mobile',
        null=True,
        blank=True
    )
    browser = models.CharField(
        max_length=100,
        verbose_name='浏览器',
        help_text='例如：Chrome, Firefox, Safari',
        null=True,
        blank=True
    )
    login_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='登录时间'
    )
    logout_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='退出时间'
    )
    session_key = models.CharField(
        max_length=255,
        verbose_name='会话密钥',
        help_text='用于关联会话',
        null=True,
        blank=True,
        db_index=True
    )
    last_activity = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='最后活动时间',
        help_text='用户最后一次活动的时间'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='会话是否活跃'
    )

    class Meta:
        db_table = 'login_records'
        verbose_name = '登录记录'
        verbose_name_plural = verbose_name
        ordering = ['-login_time']
        indexes = [
            models.Index(fields=['-login_time']),
            models.Index(fields=['user', '-login_time']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.ip_address} - {self.login_time.strftime('%Y-%m-%d %H:%M:%S')}"
    
    @property
    def session_duration(self):
        """计算会话时长"""
        if self.logout_time:
            duration = self.logout_time - self.login_time
            return int(duration.total_seconds())
        return None
    
    @property
    def is_truly_active(self):
        """
        智能判断是否真正在线
        如果超过1小时没有活动，视为离线
        """
        from django.utils import timezone
        from datetime import timedelta
        
        if not self.is_active:
            return False
        
        if self.logout_time:
            return False
        
        # 如果有最后活动时间，检查是否超时
        if self.last_activity:
            timeout = timedelta(hours=1)  # 1小时超时
            return timezone.now() - self.last_activity < timeout
        
        # 如果没有最后活动时间，使用登录时间判断
        timeout = timedelta(hours=1)
        return timezone.now() - self.login_time < timeout


class TelegramUser(models.Model):
    """Telegram 用户模型"""
    telegram_id = models.BigIntegerField(unique=True, verbose_name='Telegram ID')
    username = models.CharField(max_length=255, null=True, blank=True, verbose_name='用户名')
    first_name = models.CharField(max_length=255, null=True, blank=True, verbose_name='名字')
    last_name = models.CharField(max_length=255, null=True, blank=True, verbose_name='姓氏')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'telegram_users'
        verbose_name = 'Telegram用户'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.username or self.first_name} ({self.telegram_id})"
    
    def get_display_name(self):
        """获取显示名称"""
        if self.last_name and self.first_name:
            return f"{self.first_name}{self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        elif self.username:
            return self.username
        else:
            return f"User_{self.telegram_id}"


class Lottery(models.Model):
    """抽奖活动模型"""
    STATUS_CHOICES = [
        ('pending', '待开始'),
        ('active', '进行中'),
        ('finished', '已结束'),
        ('cancelled', '已取消'),
    ]

    # 管理员用户（老板账号）- 用于多租户数据隔离
    admin_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='managed_lotteries',
        verbose_name='管理员',
        null=True,
        blank=True,
        help_text='创建此抽奖的管理员账号'
    )
    
    # Telegram创建者（保留用于兼容）
    creator = models.ForeignKey(
        TelegramUser, 
        on_delete=models.CASCADE, 
        related_name='created_lotteries',
        verbose_name='Telegram创建者',
        null=True,
        blank=True
    )
    
    title = models.CharField(max_length=255, verbose_name='抽奖标题')
    description = models.TextField(blank=True, verbose_name='抽奖说明')
    prize_name = models.CharField(max_length=255, verbose_name='奖品名称')
    prize_count = models.IntegerField(default=1, verbose_name='奖品数量')
    prize_image = models.ImageField(
        upload_to='prizes/', 
        null=True, 
        blank=True, 
        verbose_name='奖品图片'
    )
    
    max_participants = models.IntegerField(
        default=0, 
        verbose_name='最大参与人数',
        help_text='0表示不限制'
    )
    
    start_time = models.DateTimeField(verbose_name='开始时间')
    end_time = models.DateTimeField(verbose_name='结束时间')
    
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name='状态'
    )
    
    manual_drawn = models.BooleanField(
        default=False,
        verbose_name='是否手动开奖',
        help_text='如果手动开奖，则不会自动开奖'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'lotteries'
        verbose_name = '抽奖活动'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.prize_name}"

    @property
    def participant_count(self):
        """参与人数"""
        return self.participations.count()

    @property
    def winner_count(self):
        """中奖人数"""
        return self.winners.count()

    @property
    def is_active(self):
        """是否进行中"""
        from datetime import datetime
        now = datetime.now()
        
        # 兼容处理：确保时间都是 naive datetime
        start_time = self.start_time
        end_time = self.end_time
        
        if timezone.is_aware(start_time):
            start_time = timezone.make_naive(start_time)
        if timezone.is_aware(end_time):
            end_time = timezone.make_naive(end_time)
        
        return (
            self.status == 'active' and 
            start_time <= now <= end_time
        )

    @property
    def can_participate(self):
        """是否可以参与"""
        if not self.is_active:
            return False
        if self.max_participants > 0 and self.participant_count >= self.max_participants:
            return False
        return True

    def draw_winners(self):
        """
        执行开奖（支持多奖品）
        
        开奖策略：
        1. 按奖品等级从高到低（level从小到大）依次抽奖
        2. 每个参与者最多只能中一个奖品
        3. 高等级奖品优先抽取
        4. 允许没有参与者的情况（开奖成功但无中奖者）
        """
        if self.status != 'active':
            return False
        
        # 获取所有参与者
        all_participants = list(self.participations.all())
        
        # 获取所有奖品（按等级排序）
        prizes = list(self.prizes.all().order_by('level', 'id'))
        
        if not prizes:
            logger.warning(f'抽奖 {self.id} 没有设置奖品')
            return False
        
        # 如果没有参与者，直接结束抽奖（状态变为finished，但无中奖记录）
        if not all_participants:
            logger.warning(f'抽奖 {self.id} 没有参与者，开奖成功但无中奖者')
            self.status = 'finished'
            self.save()
            return True
        
        # 创建中奖记录
        winner_data = []  # [(user, prize), ...]
        remaining_participants = all_participants.copy()
        
        # 按奖品等级依次抽奖
        for prize in prizes:
            if not remaining_participants:
                logger.info(f'奖品 {prize.name} 抽奖时已无剩余参与者')
                break
            
            # 确定本奖品的中奖人数
            actual_winner_count = min(prize.winner_count, len(remaining_participants))
            
            # 随机抽取中奖者
            selected_winners = random.sample(remaining_participants, actual_winner_count)
            
            # 记录中奖信息并创建Winner记录
            for participation in selected_winners:
                Winner.objects.create(
                    lottery=self,
                    prize=prize,
                    user=participation.user,
                    prize_name=prize.name  # 冗余字段，便于查询
                )
                winner_data.append((participation.user, prize))
                # 从候选池中移除（确保每人只中一次奖）
                remaining_participants.remove(participation)
            
            logger.info(f'奖品 {prize.name} 抽取了 {actual_winner_count} 位中奖者')
        
        # 更新状态
        self.status = 'finished'
        self.save()
        
        # 发送通知给中奖者
        if winner_data:
            self._send_winner_notifications_multi_prize(winner_data)
        
        return True
    
    def _send_winner_notifications_multi_prize(self, winner_data):
        """
        发送多奖品中奖通知
        
        Args:
            winner_data: [(user, prize), ...] 中奖用户和奖品的列表
        """
        bot_token = settings.TELEGRAM_BOT_TOKEN
        if not bot_token:
            logger.warning('BOT_TOKEN 未配置，无法发送通知')
            return
        
        for user, prize in winner_data:
            try:
                # 构造通知消息（包含奖品等级信息）
                level_text = self._get_level_text(prize.level)
                message = (
                    f"🎉🎉🎉 恭喜您中奖啦！\n\n"
                    f"📋 抽奖活动：{self.title}\n"
                    f"🏆 获得奖品：{level_text} {prize.name}\n"
                )
                
                if prize.description:
                    message += f"📝 奖品说明：{prize.description}\n"
                
                message += "\n请联系管理员领取您的奖品！"
                
                # 如果有奖品图片，发送图片消息
                if prize.image:
                    from django.conf import settings as django_settings
                    image_url = f"http://localhost:8000{prize.image.url}"
                    
                    url = f'https://api.telegram.org/bot{bot_token}/sendPhoto'
                    data = {
                        'chat_id': user.telegram_id,
                        'photo': image_url,
                        'caption': message,
                        'parse_mode': 'HTML'
                    }
                else:
                    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
                    data = {
                        'chat_id': user.telegram_id,
                        'text': message,
                        'parse_mode': 'HTML'
                    }
                
                response = requests.post(url, json=data, timeout=10)
                
                if response.status_code == 200:
                    logger.info(f'成功发送中奖通知给用户 {user.telegram_id} - 奖品: {prize.name}')
                else:
                    logger.error(f'发送通知失败: {response.status_code} - {response.text}')
                    
            except Exception as e:
                logger.error(f'发送通知给用户 {user.telegram_id} 时出错: {str(e)}')
    
    def _get_level_text(self, level):
        """根据等级返回对应的文本"""
        level_map = {
            1: '🥇一等奖',
            2: '🥈二等奖',
            3: '🥉三等奖',
        }
        return level_map.get(level, f'第{level}等奖')
    
    def _send_winner_notifications(self, winner_users):
        """发送中奖通知给用户"""
        bot_token = settings.TELEGRAM_BOT_TOKEN
        if not bot_token:
            logger.warning('BOT_TOKEN 未配置，无法发送通知')
            return
        
        for user in winner_users:
            try:
                # 构造通知消息
                message = (
                    f"🎉 恭喜您中奖啦！\n\n"
                    f"📋 抽奖活动：{self.title}\n"
                    f"🎁 奖品：{self.prize_name}\n"
                    f"📝 说明：{self.description}\n\n"
                    f"请联系管理员领取奖品！"
                )
                
                # 如果有奖品图片，发送图片消息
                if self.prize_image:
                    # 获取图片的完整 URL
                    from django.conf import settings as django_settings
                    image_url = f"http://localhost:8000{self.prize_image.url}"
                    
                    # 发送图片消息
                    url = f'https://api.telegram.org/bot{bot_token}/sendPhoto'
                    data = {
                        'chat_id': user.telegram_id,
                        'photo': image_url,
                        'caption': message,
                        'parse_mode': 'HTML'
                    }
                else:
                    # 只发送文字消息
                    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
                    data = {
                        'chat_id': user.telegram_id,
                        'text': message,
                        'parse_mode': 'HTML'
                    }
                
                response = requests.post(url, json=data, timeout=10)
                
                if response.status_code == 200:
                    logger.info(f'成功发送中奖通知给用户 {user.telegram_id}')
                else:
                    logger.error(f'发送通知失败: {response.status_code} - {response.text}')
                    
            except Exception as e:
                logger.error(f'发送通知给用户 {user.telegram_id} 时出错: {str(e)}')


class Participation(models.Model):
    """参与记录模型"""
    lottery = models.ForeignKey(
        Lottery, 
        on_delete=models.CASCADE, 
        related_name='participations',
        verbose_name='抽奖活动'
    )
    user = models.ForeignKey(
        TelegramUser, 
        on_delete=models.CASCADE, 
        related_name='participations',
        verbose_name='参与用户'
    )
    participated_at = models.DateTimeField(auto_now_add=True, verbose_name='参与时间')

    class Meta:
        db_table = 'participations'
        verbose_name = '参与记录'
        verbose_name_plural = verbose_name
        unique_together = ['lottery', 'user']  # 同一用户只能参与一次
        ordering = ['-participated_at']

    def __str__(self):
        return f"{self.user} 参与 {self.lottery.title}"


class Prize(models.Model):
    """奖品模型"""
    lottery = models.ForeignKey(
        Lottery,
        on_delete=models.CASCADE,
        related_name='prizes',
        verbose_name='抽奖活动'
    )
    name = models.CharField(max_length=255, verbose_name='奖品名称')
    description = models.TextField(blank=True, verbose_name='奖品描述')
    image = models.ImageField(
        upload_to='prizes/',
        null=True,
        blank=True,
        verbose_name='奖品图片'
    )
    winner_count = models.IntegerField(default=1, verbose_name='中奖人数')
    level = models.IntegerField(default=1, verbose_name='奖品等级', help_text='数字越小等级越高，1=一等奖')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'prizes'
        verbose_name = '奖品'
        verbose_name_plural = verbose_name
        ordering = ['level', 'id']

    def __str__(self):
        return f"{self.lottery.title} - {self.name} (x{self.winner_count})"

    @property
    def winner_list_count(self):
        """已中奖人数"""
        return self.winners.count()


class Winner(models.Model):
    """中奖记录模型"""
    lottery = models.ForeignKey(
        Lottery, 
        on_delete=models.CASCADE, 
        related_name='winners',
        verbose_name='抽奖活动'
    )
    prize = models.ForeignKey(
        Prize,
        on_delete=models.CASCADE,
        related_name='winners',
        verbose_name='中奖奖品',
        null=True,  # 兼容旧数据
        blank=True
    )
    user = models.ForeignKey(
        TelegramUser, 
        on_delete=models.CASCADE, 
        related_name='won_lotteries',
        verbose_name='中奖用户'
    )
    prize_name = models.CharField(max_length=255, verbose_name='奖品名称')  # 保留用于向后兼容
    won_at = models.DateTimeField(auto_now_add=True, verbose_name='中奖时间')
    claimed = models.BooleanField(default=False, verbose_name='是否已领取')

    class Meta:
        db_table = 'winners'
        verbose_name = '中奖记录'
        verbose_name_plural = verbose_name
        ordering = ['-won_at']

    def __str__(self):
        prize_display = self.prize.name if self.prize else self.prize_name
        return f"{self.user} 中奖 {prize_display}"

"""
抽奖系统数据库模型
"""
from django.db import models
from django.utils import timezone
from django.conf import settings
import random
import requests
import logging

logger = logging.getLogger(__name__)


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


class Lottery(models.Model):
    """抽奖活动模型"""
    STATUS_CHOICES = [
        ('pending', '待开始'),
        ('active', '进行中'),
        ('finished', '已结束'),
        ('cancelled', '已取消'),
    ]

    creator = models.ForeignKey(
        TelegramUser, 
        on_delete=models.CASCADE, 
        related_name='created_lotteries',
        verbose_name='创建者',
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
        now = timezone.now()
        return (
            self.status == 'active' and 
            self.start_time <= now <= self.end_time
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
        """执行开奖"""
        if self.status != 'active':
            return False
        
        # 获取所有参与者
        participants = list(self.participations.all())
        
        if len(participants) < self.prize_count:
            # 参与人数少于奖品数量
            winners = participants
        else:
            # 随机抽取中奖者
            winners = random.sample(participants, self.prize_count)
        
        # 创建中奖记录
        winner_users = []
        for participation in winners:
            Winner.objects.create(
                lottery=self,
                user=participation.user,
                prize_name=self.prize_name
            )
            winner_users.append(participation.user)
        
        # 更新状态
        self.status = 'finished'
        self.save()
        
        # 发送通知给中奖者
        self._send_winner_notifications(winner_users)
        
        return True
    
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
                
                # 调用 Telegram Bot API
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


class Winner(models.Model):
    """中奖记录模型"""
    lottery = models.ForeignKey(
        Lottery, 
        on_delete=models.CASCADE, 
        related_name='winners',
        verbose_name='抽奖活动'
    )
    user = models.ForeignKey(
        TelegramUser, 
        on_delete=models.CASCADE, 
        related_name='won_lotteries',
        verbose_name='中奖用户'
    )
    prize_name = models.CharField(max_length=255, verbose_name='奖品名称')
    won_at = models.DateTimeField(auto_now_add=True, verbose_name='中奖时间')
    claimed = models.BooleanField(default=False, verbose_name='是否已领取')

    class Meta:
        db_table = 'winners'
        verbose_name = '中奖记录'
        verbose_name_plural = verbose_name
        ordering = ['-won_at']

    def __str__(self):
        return f"{self.user} 中奖 {self.prize_name}"

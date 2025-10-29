"""
Django REST Framework 序列化器
"""
from rest_framework import serializers
from .models import TelegramUser, Lottery, Prize, Participation, Winner, BotConfig, LoginRecord


class TelegramUserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    class Meta:
        model = TelegramUser
        fields = ['id', 'telegram_id', 'username', 'first_name', 'last_name', 'created_at']
        read_only_fields = ['id', 'created_at']


class PrizeSerializer(serializers.ModelSerializer):
    """奖品序列化器"""
    winner_list_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Prize
        fields = ['id', 'name', 'description', 'image', 'winner_count', 'level', 'winner_list_count', 'created_at']
        read_only_fields = ['id', 'created_at', 'winner_list_count']
    
    def get_winner_list_count(self, obj):
        """获取该奖品的实际中奖人数"""
        return obj.winners.count()


class LotteryListSerializer(serializers.ModelSerializer):
    """抽奖列表序列化器（简化版）"""
    participant_count = serializers.IntegerField(read_only=True)
    winner_count = serializers.IntegerField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    can_participate = serializers.BooleanField(read_only=True)
    prizes = PrizeSerializer(many=True, read_only=True)
    
    # 保留旧字段用于向后兼容
    prize_name = serializers.SerializerMethodField()
    prize_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Lottery
        fields = [
            'id', 'title', 'prize_name', 'prize_count', 'prize_image',
            'max_participants', 'start_time', 'end_time', 'status',
            'participant_count', 'winner_count',
            'is_active', 'can_participate', 'prizes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_prize_name(self, obj):
        """向后兼容：返回第一个奖品名称"""
        first_prize = obj.prizes.first()
        return first_prize.name if first_prize else obj.prize_name
    
    def get_prize_count(self, obj):
        """向后兼容：返回总中奖人数"""
        return sum(p.winner_count for p in obj.prizes.all()) if obj.prizes.exists() else obj.prize_count


class ParticipationSerializer(serializers.ModelSerializer):
    """参与记录序列化器"""
    user = TelegramUserSerializer(read_only=True)
    
    class Meta:
        model = Participation
        fields = ['id', 'user', 'participated_at']
        read_only_fields = ['id', 'participated_at']


class ParticipationWithLotterySerializer(serializers.ModelSerializer):
    """参与记录序列化器（包含抽奖信息）"""
    user = TelegramUserSerializer(read_only=True)
    lottery = LotteryListSerializer(read_only=True)
    
    class Meta:
        model = Participation
        fields = ['id', 'user', 'lottery', 'participated_at']
        read_only_fields = ['id', 'participated_at']


class WinnerSerializer(serializers.ModelSerializer):
    """中奖记录序列化器"""
    user = TelegramUserSerializer(read_only=True)
    prize = PrizeSerializer(read_only=True)
    prize_display_name = serializers.SerializerMethodField()
    prize_level_text = serializers.SerializerMethodField()
    
    class Meta:
        model = Winner
        fields = ['id', 'user', 'prize', 'prize_name', 'prize_display_name', 'prize_level_text', 'won_at', 'claimed']
        read_only_fields = ['id', 'won_at']
    
    def get_prize_display_name(self, obj):
        """获取显示用的奖品名称（优先使用Prize，否则使用旧的prize_name）"""
        return obj.prize.name if obj.prize else obj.prize_name
    
    def get_prize_level_text(self, obj):
        """获取奖品等级文本"""
        if not obj.prize:
            return '-'
        
        level_map = {
            1: '🥇一等奖',
            2: '🥈二等奖',
            3: '🥉三等奖',
            4: '四等奖',
            5: '五等奖',
        }
        return level_map.get(obj.prize.level, f'第{obj.prize.level}等奖')


class LotteryDetailSerializer(serializers.ModelSerializer):
    """抽奖详情序列化器（完整版）"""
    participations = ParticipationSerializer(many=True, read_only=True)
    winners = WinnerSerializer(many=True, read_only=True)
    prizes = PrizeSerializer(many=True, read_only=True)
    participant_count = serializers.IntegerField(read_only=True)
    winner_count = serializers.IntegerField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    can_participate = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Lottery
        fields = [
            'id', 'title', 'description', 'prize_name', 'prize_count', 'prize_image',
            'max_participants', 'start_time', 'end_time', 'status',
            'prizes', 'participations', 'winners',
            'participant_count', 'winner_count',
            'is_active', 'can_participate',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PrizeCreateSerializer(serializers.Serializer):
    """创建奖品序列化器（用于嵌套在抽奖创建中）"""
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    winner_count = serializers.IntegerField(min_value=1)
    level = serializers.IntegerField(min_value=1, required=False, default=1)


class LotteryCreateSerializer(serializers.ModelSerializer):
    """创建抽奖序列化器（支持多奖品）"""
    prize_image = serializers.ImageField(required=False, allow_null=True)
    prizes = PrizeCreateSerializer(many=True, required=False)  # 新：多奖品
    
    # 明确指定时间字段的输入格式
    start_time = serializers.DateTimeField(
        input_formats=['%Y-%m-%d %H:%M:%S']
    )
    end_time = serializers.DateTimeField(
        input_formats=['%Y-%m-%d %H:%M:%S']
    )
    
    class Meta:
        model = Lottery
        fields = [
            'title', 'description', 'prize_name', 'prize_count', 'prize_image',
            'max_participants', 'start_time', 'end_time', 'prizes'
        ]
    
    def validate_prize_image(self, value):
        """验证图片字段"""
        if value == '':
            return None
        return value
    
    def validate(self, data):
        """验证数据"""
        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError("结束时间必须晚于开始时间")
        
        # 如果提供了prizes，则验证prizes
        if 'prizes' in data and data['prizes']:
            if not data['prizes']:
                raise serializers.ValidationError("至少需要一个奖品")
        else:
            # 向后兼容：使用旧的prize_name和prize_count
            if data.get('prize_count', 0) < 1:
                raise serializers.ValidationError("奖品数量必须大于0")
        
        if data.get('max_participants', 0) < 0:
            raise serializers.ValidationError("最大参与人数不能为负数")
        
        return data
    
    def create(self, validated_data):
        """创建抽奖和奖品"""
        prizes_data = validated_data.pop('prizes', [])
        
        # 调试：打印奖品数据
        print(f"[DEBUG] Creating lottery with {len(prizes_data)} prizes")
        for i, prize in enumerate(prizes_data):
            print(f"[DEBUG] Prize {i+1}: {prize}")
        
        # 创建抽奖活动
        lottery = Lottery.objects.create(**validated_data)
        
        # 如果提供了prizes数据，创建多个奖品
        if prizes_data:
            for prize_data in prizes_data:
                created_prize = Prize.objects.create(lottery=lottery, **prize_data)
                print(f"[DEBUG] Created prize: {created_prize.name} (level: {created_prize.level})")
        else:
            # 向后兼容：使用旧字段创建单个奖品
            Prize.objects.create(
                lottery=lottery,
                name=lottery.prize_name,
                winner_count=lottery.prize_count,
                level=1
            )
        
        return lottery
    
    def update(self, instance, validated_data):
        """更新抽奖和奖品"""
        prizes_data = validated_data.pop('prizes', None)
        
        # 更新抽奖基本信息
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # 如果提供了prizes数据，更新奖品
        if prizes_data is not None:
            # 删除旧的奖品（如果有中奖记录则不删除，只更新）
            if not instance.winners.exists():
                instance.prizes.all().delete()
                # 创建新的奖品
                for prize_data in prizes_data:
                    Prize.objects.create(lottery=instance, **prize_data)
            else:
                # 有中奖记录的情况，只更新已有奖品，不删除
                existing_prizes = list(instance.prizes.all())
                for i, prize_data in enumerate(prizes_data):
                    if i < len(existing_prizes):
                        # 更新已有奖品
                        prize = existing_prizes[i]
                        for attr, value in prize_data.items():
                            setattr(prize, attr, value)
                        prize.save()
                    else:
                        # 新增奖品
                        Prize.objects.create(lottery=instance, **prize_data)
        
        return instance


class BotConfigSerializer(serializers.ModelSerializer):
    """Bot配置序列化器"""
    username = serializers.CharField(source='admin_user.username', read_only=True)
    
    class Meta:
        model = BotConfig
        fields = ['admin_user_id', 'username', 'bot_token', 'bot_username', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['admin_user_id', 'username', 'created_at', 'updated_at']
        extra_kwargs = {
            'bot_token': {'write_only': True}  # 安全起见，不返回完整token
        }
    
    def to_representation(self, instance):
        """自定义输出，只返回token的前缀"""
        data = super().to_representation(instance)
        if instance.bot_token:
            # 只显示token的前10个字符 + ***
            data['bot_token_preview'] = instance.bot_token[:10] + '***' if len(instance.bot_token) > 10 else '***'
        else:
            data['bot_token_preview'] = None
        return data


class LoginRecordSerializer(serializers.ModelSerializer):
    """登录记录序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    full_name = serializers.SerializerMethodField()
    session_duration = serializers.IntegerField(read_only=True)
    is_truly_active = serializers.BooleanField(read_only=True)  # 智能状态
    
    class Meta:
        model = LoginRecord
        fields = [
            'id', 'username', 'first_name', 'last_name', 'full_name',
            'ip_address', 'user_agent', 'device_type', 'browser', 
            'login_time', 'logout_time', 'last_activity',
            'session_duration', 'is_active', 'is_truly_active'
        ]
        read_only_fields = ['id', 'username', 'first_name', 'last_name', 'full_name', 
                           'login_time', 'last_activity', 'session_duration', 
                           'is_active', 'is_truly_active']
    
    def get_full_name(self, obj):
        """获取完整姓名"""
        last_name = obj.user.last_name or ''
        first_name = obj.user.first_name or ''
        full_name = f"{last_name}{first_name}".strip()
        return full_name if full_name else obj.user.username
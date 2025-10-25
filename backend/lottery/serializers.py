"""
Django REST Framework 序列化器
"""
from rest_framework import serializers
from .models import TelegramUser, Lottery, Participation, Winner


class TelegramUserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    class Meta:
        model = TelegramUser
        fields = ['id', 'telegram_id', 'username', 'first_name', 'last_name', 'created_at']
        read_only_fields = ['id', 'created_at']


class WinnerSerializer(serializers.ModelSerializer):
    """中奖记录序列化器"""
    user = TelegramUserSerializer(read_only=True)
    
    class Meta:
        model = Winner
        fields = ['id', 'user', 'prize_name', 'won_at', 'claimed']
        read_only_fields = ['id', 'won_at']


class ParticipationSerializer(serializers.ModelSerializer):
    """参与记录序列化器"""
    user = TelegramUserSerializer(read_only=True)
    
    class Meta:
        model = Participation
        fields = ['id', 'user', 'participated_at']
        read_only_fields = ['id', 'participated_at']


class LotteryListSerializer(serializers.ModelSerializer):
    """抽奖列表序列化器（简化版）"""
    creator = TelegramUserSerializer(read_only=True)
    participant_count = serializers.IntegerField(read_only=True)
    winner_count = serializers.IntegerField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    can_participate = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Lottery
        fields = [
            'id', 'title', 'prize_name', 'prize_count', 'prize_image',
            'max_participants', 'start_time', 'end_time', 'status',
            'creator', 'participant_count', 'winner_count',
            'is_active', 'can_participate', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class LotteryDetailSerializer(serializers.ModelSerializer):
    """抽奖详情序列化器（完整版）"""
    creator = TelegramUserSerializer(read_only=True)
    participations = ParticipationSerializer(many=True, read_only=True)
    winners = WinnerSerializer(many=True, read_only=True)
    participant_count = serializers.IntegerField(read_only=True)
    winner_count = serializers.IntegerField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    can_participate = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Lottery
        fields = [
            'id', 'title', 'description', 'prize_name', 'prize_count', 'prize_image',
            'max_participants', 'start_time', 'end_time', 'status',
            'creator', 'participations', 'winners',
            'participant_count', 'winner_count',
            'is_active', 'can_participate',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class LotteryCreateSerializer(serializers.ModelSerializer):
    """创建抽奖序列化器"""
    class Meta:
        model = Lottery
        fields = [
            'title', 'description', 'prize_name', 'prize_count', 'prize_image',
            'max_participants', 'start_time', 'end_time'
        ]
    
    def validate(self, data):
        """验证数据"""
        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError("结束时间必须晚于开始时间")
        
        if data['prize_count'] < 1:
            raise serializers.ValidationError("奖品数量必须大于0")
        
        if data['max_participants'] < 0:
            raise serializers.ValidationError("最大参与人数不能为负数")
        
        return data

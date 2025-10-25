"""
Django REST Framework 视图
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Count
from .models import TelegramUser, Lottery, Participation, Winner
from .serializers import (
    TelegramUserSerializer,
    LotteryListSerializer,
    LotteryDetailSerializer,
    LotteryCreateSerializer,
    ParticipationSerializer,
    WinnerSerializer
)


class TelegramUserViewSet(viewsets.ModelViewSet):
    """用户视图集"""
    queryset = TelegramUser.objects.all()
    serializer_class = TelegramUserSerializer
    
    @action(detail=False, methods=['post'])
    def get_or_create(self, request):
        """获取或创建用户"""
        telegram_id = request.data.get('telegram_id')
        if not telegram_id:
            return Response(
                {'error': 'telegram_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user, created = TelegramUser.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={
                'username': request.data.get('username'),
                'first_name': request.data.get('first_name'),
                'last_name': request.data.get('last_name'),
            }
        )
        
        serializer = self.get_serializer(user)
        return Response(serializer.data)


class LotteryViewSet(viewsets.ModelViewSet):
    """抽奖视图集"""
    queryset = Lottery.objects.all().select_related('creator').prefetch_related(
        'participations__user', 'winners__user'
    )
    
    def get_serializer_class(self):
        """根据操作返回不同的序列化器"""
        if self.action == 'list':
            return LotteryListSerializer
        elif self.action == 'create':
            return LotteryCreateSerializer
        return LotteryDetailSerializer
    
    def perform_create(self, serializer):
        """创建抽奖时设置状态为 active"""
        serializer.save(status='active')
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """获取进行中的抽奖"""
        now = timezone.now()
        lotteries = self.queryset.filter(
            status='active',
            start_time__lte=now,
            end_time__gte=now
        )
        serializer = LotteryListSerializer(lotteries, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def participate(self, request, pk=None):
        """参与抽奖"""
        lottery = self.get_object()
        telegram_id = request.data.get('telegram_id')
        
        if not telegram_id:
            return Response(
                {'error': 'telegram_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 检查是否可以参与
        if not lottery.can_participate:
            return Response(
                {'error': '抽奖已结束或人数已满'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = TelegramUser.objects.get(telegram_id=telegram_id)
        except TelegramUser.DoesNotExist:
            return Response(
                {'error': '用户不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 检查是否已参与
        if Participation.objects.filter(lottery=lottery, user=user).exists():
            return Response(
                {'error': '您已经参与过此抽奖'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 创建参与记录
        participation = Participation.objects.create(lottery=lottery, user=user)
        serializer = ParticipationSerializer(participation)
        
        return Response({
            'message': '参与成功',
            'participation': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def draw(self, request, pk=None):
        """执行开奖"""
        lottery = self.get_object()
        
        if lottery.status != 'active':
            return Response(
                {'error': '抽奖未进行中'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 执行开奖
        success = lottery.draw_winners()
        
        if success:
            # 获取中奖者
            winners = lottery.winners.all()
            serializer = WinnerSerializer(winners, many=True)
            
            return Response({
                'message': '开奖成功',
                'winners': serializer.data
            })
        else:
            return Response(
                {'error': '开奖失败'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """统计数据"""
        total_lotteries = Lottery.objects.count()
        active_lotteries = Lottery.objects.filter(status='active').count()
        finished_lotteries = Lottery.objects.filter(status='finished').count()
        total_participants = Participation.objects.count()
        total_winners = Winner.objects.count()
        
        return Response({
            'total_lotteries': total_lotteries,
            'active_lotteries': active_lotteries,
            'finished_lotteries': finished_lotteries,
            'total_participants': total_participants,
            'total_winners': total_winners
        })


class ParticipationViewSet(viewsets.ReadOnlyModelViewSet):
    """参与记录视图集（只读）"""
    queryset = Participation.objects.all().select_related('lottery', 'user')
    serializer_class = ParticipationSerializer
    
    @action(detail=False, methods=['get'])
    def my_participations(self, request):
        """获取我的参与记录"""
        telegram_id = request.query_params.get('telegram_id')
        if not telegram_id:
            return Response(
                {'error': 'telegram_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = TelegramUser.objects.get(telegram_id=telegram_id)
            participations = self.queryset.filter(user=user)
            serializer = self.get_serializer(participations, many=True)
            return Response(serializer.data)
        except TelegramUser.DoesNotExist:
            return Response(
                {'error': '用户不存在'},
                status=status.HTTP_404_NOT_FOUND
            )


class WinnerViewSet(viewsets.ReadOnlyModelViewSet):
    """中奖记录视图集（只读）"""
    queryset = Winner.objects.all().select_related('lottery', 'user')
    serializer_class = WinnerSerializer
    
    @action(detail=False, methods=['get'])
    def my_wins(self, request):
        """获取我的中奖记录"""
        telegram_id = request.query_params.get('telegram_id')
        if not telegram_id:
            return Response(
                {'error': 'telegram_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = TelegramUser.objects.get(telegram_id=telegram_id)
            winners = self.queryset.filter(user=user)
            serializer = self.get_serializer(winners, many=True)
            return Response(serializer.data)
        except TelegramUser.DoesNotExist:
            return Response(
                {'error': '用户不存在'},
                status=status.HTTP_404_NOT_FOUND
            )

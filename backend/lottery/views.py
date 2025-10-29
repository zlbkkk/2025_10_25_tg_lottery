"""
Django REST Framework 视图
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.db.models import Count
from .models import TelegramUser, Lottery, Participation, Winner
from .serializers import (
    TelegramUserSerializer,
    LotteryListSerializer,
    LotteryDetailSerializer,
    LotteryCreateSerializer,
    ParticipationSerializer,
    ParticipationWithLotterySerializer,
    WinnerSerializer
)


class LotteryPagination(PageNumberPagination):
    """抽奖列表分页器"""
    page_size = 10  # 每页10条
    page_size_query_param = 'page_size'
    max_page_size = 100


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
    queryset = Lottery.objects.all().select_related('admin_user').prefetch_related(
        'participations__user', 'winners__user', 'prizes'
    )
    parser_classes = [JSONParser, MultiPartParser, FormParser]  # 支持 JSON 和文件上传
    pagination_class = LotteryPagination  # 使用自定义分页器
    permission_classes = [IsAuthenticated]  # 需要登录
    
    def get_queryset(self):
        """
        数据隔离：只返回当前登录用户创建的抽奖
        自定义排序：进行中 > 已结束 > 已作废，每组内按创建时间倒序
        """
        from django.db.models import Case, When, IntegerField
        
        queryset = super().get_queryset()
        
        # 多租户数据隔离：只查询当前用户的数据
        if self.request.user.is_authenticated:
            queryset = queryset.filter(admin_user=self.request.user)
        
        # 只对列表操作进行自定义排序
        if self.action == 'list':
            queryset = queryset.annotate(
                status_order=Case(
                    When(status='active', then=1),
                    When(status='finished', then=2),
                    When(status='cancelled', then=3),
                    default=4,
                    output_field=IntegerField()
                )
            ).order_by('status_order', '-created_at')
        
        return queryset
    
    def get_serializer_class(self):
        """根据操作返回不同的序列化器"""
        if self.action == 'list':
            return LotteryListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return LotteryCreateSerializer
        return LotteryDetailSerializer
    
    def create(self, request, *args, **kwargs):
        """创建抽奖（处理 FormData 中的 JSON 字符串）"""
        import json
        
        print("[DEBUG] ====== 创建抽奖 ======")
        print(f"[DEBUG] Content-Type: {request.content_type}")
        print(f"[DEBUG] 原始 prizes 类型: {type(request.data.get('prizes'))}")
        
        # 将 QueryDict 转换为普通字典
        data = {}
        for key in request.data:
            value = request.data[key]
            data[key] = value
        
        if 'prizes' in data and isinstance(data.get('prizes'), str):
            try:
                data['prizes'] = json.loads(data['prizes'])
                print(f"[DEBUG] 解析后 prizes 数量: {len(data['prizes'])}")
                for i, prize in enumerate(data['prizes']):
                    print(f"[DEBUG] Prize {i+1}: {prize['name']} (level: {prize['level']})")
            except json.JSONDecodeError as e:
                print(f"[DEBUG] JSON解析失败: {e}")
                return Response(
                    {'error': '奖品数据格式错误'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # 使用处理后的数据创建序列化器
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, *args, **kwargs):
        """更新抽奖（处理 FormData 中的 JSON 字符串）"""
        import json
        
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        print("[DEBUG] ====== 更新抽奖 ======")
        
        # 将 QueryDict 转换为普通字典
        data = {}
        for key in request.data:
            value = request.data[key]
            data[key] = value
        
        if 'prizes' in data and isinstance(data.get('prizes'), str):
            try:
                data['prizes'] = json.loads(data['prizes'])
                print(f"[DEBUG] 解析后 prizes 数量: {len(data['prizes'])}")
            except json.JSONDecodeError:
                return Response(
                    {'error': '奖品数据格式错误'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # 使用处理后的数据更新序列化器
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        
        return Response(serializer.data)
    
    def perform_create(self, serializer):
        """创建抽奖时设置状态为 active，并自动设置管理员为当前用户"""
        serializer.save(status='active', admin_user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """获取进行中的抽奖（排除已结束和已作废）"""
        from datetime import datetime
        now = datetime.now()
        lotteries = self.queryset.filter(
            status='active',
            start_time__lte=now,
            end_time__gte=now
        ).exclude(
            status__in=['finished', 'cancelled']
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
    
    @action(detail=True, methods=['get'])
    def participants(self, request, pk=None):
        """获取抽奖的参与者列表"""
        lottery = self.get_object()
        
        # 获取所有参与者
        participations = Participation.objects.filter(lottery=lottery).select_related('user')
        
        # 构造参与者数据
        participants_data = []
        for participation in participations:
            participants_data.append({
                'id': participation.user.id,
                'telegram_id': participation.user.telegram_id,
                'username': participation.user.username,
                'first_name': participation.user.first_name,
                'last_name': participation.user.last_name,
                'display_name': participation.user.get_display_name(),
                'participated_at': participation.participated_at
            })
        
        return Response({
            'total': len(participants_data),
            'participants': participants_data
        })
    
    @action(detail=True, methods=['post'])
    def manual_draw(self, request, pk=None):
        """手动指定中奖人 - 按奖品等级依次分配"""
        lottery = self.get_object()
        
        if lottery.status != 'active':
            return Response(
                {'error': '抽奖未进行中'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 检查是否超过结束时间
        from datetime import datetime
        now = datetime.now()
        end_time = lottery.end_time
        
        # 兼容旧数据：转换aware datetime为naive
        if timezone.is_aware(end_time):
            end_time = timezone.make_naive(end_time)
        
        if now > end_time:
            return Response(
                {'error': '抽奖已结束，无法手动开奖'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 获取要指定的中奖人ID列表
        winner_ids = request.data.get('winner_ids', [])
        if not winner_ids:
            return Response(
                {'error': '请选择至少一个中奖人'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 获取所有奖品（按等级排序）
        prizes = lottery.prizes.all().order_by('level')
        if not prizes.exists():
            return Response(
                {'error': '该抽奖没有配置奖品'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 计算总的中奖名额
        total_winner_slots = sum(prize.winner_count for prize in prizes)
        
        # 验证选择的人数是否超过总名额
        if len(winner_ids) > total_winner_slots:
            return Response(
                {'error': f'选择的中奖人数({len(winner_ids)})不能超过总中奖名额({total_winner_slots})'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 验证所有ID是否都是该抽奖的参与者
        participations = Participation.objects.filter(
            lottery=lottery,
            user__id__in=winner_ids
        )
        
        if participations.count() != len(winner_ids):
            return Response(
                {'error': '选择的用户中包含未参与此抽奖的用户'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 清除之前的中奖记录（如果有）
        Winner.objects.filter(lottery=lottery).delete()
        
        # 按照奖品等级依次分配中奖人
        winners = []
        winner_index = 0
        
        for prize in prizes:
            # 为当前奖品分配中奖人
            for _ in range(prize.winner_count):
                if winner_index >= len(winner_ids):
                    break  # 如果没有更多的中奖人，结束分配
                
                user_id = winner_ids[winner_index]
                user = TelegramUser.objects.get(id=user_id)
                
                winner = Winner.objects.create(
                    lottery=lottery,
                    prize=prize,
                    user=user,
                    prize_name=prize.name  # 向后兼容
                )
                winners.append(winner)
                winner_index += 1
            
            if winner_index >= len(winner_ids):
                break  # 所有选中的人都已分配完毕
        
        # 更新抽奖状态
        lottery.status = 'finished'
        lottery.manual_drawn = True
        lottery.save()
        
        # 发送中奖通知
        winner_data = [(winner.user, winner.prize) for winner in winners]
        lottery._send_winner_notifications_multi_prize(winner_data)
        
        # 返回结果
        serializer = WinnerSerializer(winners, many=True)
        return Response({
            'message': f'手动指定开奖成功！共{len(winners)}人中奖',
            'winners': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def draw(self, request, pk=None):
        """随机开奖"""
        lottery = self.get_object()
        
        if lottery.status != 'active':
            return Response(
                {'error': '抽奖未进行中'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 检查是否超过结束时间
        from datetime import datetime
        now = datetime.now()
        end_time = lottery.end_time
        
        # 兼容旧数据：转换aware datetime为naive
        if timezone.is_aware(end_time):
            end_time = timezone.make_naive(end_time)
        
        if now > end_time:
            return Response(
                {'error': '抽奖已结束，无法手动开奖'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 标记为手动开奖并执行
        lottery.manual_drawn = True
        lottery.save()
        
        if lottery.draw_winners():
            winners = lottery.winners.all()
            serializer = WinnerSerializer(winners, many=True)
            return Response({
                'message': '随机开奖成功',
                'winners': serializer.data
            })
        else:
            return Response(
                {'error': '开奖失败'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """作废抽奖"""
        lottery = self.get_object()
        
        if lottery.status == 'finished':
            return Response(
                {'error': '已结束的抽奖不能作废'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if lottery.status == 'cancelled':
            return Response(
                {'error': '抽奖已经作废'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 设置状态为作废
        lottery.status = 'cancelled'
        lottery.save()
        
        return Response({
            'message': '作废成功'
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        统计数据 - 多租户隔离
        只统计当前登录用户的抽奖数据
        """
        # 获取当前用户的抽奖
        user_lotteries = Lottery.objects.filter(admin_user=request.user)
        
        # 统计抽奖数量
        total_lotteries = user_lotteries.count()
        active_lotteries = user_lotteries.filter(status='active').count()
        finished_lotteries = user_lotteries.filter(status='finished').count()
        
        # 统计参与人数（基于用户的抽奖）
        total_participants = Participation.objects.filter(lottery__admin_user=request.user).count()
        
        # 统计中奖人数（基于用户的抽奖）
        total_winners = Winner.objects.filter(lottery__admin_user=request.user).count()
        
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
        """获取我的参与记录（包含抽奖详情）"""
        telegram_id = request.query_params.get('telegram_id')
        if not telegram_id:
            return Response(
                {'error': 'telegram_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = TelegramUser.objects.get(telegram_id=telegram_id)
            participations = self.queryset.filter(user=user)
            # 使用包含抽奖信息的序列化器
            serializer = ParticipationWithLotterySerializer(participations, many=True)
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

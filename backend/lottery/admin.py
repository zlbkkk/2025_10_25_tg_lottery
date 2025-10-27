"""
Django Admin 配置
"""
from django.contrib import admin
from .models import TelegramUser, Lottery, Prize, Participation, Winner


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ['telegram_id', 'username', 'first_name', 'last_name', 'created_at']
    search_fields = ['telegram_id', 'username', 'first_name']
    list_filter = ['created_at']
    readonly_fields = ['created_at', 'updated_at']


class PrizeInline(admin.TabularInline):
    """奖品内联编辑（在抽奖详情页显示）"""
    model = Prize
    extra = 1
    fields = ['name', 'description', 'winner_count', 'level']


@admin.register(Lottery)
class LotteryAdmin(admin.ModelAdmin):
    list_display = ['title', 'prize_name', 'prize_count', 'status', 'creator', 'participant_count', 'start_time', 'end_time']
    search_fields = ['title', 'prize_name', 'description']
    list_filter = ['status', 'created_at']
    readonly_fields = ['created_at', 'updated_at', 'participant_count', 'winner_count']
    date_hierarchy = 'created_at'
    inlines = [PrizeInline]  # 添加奖品内联编辑
    
    fieldsets = (
        ('基本信息', {
            'fields': ('creator', 'title', 'description')
        }),
        ('旧奖品信息（兼容）', {
            'fields': ('prize_name', 'prize_count', 'prize_image'),
            'classes': ('collapse',)  # 默认折叠
        }),
        ('活动设置', {
            'fields': ('max_participants', 'start_time', 'end_time', 'status')
        }),
        ('统计信息', {
            'fields': ('participant_count', 'winner_count', 'created_at', 'updated_at')
        }),
    )


@admin.register(Prize)
class PrizeAdmin(admin.ModelAdmin):
    list_display = ['lottery', 'name', 'winner_count', 'level', 'winner_list_count', 'created_at']
    search_fields = ['name', 'lottery__title']
    list_filter = ['level', 'created_at']
    readonly_fields = ['created_at', 'winner_list_count']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('lottery', 'name', 'description', 'image')
        }),
        ('设置', {
            'fields': ('winner_count', 'level')
        }),
        ('统计', {
            'fields': ('winner_list_count', 'created_at')
        }),
    )


@admin.register(Participation)
class ParticipationAdmin(admin.ModelAdmin):
    list_display = ['lottery', 'user', 'participated_at']
    search_fields = ['lottery__title', 'user__username']
    list_filter = ['participated_at']
    readonly_fields = ['participated_at']


@admin.register(Winner)
class WinnerAdmin(admin.ModelAdmin):
    list_display = ['lottery', 'user', 'get_prize_display', 'won_at', 'claimed']
    search_fields = ['lottery__title', 'user__username', 'prize_name', 'prize__name']
    list_filter = ['claimed', 'won_at']
    readonly_fields = ['won_at']
    
    def get_prize_display(self, obj):
        """显示奖品名称"""
        return obj.prize.name if obj.prize else obj.prize_name
    get_prize_display.short_description = '奖品'

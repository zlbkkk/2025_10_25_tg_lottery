"""
Django Admin 配置
"""
from django.contrib import admin
from .models import TelegramUser, Lottery, Participation, Winner


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ['telegram_id', 'username', 'first_name', 'last_name', 'created_at']
    search_fields = ['telegram_id', 'username', 'first_name']
    list_filter = ['created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Lottery)
class LotteryAdmin(admin.ModelAdmin):
    list_display = ['title', 'prize_name', 'prize_count', 'status', 'creator', 'participant_count', 'start_time', 'end_time']
    search_fields = ['title', 'prize_name', 'description']
    list_filter = ['status', 'created_at']
    readonly_fields = ['created_at', 'updated_at', 'participant_count', 'winner_count']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('基本信息', {
            'fields': ('creator', 'title', 'description')
        }),
        ('奖品信息', {
            'fields': ('prize_name', 'prize_count', 'prize_image')
        }),
        ('活动设置', {
            'fields': ('max_participants', 'start_time', 'end_time', 'status')
        }),
        ('统计信息', {
            'fields': ('participant_count', 'winner_count', 'created_at', 'updated_at')
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
    list_display = ['lottery', 'user', 'prize_name', 'won_at', 'claimed']
    search_fields = ['lottery__title', 'user__username', 'prize_name']
    list_filter = ['claimed', 'won_at']
    readonly_fields = ['won_at']

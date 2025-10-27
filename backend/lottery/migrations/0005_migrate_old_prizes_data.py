# Generated manually for data migration
from django.db import migrations


def migrate_old_lottery_prizes(apps, schema_editor):
    """
    将旧的抽奖数据（prize_name, prize_count）迁移到新的Prize模型
    """
    Lottery = apps.get_model('lottery', 'Lottery')
    Prize = apps.get_model('lottery', 'Prize')
    Winner = apps.get_model('lottery', 'Winner')
    
    # 遍历所有抽奖活动
    for lottery in Lottery.objects.all():
        # 如果该抽奖还没有创建Prize（旧数据）
        if not lottery.prizes.exists():
            # 创建一个Prize，使用原来的prize_name和prize_count
            prize = Prize.objects.create(
                lottery=lottery,
                name=lottery.prize_name,
                description=f"从旧数据迁移：{lottery.prize_name}",
                winner_count=lottery.prize_count,
                level=1
            )
            
            # 将该抽奖的所有Winner关联到这个新创建的Prize
            Winner.objects.filter(lottery=lottery, prize__isnull=True).update(prize=prize)


def reverse_migration(apps, schema_editor):
    """回滚操作"""
    # 删除所有自动创建的Prize（可选）
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('lottery', '0004_auto_20251026_1401'),
    ]

    operations = [
        migrations.RunPython(migrate_old_lottery_prizes, reverse_migration),
    ]

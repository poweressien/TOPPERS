from django.contrib import admin
from django.utils import timezone
from .models import PointTransaction, Achievement, UserAchievement, AirtimeRedemption


@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'transaction_type', 'balance_after', 'created_at']
    list_filter = ['transaction_type']
    search_fields = ['user__username', 'description']
    readonly_fields = ['id', 'created_at']
    ordering = ['-created_at']


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['badge_emoji', 'name', 'achievement_type', 'threshold', 'points_reward', 'is_active']
    list_filter = ['achievement_type', 'is_active']


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ['user', 'achievement', 'earned_at']
    list_filter = ['achievement']
    search_fields = ['user__username']


@admin.register(AirtimeRedemption)
class AirtimeRedemptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'network', 'phone_number', 'naira_value', 'points_used', 'status', 'created_at']
    list_filter = ['status', 'network']
    search_fields = ['user__username', 'phone_number']
    readonly_fields = ['id', 'created_at', 'user', 'points_used', 'naira_value']
    actions = ['approve_redemptions', 'reject_redemptions']

    def approve_redemptions(self, request, queryset):
        updated = queryset.filter(status='pending').update(
            status='approved', processed_at=timezone.now()
        )
        self.message_user(request, f'{updated} redemptions approved.')
    approve_redemptions.short_description = 'Approve selected redemptions'

    def reject_redemptions(self, request, queryset):
        for redemption in queryset.filter(status='pending'):
            # Refund points
            user = redemption.user
            user.total_points += redemption.points_used
            user.save(update_fields=['total_points'])
            PointTransaction.objects.create(
                user=user,
                amount=redemption.points_used,
                transaction_type='admin_credit',
                description=f'Refund for rejected redemption #{redemption.id}',
                balance_after=user.total_points,
            )
            redemption.status = 'rejected'
            redemption.processed_at = timezone.now()
            redemption.save()
        self.message_user(request, f'Redemptions rejected and points refunded.')
    reject_redemptions.short_description = 'Reject and refund selected redemptions'

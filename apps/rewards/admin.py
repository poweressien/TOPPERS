from django.contrib import admin
from django.utils import timezone
from .models import PointTransaction, Achievement, UserAchievement, WithdrawalRequest


@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    list_display  = ['user', 'amount', 'transaction_type', 'balance_after', 'created_at']
    list_filter   = ['transaction_type']
    search_fields = ['user__username', 'description']
    readonly_fields = ['id', 'created_at']
    ordering = ['-created_at']


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['badge_emoji', 'name', 'achievement_type', 'threshold', 'points_reward', 'is_active']
    list_filter  = ['achievement_type', 'is_active']


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display  = ['user', 'achievement', 'earned_at']
    list_filter   = ['achievement']
    search_fields = ['user__username']


@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display  = [
        'reference', 'user', 'amount_requested', 'fee_amount',
        'amount_to_receive', 'bank_display', 'account_number',
        'account_name', 'status', 'created_at',
    ]
    list_filter   = ['status', 'bank_name']
    search_fields = ['user__username', 'account_number', 'account_name', 'reference']
    readonly_fields = [
        'id', 'reference', 'user', 'amount_requested', 'fee_amount',
        'amount_to_receive', 'points_deducted', 'created_at',
    ]
    ordering = ['-created_at']

    fieldsets = (
        ('Request Details', {
            'fields': ('reference', 'user', 'status')
        }),
        ('Amount Breakdown', {
            'fields': ('amount_requested', 'fee_amount', 'amount_to_receive', 'points_deducted')
        }),
        ('Bank Details', {
            'fields': ('bank_name', 'account_number', 'account_name')
        }),
        ('Admin Notes', {
            'fields': ('admin_notes', 'rejection_reason', 'processed_at')
        }),
    )

    actions = ['approve_withdrawals', 'mark_completed', 'reject_withdrawals']

    def approve_withdrawals(self, request, queryset):
        updated = queryset.filter(status='pending').update(
            status='approved', processed_at=timezone.now()
        )
        self.message_user(request, f'{updated} withdrawal(s) approved.')
    approve_withdrawals.short_description = '✅ Approve selected withdrawals'

    def mark_completed(self, request, queryset):
        updated = queryset.filter(status__in=['approved', 'processing']).update(
            status='completed', processed_at=timezone.now()
        )
        self.message_user(request, f'{updated} withdrawal(s) marked as completed.')
    mark_completed.short_description = '✔️ Mark selected as Completed'

    def reject_withdrawals(self, request, queryset):
        """Reject and refund points to user."""
        count = 0
        for wd in queryset.filter(status__in=['pending', 'approved']):
            # Refund points
            user = wd.user
            user.total_points += wd.points_deducted
            user.save(update_fields=['total_points'])
            PointTransaction.objects.create(
                user=user,
                amount=wd.points_deducted,
                transaction_type=PointTransaction.TYPE_ADMIN_CREDIT,
                description=f'Refund for rejected withdrawal {wd.reference}',
                balance_after=user.total_points,
            )
            # Update withdrawal
            wd.status = 'rejected'
            wd.processed_at = timezone.now()
            wd.rejection_reason = wd.rejection_reason or 'Rejected by admin.'
            wd.save()
            count += 1

            # Reverse total_withdrawn_naira
            user.total_withdrawn_naira = max(
                0, float(user.total_withdrawn_naira or 0) - float(wd.amount_to_receive)
            )
            user.save(update_fields=['total_withdrawn_naira'])

            try:
                from apps.notifications.utils import send_notification
                send_notification(
                    user,
                    'Withdrawal Rejected',
                    f'Your withdrawal of ₦{wd.amount_to_receive} (Ref: {wd.reference}) '
                    f'was rejected. {wd.points_deducted:,} pts refunded to your account.',
                    'reward',
                )
            except Exception:
                pass

        self.message_user(request, f'{count} withdrawal(s) rejected. Points refunded.')
    reject_withdrawals.short_description = '❌ Reject selected & refund points'

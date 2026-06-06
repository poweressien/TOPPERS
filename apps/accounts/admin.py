from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, ReferralReward, EmailVerificationToken


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'country', 'total_points', 'level', 'current_streak', 'is_email_verified', 'date_joined']
    list_filter = ['level', 'country', 'is_email_verified', 'is_staff', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    readonly_fields = ['id', 'referral_code', 'total_points', 'total_xp', 'date_joined']

    fieldsets = UserAdmin.fieldsets + (
        ('Profile', {'fields': ('avatar', 'bio', 'country', 'phone_number', 'is_email_verified', 'google_id')}),
        ('Points & Level', {'fields': ('total_points', 'total_xp', 'level')}),
        ('Referral', {'fields': ('referral_code', 'referred_by')}),
        ('Streak & Daily', {'fields': ('current_streak', 'longest_streak', 'last_login_date', 'daily_games_played', 'last_game_reset')}),
        ('Stats', {'fields': ('total_games_played', 'total_correct_answers', 'total_wrong_answers', 'total_challenges_won', 'total_airtime_earned')}),
    )


@admin.register(ReferralReward)
class ReferralRewardAdmin(admin.ModelAdmin):
    list_display = ['referrer', 'referred_user', 'points_awarded', 'bonus_naira', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['referrer__username', 'referred_user__username']
    actions = ['mark_as_paid']

    def mark_as_paid(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(status='pending').update(status='paid', paid_at=timezone.now())
        self.message_user(request, f'{updated} referral rewards marked as paid.')
    mark_as_paid.short_description = 'Mark selected rewards as paid'


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'expires_at', 'is_used']
    list_filter = ['is_used']

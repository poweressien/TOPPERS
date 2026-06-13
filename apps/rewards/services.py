"""
Reward Services — points, earnings cap, withdrawal logic, achievements.
"""
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from django.db.models import Sum
from .models import PointTransaction, Achievement, UserAchievement

GAME_CONFIG = settings.GAME_CONFIG


class EarningsCapService:
    """Enforce the weekly ₦2,000 earning cap."""

    @staticmethod
    def get_week_start():
        today = timezone.localdate()
        return today - timezone.timedelta(days=today.weekday())  # Monday

    @staticmethod
    def get_weekly_earned_naira(user):
        """How much Naira value the user has earned THIS week."""
        week_start = EarningsCapService.get_week_start()
        earned_pts = PointTransaction.objects.filter(
            user=user,
            amount__gt=0,
            transaction_type__in=[
                PointTransaction.TYPE_EARNED_GAME,
                PointTransaction.TYPE_CHALLENGE_WIN,
            ],
            created_at__date__gte=week_start,
        ).aggregate(total=Sum('amount'))['total'] or 0

        rate = GAME_CONFIG['POINTS_TO_NAIRA_RATE']
        return round(earned_pts * rate, 2)

    @staticmethod
    def can_earn(user, points_to_add):
        """Check if adding these points would exceed the weekly cap."""
        rate = GAME_CONFIG['POINTS_TO_NAIRA_RATE']
        naira_value = points_to_add * rate
        already_earned = EarningsCapService.get_weekly_earned_naira(user)
        cap = GAME_CONFIG['MAX_WEEKLY_EARN_NAIRA']
        return (already_earned + naira_value) <= cap

    @staticmethod
    def get_remaining_earnable(user):
        """How much more the user can earn this week in Naira."""
        cap = GAME_CONFIG['MAX_WEEKLY_EARN_NAIRA']
        earned = EarningsCapService.get_weekly_earned_naira(user)
        remaining_naira = max(0, cap - earned)
        rate = GAME_CONFIG['POINTS_TO_NAIRA_RATE']
        remaining_points = int(remaining_naira / rate) if rate > 0 else 0
        return {
            'remaining_naira': remaining_naira,
            'remaining_points': remaining_points,
            'earned_naira': earned,
            'cap_naira': cap,
            'percent_used': round((earned / cap) * 100, 1) if cap > 0 else 0,
        }


class WithdrawalEligibilityService:
    """Check if user can make a withdrawal."""

    @staticmethod
    def get_week_withdrawals(user):
        """Count withdrawals made this week."""
        from .models import WithdrawalRequest
        week_start = EarningsCapService.get_week_start()
        return WithdrawalRequest.objects.filter(
            user=user,
            created_at__date__gte=week_start,
            status__in=[
                WithdrawalRequest.STATUS_PENDING,
                WithdrawalRequest.STATUS_APPROVED,
                WithdrawalRequest.STATUS_PROCESSING,
                WithdrawalRequest.STATUS_COMPLETED,
            ]
        ).count()

    @staticmethod
    def check_eligibility(user, amount_naira):
        """
        Returns (is_eligible: bool, reason: str).
        """
        from .models import WithdrawalRequest
        cfg = GAME_CONFIG
        min_wd = cfg['MIN_WITHDRAWAL_NAIRA']
        max_per_week = cfg['MAX_WEEKLY_WITHDRAWALS']

        # 1. Minimum amount
        if amount_naira < min_wd:
            return False, f'Minimum withdrawal is ₦{min_wd:,}.'

        # 2. Sufficient points
        rate = cfg['POINTS_TO_NAIRA_RATE']
        points_needed = int(amount_naira / rate)
        if user.total_points < points_needed:
            return False, f'Insufficient points. You need {points_needed:,} pts for ₦{amount_naira:,}.'

        # 3. Weekly withdrawal limit
        used_this_week = WithdrawalEligibilityService.get_week_withdrawals(user)
        if used_this_week >= max_per_week:
            return False, f'Weekly limit reached. You can only withdraw {max_per_week}x per week.'

        return True, 'Eligible'


class PointsService:
    """All point operations with earning cap enforcement."""

    @staticmethod
    def add_points(user, amount, transaction_type, description='', session=None, enforce_cap=False):
        """Add points to a user. If enforce_cap=True, cap points to weekly limit."""
        if enforce_cap and transaction_type in [
            PointTransaction.TYPE_EARNED_GAME,
            PointTransaction.TYPE_CHALLENGE_WIN,
        ]:
            cap_info = EarningsCapService.get_remaining_earnable(user)
            max_points = cap_info['remaining_points']
            if max_points <= 0:
                return 0  # Cap reached — no points awarded
            amount = min(amount, max_points)  # Cap the points

        if amount <= 0:
            return 0

        user.add_points(amount, save=True)
        PointTransaction.objects.create(
            user=user,
            amount=amount,
            transaction_type=transaction_type,
            description=description,
            balance_after=user.total_points,
            game_session=session,
        )
        return amount

    @staticmethod
    def deduct_points(user, amount, transaction_type, description=''):
        """Deduct points (for withdrawals)."""
        user.deduct_points(amount, save=True)
        PointTransaction.objects.create(
            user=user,
            amount=-amount,
            transaction_type=transaction_type,
            description=description,
            balance_after=user.total_points,
        )

    @staticmethod
    def award_daily_login_bonus(user):
        """Award daily login bonus — once per day."""
        today = timezone.localdate()
        already = PointTransaction.objects.filter(
            user=user,
            transaction_type=PointTransaction.TYPE_DAILY_BONUS,
            created_at__date=today,
        ).exists()
        if already:
            return None

        base = GAME_CONFIG['DAILY_LOGIN_BONUS']
        streak = user.current_streak
        if streak >= 30:
            bonus = int(base * 3.0)
        elif streak >= 14:
            bonus = int(base * 2.0)
        elif streak >= 7:
            bonus = int(base * 1.5)
        else:
            bonus = base

        PointsService.add_points(
            user=user, amount=bonus,
            transaction_type=PointTransaction.TYPE_DAILY_BONUS,
            description=f'Daily login bonus – {streak} day streak',
        )
        return bonus

    @staticmethod
    def award_referral_bonus(referrer, referred_user):
        """Award referral bonus to referrer."""
        bonus = GAME_CONFIG['REFERRAL_BONUS_POINTS']
        PointsService.add_points(
            user=referrer, amount=bonus,
            transaction_type=PointTransaction.TYPE_REFERRAL_BONUS,
            description=f'{referred_user.username} joined using your referral code',
        )
        from apps.accounts.models import ReferralReward
        ReferralReward.objects.filter(
            referrer=referrer, referred_user=referred_user
        ).update(status='paid', paid_at=timezone.now(), points_awarded=bonus)

    @staticmethod
    def process_withdrawal(user, amount_naira, bank_name, account_number, account_name):
        """
        Deduct points and create a withdrawal request.
        Returns (WithdrawalRequest, error_message).
        """
        from .models import WithdrawalRequest

        eligible, reason = WithdrawalEligibilityService.check_eligibility(user, amount_naira)
        if not eligible:
            return None, reason

        cfg = GAME_CONFIG
        rate = cfg['POINTS_TO_NAIRA_RATE']
        fee_pct = cfg['WITHDRAWAL_FEE_PERCENT']

        points_needed = int(amount_naira / rate)
        fee = round(Decimal(str(amount_naira)) * Decimal(str(fee_pct)) / 100, 2)
        amount_to_receive = round(Decimal(str(amount_naira)) - fee, 2)

        # Deduct points
        PointsService.deduct_points(
            user=user,
            amount=points_needed,
            transaction_type=PointTransaction.TYPE_WITHDRAWN,
            description=f'Withdrawal ₦{amount_naira} to {bank_name} {account_number}',
        )

        # Update user's total withdrawn
        user.total_withdrawn_naira = float(
            (Decimal(str(user.total_withdrawn_naira or 0)) + amount_to_receive)
        )
        user.save(update_fields=['total_withdrawn_naira'])

        wd = WithdrawalRequest.objects.create(
            user=user,
            amount_requested=Decimal(str(amount_naira)),
            fee_amount=fee,
            amount_to_receive=amount_to_receive,
            points_deducted=points_needed,
            bank_name=bank_name,
            account_number=account_number,
            account_name=account_name,
        )
        return wd, None


class AchievementService:
    RULES = [
        {'name': 'First Win', 'description': 'Complete your first game.', 'badge_emoji': '🎉', 'type': 'games', 'threshold': 1, 'check': lambda u: u.total_games_played >= 1},
        {'name': '7-Day Streak', 'description': 'Play 7 days in a row.', 'badge_emoji': '🔥', 'type': 'streak', 'threshold': 7, 'check': lambda u: u.current_streak >= 7},
        {'name': '30-Day Streak', 'description': '30 days straight!', 'badge_emoji': '🌟', 'type': 'streak', 'threshold': 30, 'check': lambda u: u.current_streak >= 30},
        {'name': 'Sharp Shooter', 'description': '90%+ accuracy across 10 games.', 'badge_emoji': '🎯', 'type': 'accuracy', 'threshold': 90, 'check': lambda u: u.total_games_played >= 10 and u.accuracy_rate >= 90},
        {'name': 'Century Player', 'description': 'Play 100 games.', 'badge_emoji': '💯', 'type': 'games', 'threshold': 100, 'check': lambda u: u.total_games_played >= 100},
        {'name': 'First Cashout', 'description': 'Make your first withdrawal.', 'badge_emoji': '💸', 'type': 'special', 'threshold': 1, 'check': lambda u: getattr(u, 'total_withdrawn_naira', 0) > 0},
        {'name': 'Top Referrer', 'description': 'Refer 10 users.', 'badge_emoji': '🤝', 'type': 'referral', 'threshold': 10, 'check': lambda u: u.referrals.count() >= 10},
        {'name': 'Challenge Champion', 'description': 'Win 25 live challenges.', 'badge_emoji': '⚔️', 'type': 'games', 'threshold': 25, 'check': lambda u: u.total_challenges_won >= 25},
        {'name': 'Legend', 'description': 'Reach Legend level.', 'badge_emoji': '👑', 'type': 'level', 'threshold': 6, 'check': lambda u: u.level >= 6},
    ]

    @classmethod
    def ensure_achievements_exist(cls):
        for rule in cls.RULES:
            Achievement.objects.get_or_create(
                name=rule['name'],
                defaults={
                    'description': rule['description'],
                    'badge_emoji': rule.get('badge_emoji', '🏆'),
                    'achievement_type': rule['type'],
                    'threshold': rule['threshold'],
                    'points_reward': 50,
                    'is_active': True,
                }
            )

    @classmethod
    def check_and_award(cls, user):
        cls.ensure_achievements_exist()
        earned_ids = set(UserAchievement.objects.filter(user=user).values_list('achievement_id', flat=True))
        new_achievements = []
        for rule in cls.RULES:
            try:
                achievement = Achievement.objects.get(name=rule['name'], is_active=True)
            except Achievement.DoesNotExist:
                continue
            if achievement.id in earned_ids:
                continue
            try:
                unlocked = rule['check'](user)
            except Exception:
                continue
            if unlocked:
                UserAchievement.objects.create(user=user, achievement=achievement)
                new_achievements.append(achievement)
                if achievement.points_reward > 0:
                    PointsService.add_points(
                        user=user, amount=achievement.points_reward,
                        transaction_type=PointTransaction.TYPE_EVENT_BONUS,
                        description=f'Achievement unlocked: {achievement.name}',
                    )
                try:
                    from apps.notifications.utils import send_notification
                    send_notification(user, f'Achievement Unlocked: {achievement.name}', achievement.description, 'achievement')
                except Exception:
                    pass
        return new_achievements

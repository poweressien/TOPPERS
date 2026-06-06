"""
Reward Services — business logic for points and achievements.
Imported by games/views.py and other apps.
"""
from django.conf import settings
from django.utils import timezone
from .models import PointTransaction, Achievement, UserAchievement

GAME_CONFIG = settings.GAME_CONFIG


class PointsService:
    """All point-related operations."""

    @staticmethod
    def add_points(user, amount, transaction_type, description='', session=None):
        """Add points to a user and record the transaction."""
        user.add_points(amount, save=True)
        PointTransaction.objects.create(
            user=user,
            amount=amount,
            transaction_type=transaction_type,
            description=description,
            balance_after=user.total_points,
            game_session=session,
        )

    @staticmethod
    def deduct_points(user, amount, transaction_type, description=''):
        """Deduct points (e.g., airtime redemption)."""
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
        if user.last_login_date == today:
            # Check if already awarded today
            already = PointTransaction.objects.filter(
                user=user,
                transaction_type=PointTransaction.TYPE_DAILY_BONUS,
                created_at__date=today,
            ).exists()
            if already:
                return None

        base = GAME_CONFIG['DAILY_LOGIN_BONUS']

        # Streak multiplier
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
            user=user,
            amount=bonus,
            transaction_type=PointTransaction.TYPE_DAILY_BONUS,
            description=f'Daily login bonus – {streak} day streak',
        )
        return bonus

    @staticmethod
    def award_referral_bonus(referrer, referred_user):
        """Award referral bonus to the referrer."""
        bonus = GAME_CONFIG['REFERRAL_BONUS_POINTS']
        PointsService.add_points(
            user=referrer,
            amount=bonus,
            transaction_type=PointTransaction.TYPE_REFERRAL_BONUS,
            description=f'{referred_user.username} joined using your referral',
        )
        # Mark the referral reward as paid
        from apps.accounts.models import ReferralReward
        ReferralReward.objects.filter(referrer=referrer, referred_user=referred_user).update(
            status='paid', paid_at=timezone.now(), points_awarded=bonus
        )


class AchievementService:
    """Check and award achievements after game events."""

    RULES = [
        # (achievement_name, achievement_type, threshold, check_fn)
        # check_fn receives (user) and returns bool
        {
            'name': 'First Win',
            'description': 'Complete your very first game.',
            'badge_emoji': '🎉',
            'type': 'games',
            'threshold': 1,
            'check': lambda u: u.total_games_played >= 1,
        },
        {
            'name': '7-Day Streak',
            'description': 'Log in and play for 7 days in a row.',
            'badge_emoji': '🔥',
            'type': 'streak',
            'threshold': 7,
            'check': lambda u: u.current_streak >= 7,
        },
        {
            'name': '30-Day Streak',
            'description': 'Incredible — 30 days straight!',
            'badge_emoji': '🌟',
            'type': 'streak',
            'threshold': 30,
            'check': lambda u: u.current_streak >= 30,
        },
        {
            'name': 'Sharp Shooter',
            'description': 'Achieve 90%+ accuracy across 10 games.',
            'badge_emoji': '🎯',
            'type': 'accuracy',
            'threshold': 90,
            'check': lambda u: u.total_games_played >= 10 and u.accuracy_rate >= 90,
        },
        {
            'name': 'Century Player',
            'description': 'Play 100 games.',
            'badge_emoji': '💯',
            'type': 'games',
            'threshold': 100,
            'check': lambda u: u.total_games_played >= 100,
        },
        {
            'name': 'Point Millionaire',
            'description': 'Earn 1,000,000 total points.',
            'badge_emoji': '💎',
            'type': 'score',
            'threshold': 1000000,
            'check': lambda u: u.total_xp >= 1000000,
        },
        {
            'name': 'Top Referrer',
            'description': 'Refer 10 active users.',
            'badge_emoji': '🤝',
            'type': 'referral',
            'threshold': 10,
            'check': lambda u: u.referrals.count() >= 10,
        },
        {
            'name': 'Challenge Champion',
            'description': 'Win 25 live challenges.',
            'badge_emoji': '⚔️',
            'type': 'games',
            'threshold': 25,
            'check': lambda u: u.total_challenges_won >= 25,
        },
        {
            'name': 'Legend',
            'description': 'Reach Legend level (Level 6).',
            'badge_emoji': '👑',
            'type': 'level',
            'threshold': 6,
            'check': lambda u: u.level >= 6,
        },
    ]

    @classmethod
    def ensure_achievements_exist(cls):
        """Seed achievements into DB if not present."""
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
        """Check all rules, award any newly earned achievements. Returns list of new Achievement objects."""
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

            if rule['check'](user):
                UserAchievement.objects.create(user=user, achievement=achievement)
                new_achievements.append(achievement)

                # Award bonus points for unlocking
                if achievement.points_reward > 0:
                    PointsService.add_points(
                        user=user,
                        amount=achievement.points_reward,
                        transaction_type=PointTransaction.TYPE_EVENT_BONUS,
                        description=f'Achievement unlocked: {achievement.name}',
                    )

                # Send notification
                try:
                    from apps.notifications.utils import send_notification
                    send_notification(
                        user=user,
                        title=f'Achievement Unlocked: {achievement.name}',
                        message=achievement.description,
                        notification_type='achievement',
                    )
                except Exception:
                    pass

        return new_achievements

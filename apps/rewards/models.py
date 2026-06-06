import uuid
from django.db import models


class PointTransaction(models.Model):
    """Ledger of every point movement for a user."""

    TYPE_EARNED_GAME    = 'earned_game'
    TYPE_DAILY_BONUS    = 'daily_bonus'
    TYPE_STREAK_BONUS   = 'streak_bonus'
    TYPE_REFERRAL_BONUS = 'referral_bonus'
    TYPE_CHALLENGE_WIN  = 'challenge_win'
    TYPE_REDEEMED       = 'redeemed'
    TYPE_AD_BONUS       = 'ad_bonus'
    TYPE_EVENT_BONUS    = 'event_bonus'
    TYPE_ADMIN_CREDIT   = 'admin_credit'

    TYPE_CHOICES = [
        (TYPE_EARNED_GAME,    'Earned from Game'),
        (TYPE_DAILY_BONUS,    'Daily Login Bonus'),
        (TYPE_STREAK_BONUS,   'Streak Bonus'),
        (TYPE_REFERRAL_BONUS, 'Referral Bonus'),
        (TYPE_CHALLENGE_WIN,  'Challenge Win'),
        (TYPE_REDEEMED,       'Redeemed for Airtime'),
        (TYPE_AD_BONUS,       'Ad Reward'),
        (TYPE_EVENT_BONUS,    'Event Bonus'),
        (TYPE_ADMIN_CREDIT,   'Admin Credit'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='point_transactions')
    amount = models.IntegerField(help_text='Positive = credit, negative = debit')
    transaction_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    description = models.CharField(max_length=255, blank=True)
    balance_after = models.IntegerField()
    game_session = models.ForeignKey(
        'games.GameSession', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='point_transactions'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        sign = '+' if self.amount >= 0 else ''
        return f'{self.user.username} {sign}{self.amount}pts – {self.transaction_type}'


class Achievement(models.Model):
    """Platform achievements / badges."""

    TYPE_STREAK   = 'streak'
    TYPE_GAMES    = 'games'
    TYPE_SCORE    = 'score'
    TYPE_REFERRAL = 'referral'
    TYPE_ACCURACY = 'accuracy'
    TYPE_LEVEL    = 'level'
    TYPE_CATEGORY = 'category'
    TYPE_SPECIAL  = 'special'

    TYPE_CHOICES = [
        (TYPE_STREAK,   'Streak'),
        (TYPE_GAMES,    'Games Played'),
        (TYPE_SCORE,    'Score'),
        (TYPE_REFERRAL, 'Referral'),
        (TYPE_ACCURACY, 'Accuracy'),
        (TYPE_LEVEL,    'Level'),
        (TYPE_CATEGORY, 'Category'),
        (TYPE_SPECIAL,  'Special'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    badge_emoji = models.CharField(max_length=10, default='🏆')
    achievement_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    threshold = models.IntegerField(default=1, help_text='Value needed to unlock')
    points_reward = models.IntegerField(default=0, help_text='Bonus points on unlock')
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return f'{self.badge_emoji} {self.name}'


class UserAchievement(models.Model):
    """Records when a user earns an achievement."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, related_name='earned_by')
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'achievement')

    def __str__(self):
        return f'{self.user.username} – {self.achievement.name}'


class AirtimeRedemption(models.Model):
    """Airtime redemption request."""

    NETWORK_MTN    = 'mtn'
    NETWORK_AIRTEL = 'airtel'
    NETWORK_GLO    = 'glo'
    NETWORK_9MOBILE = '9mobile'

    NETWORK_CHOICES = [
        (NETWORK_MTN,     'MTN'),
        (NETWORK_AIRTEL,  'Airtel'),
        (NETWORK_GLO,     'Glo'),
        (NETWORK_9MOBILE, '9Mobile'),
    ]

    STATUS_PENDING    = 'pending'
    STATUS_APPROVED   = 'approved'
    STATUS_PROCESSING = 'processing'
    STATUS_COMPLETED  = 'completed'
    STATUS_REJECTED   = 'rejected'

    STATUS_CHOICES = [
        (STATUS_PENDING,    'Pending'),
        (STATUS_APPROVED,   'Approved'),
        (STATUS_PROCESSING, 'Processing'),
        (STATUS_COMPLETED,  'Completed'),
        (STATUS_REJECTED,   'Rejected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='airtime_redemptions')
    network = models.CharField(max_length=20, choices=NETWORK_CHOICES)
    phone_number = models.CharField(max_length=15)
    points_used = models.IntegerField()
    naira_value = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    vtpass_reference = models.CharField(max_length=100, blank=True)
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} – ₦{self.naira_value} ({self.status})'

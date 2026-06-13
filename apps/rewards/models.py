import uuid
import shortuuid
from django.db import models
from django.utils import timezone


class PointTransaction(models.Model):
    TYPE_EARNED_GAME    = 'earned_game'
    TYPE_DAILY_BONUS    = 'daily_bonus'
    TYPE_STREAK_BONUS   = 'streak_bonus'
    TYPE_REFERRAL_BONUS = 'referral_bonus'
    TYPE_CHALLENGE_WIN  = 'challenge_win'
    TYPE_WITHDRAWN      = 'withdrawn'
    TYPE_AD_BONUS       = 'ad_bonus'
    TYPE_EVENT_BONUS    = 'event_bonus'
    TYPE_ADMIN_CREDIT   = 'admin_credit'

    TYPE_CHOICES = [
        (TYPE_EARNED_GAME,    'Earned from Game'),
        (TYPE_DAILY_BONUS,    'Daily Login Bonus'),
        (TYPE_STREAK_BONUS,   'Streak Bonus'),
        (TYPE_REFERRAL_BONUS, 'Referral Bonus'),
        (TYPE_CHALLENGE_WIN,  'Challenge Win'),
        (TYPE_WITHDRAWN,      'Withdrawn to Bank'),
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
    TYPE_CHOICES = [
        ('streak',   'Streak'),
        ('games',    'Games Played'),
        ('score',    'Score'),
        ('referral', 'Referral'),
        ('accuracy', 'Accuracy'),
        ('level',    'Level'),
        ('category', 'Category'),
        ('special',  'Special'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    badge_emoji = models.CharField(max_length=10, default='🏆')
    achievement_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    threshold = models.IntegerField(default=1)
    points_reward = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return f'{self.badge_emoji} {self.name}'


class UserAchievement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, related_name='earned_by')
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'achievement')

    def __str__(self):
        return f'{self.user.username} – {self.achievement.name}'


def generate_withdrawal_ref():
    return f'TPS-{shortuuid.ShortUUID().random(length=10).upper()}'


class WithdrawalRequest(models.Model):
    """Real money withdrawal to Nigerian bank accounts."""

    BANK_CHOICES = [
        # Commercial Banks
        ('access',      'Access Bank'),
        ('citibank',    'Citibank Nigeria'),
        ('ecobank',     'Ecobank Nigeria'),
        ('fcmb',        'FCMB'),
        ('fidelity',    'Fidelity Bank'),
        ('firstbank',   'First Bank of Nigeria'),
        ('gtbank',      'Guaranty Trust Bank (GTBank)'),
        ('heritage',    'Heritage Bank'),
        ('jaiz',        'Jaiz Bank'),
        ('keystone',    'Keystone Bank'),
        ('polaris',     'Polaris Bank'),
        ('providus',    'Providus Bank'),
        ('stanbic',     'Stanbic IBTC Bank'),
        ('sterling',    'Sterling Bank'),
        ('suntrust',    'SunTrust Bank'),
        ('titan',       'Titan Bank'),
        ('uba',         'United Bank for Africa (UBA)'),
        ('union',       'Union Bank'),
        ('unity',       'Unity Bank'),
        ('wema',        'Wema Bank'),
        ('zenith',      'Zenith Bank'),
        # Microfinance / Online Banks
        ('carbon',      'Carbon (One Finance)'),
        ('fairmoney',   'FairMoney Microfinance Bank'),
        ('kuda',        'Kuda Bank'),
        ('moniepoint',  'Moniepoint Microfinance Bank'),
        ('opay',        'OPay Digital Services'),
        ('palmpay',     'PalmPay'),
        ('rubies',      'Rubies Bank'),
        ('vfd',         'VFD Microfinance Bank'),
        ('branch',      'Branch International Finance'),
        ('eyowo',       'Eyowo'),
    ]

    STATUS_PENDING    = 'pending'
    STATUS_APPROVED   = 'approved'
    STATUS_PROCESSING = 'processing'
    STATUS_COMPLETED  = 'completed'
    STATUS_REJECTED   = 'rejected'
    STATUS_FAILED     = 'failed'

    STATUS_CHOICES = [
        (STATUS_PENDING,    'Pending'),
        (STATUS_APPROVED,   'Approved'),
        (STATUS_PROCESSING, 'Processing'),
        (STATUS_COMPLETED,  'Completed'),
        (STATUS_REJECTED,   'Rejected'),
        (STATUS_FAILED,     'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='withdrawal_requests')

    # Amount breakdown
    amount_requested = models.DecimalField(max_digits=10, decimal_places=2, help_text='Amount before fee')
    fee_amount       = models.DecimalField(max_digits=10, decimal_places=2, help_text='5% fee')
    amount_to_receive = models.DecimalField(max_digits=10, decimal_places=2, help_text='Amount after fee deduction')
    points_deducted  = models.IntegerField(help_text='Points deducted for this withdrawal')

    # Bank details
    bank_name       = models.CharField(max_length=50, choices=BANK_CHOICES)
    account_number  = models.CharField(max_length=20)
    account_name    = models.CharField(max_length=200)

    # Status & tracking
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    reference       = models.CharField(max_length=30, unique=True, default=generate_withdrawal_ref)
    admin_notes     = models.TextField(blank=True)
    rejection_reason = models.CharField(max_length=300, blank=True)

    created_at      = models.DateTimeField(auto_now_add=True)
    processed_at    = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} – ₦{self.amount_to_receive} → {self.get_bank_name_display()} ({self.status})'

    @property
    def bank_display(self):
        return self.get_bank_name_display()

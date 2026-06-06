import uuid
import random
import string
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


def generate_referral_code():
    """Generate a unique 8-character alphanumeric referral code."""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=8))


class CustomUser(AbstractUser):
    """Extended user model with all TOPPERS profile and game data."""

    LEVEL_CHOICES = [
        (1, 'Beginner'),
        (2, 'Intermediate'),
        (3, 'Advanced'),
        (4, 'Expert'),
        (5, 'Master'),
        (6, 'Legend'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Profile
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=300, blank=True)
    country = models.CharField(max_length=100, default='Nigeria')
    phone_number = models.CharField(max_length=20, blank=True)

    # Points & Leveling
    total_points = models.IntegerField(default=0)
    total_xp = models.IntegerField(default=0)
    level = models.IntegerField(default=1, choices=LEVEL_CHOICES)

    # Referral
    referral_code = models.CharField(max_length=20, unique=True, default=generate_referral_code)
    referred_by = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='referrals'
    )

    # Verification
    is_email_verified = models.BooleanField(default=False)

    # OAuth
    google_id = models.CharField(max_length=255, blank=True)

    # Streak tracking
    last_login_date = models.DateField(null=True, blank=True)
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)

    # Daily game tracking
    daily_games_played = models.IntegerField(default=0)
    last_game_reset = models.DateField(null=True, blank=True)

    # Stats
    total_games_played = models.IntegerField(default=0)
    total_correct_answers = models.IntegerField(default=0)
    total_wrong_answers = models.IntegerField(default=0)
    total_challenges_won = models.IntegerField(default=0)
    total_airtime_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f'{self.username} ({self.email})'

    @property
    def level_name(self):
        return dict(self.LEVEL_CHOICES).get(self.level, 'Beginner')

    @property
    def accuracy_rate(self):
        total = self.total_correct_answers + self.total_wrong_answers
        if total == 0:
            return 0.0
        return round((self.total_correct_answers / total) * 100, 1)

    def add_points(self, amount, save=True):
        """Add points and update XP/level."""
        self.total_points += amount
        self.total_xp += amount
        self._update_level()
        if save:
            self.save(update_fields=['total_points', 'total_xp', 'level'])

    def deduct_points(self, amount, save=True):
        """Deduct points (for redemptions)."""
        if amount > self.total_points:
            raise ValueError("Insufficient points")
        self.total_points -= amount
        if save:
            self.save(update_fields=['total_points'])

    def _update_level(self):
        """Auto-level user based on XP."""
        xp = self.total_xp
        if xp >= 50000:
            self.level = 6
        elif xp >= 20000:
            self.level = 5
        elif xp >= 8000:
            self.level = 4
        elif xp >= 3000:
            self.level = 3
        elif xp >= 1000:
            self.level = 2
        else:
            self.level = 1

    def reset_daily_games(self):
        """Reset daily game count if it's a new day."""
        today = timezone.localdate()
        if self.last_game_reset != today:
            self.daily_games_played = 0
            self.last_game_reset = today
            self.save(update_fields=['daily_games_played', 'last_game_reset'])

    def update_streak(self):
        """Update login streak."""
        today = timezone.localdate()
        if self.last_login_date is None:
            self.current_streak = 1
        elif self.last_login_date == today:
            return  # Already logged in today
        elif (today - self.last_login_date).days == 1:
            self.current_streak += 1
        else:
            self.current_streak = 1

        self.last_login_date = today
        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak
        self.save(update_fields=['current_streak', 'longest_streak', 'last_login_date'])


class ReferralReward(models.Model):
    """Track referral bonuses between users."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    referrer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='referral_rewards_given')
    referred_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='referral_reward_received')
    points_awarded = models.IntegerField(default=500)
    bonus_naira = models.DecimalField(max_digits=6, decimal_places=2, default=20.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('referrer', 'referred_user')

    def __str__(self):
        return f'{self.referrer.username} referred {self.referred_user.username}'


class EmailVerificationToken(models.Model):
    """Email verification tokens."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='verification_tokens')
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at

    def __str__(self):
        return f'Token for {self.user.email}'

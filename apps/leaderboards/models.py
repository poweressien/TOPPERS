import uuid
from django.db import models


class LeaderboardEntry(models.Model):
    """Snapshot of a user's rank for a given period."""

    PERIOD_GLOBAL  = 'global'
    PERIOD_WEEKLY  = 'weekly'
    PERIOD_MONTHLY = 'monthly'

    PERIOD_CHOICES = [
        (PERIOD_GLOBAL,  'Global'),
        (PERIOD_WEEKLY,  'Weekly'),
        (PERIOD_MONTHLY, 'Monthly'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='leaderboard_entries')
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES)
    # e.g. 'all', '2024-W01', '2024-01'
    period_key = models.CharField(max_length=20, default='all')
    points = models.IntegerField(default=0)
    games_played = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    challenges_won = models.IntegerField(default=0)
    rank = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'period', 'period_key')
        ordering = ['period', 'rank']

    def __str__(self):
        return f'{self.user.username} – {self.period} #{self.rank}'

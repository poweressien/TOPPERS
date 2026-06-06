import uuid
from django.db import models
from django.utils import timezone
import datetime


class LiveChallenge(models.Model):
    """A 1v1 real-time challenge between two users."""

    STATUS_PENDING    = 'pending'
    STATUS_ACCEPTED   = 'accepted'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED  = 'completed'
    STATUS_DECLINED   = 'declined'
    STATUS_EXPIRED    = 'expired'

    STATUS_CHOICES = [
        (STATUS_PENDING,     'Pending'),
        (STATUS_ACCEPTED,    'Accepted'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_COMPLETED,   'Completed'),
        (STATUS_DECLINED,    'Declined'),
        (STATUS_EXPIRED,     'Expired'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    challenger = models.ForeignKey(
        'accounts.CustomUser', on_delete=models.CASCADE, related_name='challenges_sent'
    )
    challenged = models.ForeignKey(
        'accounts.CustomUser', on_delete=models.CASCADE, related_name='challenges_received'
    )
    category = models.ForeignKey(
        'quiz.Category', null=True, blank=True,
        on_delete=models.SET_NULL
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    winner = models.ForeignKey(
        'accounts.CustomUser', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='challenges_won'
    )
    bonus_points = models.IntegerField(default=100)
    question_ids = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + datetime.timedelta(hours=24)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.challenger.username} vs {self.challenged.username} ({self.status})'

    def is_expired(self):
        return self.status == self.STATUS_PENDING and timezone.now() > self.expires_at


class ChallengeResult(models.Model):
    """Each player's result in a challenge."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    challenge = models.ForeignKey(LiveChallenge, on_delete=models.CASCADE, related_name='results')
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    wrong_answers = models.IntegerField(default=0)
    time_taken_seconds = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('challenge', 'user')

    def __str__(self):
        return f'{self.user.username} – {self.challenge} score:{self.score}'

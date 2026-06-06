import uuid
from django.db import models


class Notification(models.Model):
    TYPE_CHOICES = [
        ('challenge',    'Challenge'),
        ('achievement',  'Achievement'),
        ('reward',       'Reward'),
        ('referral',     'Referral'),
        ('system',       'System'),
        ('leaderboard',  'Leaderboard'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='system')
    is_read = models.BooleanField(default=False)
    action_url = models.CharField(max_length=500, blank=True)
    extra_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} – {self.title}'

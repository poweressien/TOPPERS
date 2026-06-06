import uuid
from django.db import models


class Advertisement(models.Model):
    AD_TYPES = [
        ('video',         'Video'),
        ('banner',        'Banner'),
        ('interstitial',  'Interstitial'),
    ]
    REWARD_TYPES = [
        ('extra_game',   'Extra Game Session'),
        ('bonus_points', 'Bonus Points'),
        ('lifeline',     'Temporary Lifeline'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    advertiser = models.CharField(max_length=200, blank=True)
    ad_type = models.CharField(max_length=20, choices=AD_TYPES)
    media_url = models.URLField(blank=True)
    duration_seconds = models.IntegerField(default=30)
    reward_type = models.CharField(max_length=20, choices=REWARD_TYPES)
    reward_value = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    max_views_per_user_per_day = models.IntegerField(default=5)
    total_views = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} ({self.ad_type})'


class AdView(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='ad_views')
    advertisement = models.ForeignKey(Advertisement, on_delete=models.CASCADE, related_name='views_log')
    reward_granted = models.BooleanField(default=False)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-viewed_at']

    def __str__(self):
        return f'{self.user.username} viewed {self.advertisement.title}'

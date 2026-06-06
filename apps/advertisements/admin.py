from django.contrib import admin
from .models import Advertisement, AdView

@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ['title', 'ad_type', 'reward_type', 'reward_value', 'total_views', 'is_active']
    list_filter = ['ad_type', 'reward_type', 'is_active']
    search_fields = ['title', 'advertiser']

@admin.register(AdView)
class AdViewAdmin(admin.ModelAdmin):
    list_display = ['user', 'advertisement', 'reward_granted', 'viewed_at']
    list_filter = ['reward_granted']

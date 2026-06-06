from django.contrib import admin
from .models import LeaderboardEntry

@admin.register(LeaderboardEntry)
class LeaderboardEntryAdmin(admin.ModelAdmin):
    list_display = ['rank', 'user', 'period', 'period_key', 'points', 'games_played']
    list_filter = ['period']
    search_fields = ['user__username']
    ordering = ['period', 'rank']

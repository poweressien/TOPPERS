from django.contrib import admin
from .models import LiveChallenge, ChallengeResult

@admin.register(LiveChallenge)
class LiveChallengeAdmin(admin.ModelAdmin):
    list_display = ['challenger', 'challenged', 'status', 'winner', 'bonus_points', 'created_at']
    list_filter = ['status']
    search_fields = ['challenger__username', 'challenged__username']

@admin.register(ChallengeResult)
class ChallengeResultAdmin(admin.ModelAdmin):
    list_display = ['challenge', 'user', 'score', 'correct_answers', 'completed']
    list_filter = ['completed']

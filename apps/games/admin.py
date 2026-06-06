from django.contrib import admin
from .models import GameSession, GameAnswer, UserLifeline, DailyChallenge


class GameAnswerInline(admin.TabularInline):
    model = GameAnswer
    extra = 0
    readonly_fields = ['question', 'chosen_answer', 'is_correct', 'points_earned', 'time_taken_seconds']
    can_delete = False


@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'mode', 'status', 'score', 'correct_answers', 'questions_answered', 'start_time']
    list_filter = ['mode', 'status']
    search_fields = ['user__username']
    readonly_fields = ['id', 'start_time', 'end_time', 'question_ids']
    inlines = [GameAnswerInline]
    ordering = ['-start_time']


@admin.register(UserLifeline)
class UserLifelineAdmin(admin.ModelAdmin):
    list_display = ['user', 'lifeline_type', 'quantity']
    list_filter = ['lifeline_type']
    search_fields = ['user__username']


@admin.register(DailyChallenge)
class DailyChallengeAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'streak_at_time', 'bonus_awarded']
    list_filter = ['date', 'bonus_awarded']
    ordering = ['-date']

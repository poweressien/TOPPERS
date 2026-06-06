from django.urls import path
from .views import GlobalLeaderboardView, WeeklyLeaderboardView, MonthlyLeaderboardView

urlpatterns = [
    path('global/',  GlobalLeaderboardView.as_view(),  name='global_leaderboard'),
    path('weekly/',  WeeklyLeaderboardView.as_view(),  name='weekly_leaderboard'),
    path('monthly/', MonthlyLeaderboardView.as_view(), name='monthly_leaderboard'),
]

from django.urls import path
from .views import (
    PointsBalanceView, TransactionHistoryView, DailyLoginBonusView,
    AchievementListView, UserAchievementView,
    WithdrawalRequestView, WithdrawalHistoryView, WithdrawalBanksView,
)

urlpatterns = [
    path('points/',              PointsBalanceView.as_view(),     name='points_balance'),
    path('transactions/',        TransactionHistoryView.as_view(), name='transactions'),
    path('daily-bonus/',         DailyLoginBonusView.as_view(),   name='daily_bonus'),
    path('achievements/',        AchievementListView.as_view(),   name='achievements'),
    path('achievements/mine/',   UserAchievementView.as_view(),   name='my_achievements'),
    path('withdraw/',            WithdrawalRequestView.as_view(), name='withdraw'),
    path('withdraw/history/',    WithdrawalHistoryView.as_view(), name='withdrawal_history'),
    path('withdraw/banks/',      WithdrawalBanksView.as_view(),   name='banks_list'),
]

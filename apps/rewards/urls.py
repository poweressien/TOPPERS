from django.urls import path
from .views import (
    PointsBalanceView, TransactionHistoryView, DailyLoginBonusView,
    AchievementListView, UserAchievementView,
    RedeemAirtimeView, AirtimeHistoryView,
)

urlpatterns = [
    path('points/',               PointsBalanceView.as_view(),     name='points_balance'),
    path('transactions/',         TransactionHistoryView.as_view(), name='transactions'),
    path('daily-bonus/',          DailyLoginBonusView.as_view(),   name='daily_bonus'),
    path('achievements/',         AchievementListView.as_view(),   name='achievements'),
    path('achievements/mine/',    UserAchievementView.as_view(),   name='my_achievements'),
    path('airtime/redeem/',       RedeemAirtimeView.as_view(),     name='redeem_airtime'),
    path('airtime/history/',      AirtimeHistoryView.as_view(),    name='airtime_history'),
]

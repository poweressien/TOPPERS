from django.urls import path
from apps.accounts.views import MeView, PublicProfileView, UserStatsView, ReferralDashboardView

urlpatterns = [
    path('me/',                MeView.as_view(),             name='me'),
    path('me/stats/',          UserStatsView.as_view(),      name='my_stats'),
    path('me/referrals/',      ReferralDashboardView.as_view(), name='referral_dashboard'),
    path('<str:username>/',    PublicProfileView.as_view(),  name='public_profile'),
]

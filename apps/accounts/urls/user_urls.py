from django.urls import path
from apps.accounts.views import MeView, PublicProfileView, UserStatsView, ReferralDashboardView, PlatformStatsView

urlpatterns = [
    path('me/',                MeView.as_view(),             name='me'),
    path('me/stats/',          UserStatsView.as_view(),      name='my_stats'),
    path('me/referrals/',      ReferralDashboardView.as_view(), name='referral_dashboard'),
    path('stats/platform/',    PlatformStatsView.as_view(),  name='platform_stats'),
    path('<str:username>/',    PublicProfileView.as_view(),  name='public_profile'),
]

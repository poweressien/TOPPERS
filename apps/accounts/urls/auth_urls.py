from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from apps.accounts.views import (
    RegisterView, LoginView, LogoutView, ChangePasswordView,
    validate_referral_code, OAuthTokenView,
)

urlpatterns = [
    path('register/',                  RegisterView.as_view(),       name='register'),
    path('login/',                     LoginView.as_view(),           name='login'),
    path('logout/',                    LogoutView.as_view(),          name='logout'),
    path('token/refresh/',             TokenRefreshView.as_view(),    name='token_refresh'),
    path('change-password/',           ChangePasswordView.as_view(),  name='change_password'),
    path('oauth-token/',               OAuthTokenView.as_view(),      name='oauth_token'),
    path('referral/<str:code>/validate/', validate_referral_code,    name='validate_referral'),
]

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from .page_views import (home, login_page, register_page, dashboard, play,
                         leaderboard, profile, about, contact, terms, privacy)

urlpatterns = [
    path('',              home,          name='home'),
    path('login/',        login_page,    name='login'),
    path('register/',     register_page, name='register'),
    path('dashboard/',    dashboard,     name='dashboard'),
    path('play/',         play,          name='play'),
    path('leaderboard/',  leaderboard,   name='leaderboard'),
    path('profile/',      profile,       name='profile'),
    path('about/',        about,         name='about'),
    path('contact/',      contact,       name='contact'),
    path('terms/',        terms,         name='terms'),
    path('privacy/',      privacy,       name='privacy'),
    path('auth/oauth-success/', TemplateView.as_view(template_name='auth/oauth_success.html'), name='oauth_success'),
    path('admin/',        admin.site.urls),
    path('api/v1/auth/',          include('apps.accounts.urls.auth_urls')),
    path('api/v1/users/',         include('apps.accounts.urls.user_urls')),
    path('api/v1/quiz/',          include('apps.quiz.urls')),
    path('api/v1/games/',         include('apps.games.urls')),
    path('api/v1/rewards/',       include('apps.rewards.urls')),
    path('api/v1/leaderboards/',  include('apps.leaderboards.urls')),
    path('api/v1/challenges/',    include('apps.challenges.urls')),
    path('api/v1/notifications/', include('apps.notifications.urls')),
    path('api/v1/ads/',           include('apps.advertisements.urls')),
    path('accounts/',             include('allauth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    try:
        import debug_toolbar
        urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
    except ImportError:
        pass

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GameSessionViewSet, LifelineView, DailyStatusView

router = DefaultRouter()
router.register('sessions', GameSessionViewSet, basename='game_session')

urlpatterns = [
    path('', include(router.urls)),
    path('lifelines/',     LifelineView.as_view(),    name='lifelines'),
    path('daily-status/',  DailyStatusView.as_view(), name='daily_status'),
]

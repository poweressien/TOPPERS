from django.urls import path
from .views import ActiveAdsView, record_ad_view

urlpatterns = [
    path('',            ActiveAdsView.as_view(), name='active_ads'),
    path('<uuid:pk>/view/', record_ad_view,      name='record_ad_view'),
]

from django.urls import path
from .views import NotificationListView, mark_read, mark_all_read, unread_count

urlpatterns = [
    path('',             NotificationListView.as_view(), name='notifications'),
    path('unread/',      unread_count,                   name='unread_count'),
    path('read-all/',    mark_all_read,                  name='mark_all_read'),
    path('<uuid:pk>/read/', mark_read,                   name='mark_read'),
]

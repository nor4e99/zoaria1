from django.urls import path
from .views import NotificationListView, MarkNotificationReadView, UnreadCountView

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('unread-count/', UnreadCountView.as_view(), name='unread-count'),
    path('mark-read/', MarkNotificationReadView.as_view(), name='mark-all-read'),
    path('<int:pk>/read/', MarkNotificationReadView.as_view(), name='mark-read'),
]

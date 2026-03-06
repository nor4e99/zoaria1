from django.urls import path
from .views import ActivityLogView, ActivityLogDetailView, ActivityStatsView

urlpatterns = [
    path('pets/<int:pet_id>/',          ActivityLogView.as_view(),       name='activity-list'),
    path('pets/<int:pet_id>/stats/',    ActivityStatsView.as_view(),     name='activity-stats'),
    path('<int:pk>/',                   ActivityLogDetailView.as_view(), name='activity-detail'),
]

from django.urls import path
from .views import (
    PendingVetListView, ApproveVetView, RejectVetView,
    UserListView, ToggleUserActiveView, AnalyticsDashboardView
)

urlpatterns = [
    path('vets/pending/', PendingVetListView.as_view(), name='pending-vets'),
    path('vets/<int:vet_id>/approve/', ApproveVetView.as_view(), name='approve-vet'),
    path('vets/<int:vet_id>/reject/', RejectVetView.as_view(), name='reject-vet'),
    path('users/', UserListView.as_view(), name='admin-users'),
    path('users/<int:user_id>/toggle-active/', ToggleUserActiveView.as_view(), name='toggle-user'),
    path('analytics/', AnalyticsDashboardView.as_view(), name='analytics'),
]

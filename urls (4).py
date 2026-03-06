from django.urls import path
from .views import AppointmentListCreateView, AppointmentDetailView, ReminderListCreateView

urlpatterns = [
    path('appointments/', AppointmentListCreateView.as_view(), name='appointment-list'),
    path('appointments/<int:pk>/', AppointmentDetailView.as_view(), name='appointment-detail'),
    path('reminders/', ReminderListCreateView.as_view(), name='all-reminders'),
    path('pets/<int:pet_id>/reminders/', ReminderListCreateView.as_view(), name='pet-reminders'),
]

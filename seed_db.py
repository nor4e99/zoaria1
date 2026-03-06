from rest_framework import serializers, generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.urls import path

from .models import Appointment, Reminder
from apps.pets.models import Pet
from apps.users.models import User


class AppointmentSerializer(serializers.ModelSerializer):
    vet_name = serializers.SerializerMethodField()
    pet_name = serializers.CharField(source='pet.name', read_only=True)

    class Meta:
        model = Appointment
        fields = ['id', 'vet', 'vet_name', 'pet', 'pet_name',
                  'appointment_time', 'status', 'notes']
        read_only_fields = ['id']

    def get_vet_name(self, obj):
        try:
            return obj.vet.profile.name or obj.vet.email
        except Exception:
            return obj.vet.email


class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        fields = ['id', 'pet', 'reminder_type', 'reminder_date',
                  'repeat_interval_days', 'title', 'notes', 'sent']
        read_only_fields = ['id', 'sent']


class AppointmentListCreateView(generics.ListCreateAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'vet':
            return Appointment.objects.filter(vet=user).select_related('pet', 'vet')
        return Appointment.objects.filter(owner=user).select_related('pet', 'vet')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class AppointmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'vet':
            return Appointment.objects.filter(vet=user)
        return Appointment.objects.filter(owner=user)


class ReminderListCreateView(generics.ListCreateAPIView):
    serializer_class = ReminderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        pet_id = self.kwargs.get('pet_id')
        if pet_id:
            pet = get_object_or_404(Pet, id=pet_id, owner=self.request.user)
            return Reminder.objects.filter(pet=pet)
        # All reminders across all user's pets
        return Reminder.objects.filter(pet__owner=self.request.user)

    def perform_create(self, serializer):
        pet_id = self.kwargs.get('pet_id')
        if pet_id:
            pet = get_object_or_404(Pet, id=pet_id, owner=self.request.user)
            serializer.save(pet=pet)
        else:
            serializer.save()


urlpatterns = [
    path('appointments/', AppointmentListCreateView.as_view(), name='appointment-list'),
    path('appointments/<int:pk>/', AppointmentDetailView.as_view(), name='appointment-detail'),
    path('reminders/', ReminderListCreateView.as_view(), name='all-reminders'),
    path('pets/<int:pet_id>/reminders/', ReminderListCreateView.as_view(), name='pet-reminders'),
]

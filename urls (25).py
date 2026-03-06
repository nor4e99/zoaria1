from rest_framework import serializers, generics
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.urls import path

from .models import MedicalRecord, Prescription
from apps.pets.models import Pet


class MedicalRecordSerializer(serializers.ModelSerializer):
    vet_email = serializers.EmailField(source='vet.email', read_only=True)

    class Meta:
        model = MedicalRecord
        fields = ['id', 'pet', 'vet', 'vet_email', 'diagnosis', 'treatment', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']


class PrescriptionSerializer(serializers.ModelSerializer):
    vet_email = serializers.EmailField(source='vet.email', read_only=True)

    class Meta:
        model = Prescription
        fields = ['id', 'pet', 'vet', 'vet_email', 'medication_name',
                  'dosage', 'duration', 'instructions', 'created_at']
        read_only_fields = ['id', 'created_at']


def get_pet_for_user(user, pet_id):
    """Returns pet if user is owner or vet."""
    pet = get_object_or_404(Pet, id=pet_id)
    if pet.owner == user or user.role in ('vet', 'admin'):
        return pet
    from rest_framework.exceptions import PermissionDenied
    raise PermissionDenied()


class PetMedicalRecordView(generics.ListCreateAPIView):
    serializer_class = MedicalRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        pet = get_pet_for_user(self.request.user, self.kwargs['pet_id'])
        return MedicalRecord.objects.filter(pet=pet)

    def perform_create(self, serializer):
        pet = get_pet_for_user(self.request.user, self.kwargs['pet_id'])
        serializer.save(pet=pet, vet=self.request.user)


class PetPrescriptionView(generics.ListCreateAPIView):
    serializer_class = PrescriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        pet = get_pet_for_user(self.request.user, self.kwargs['pet_id'])
        return Prescription.objects.filter(pet=pet)

    def perform_create(self, serializer):
        pet = get_pet_for_user(self.request.user, self.kwargs['pet_id'])
        serializer.save(pet=pet, vet=self.request.user)


urlpatterns = [
    path('pets/<int:pet_id>/records/', PetMedicalRecordView.as_view(), name='pet-medical-records'),
    path('pets/<int:pet_id>/prescriptions/', PetPrescriptionView.as_view(), name='pet-prescriptions'),
]

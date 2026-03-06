from django.db import models
from apps.users.models import User
from apps.pets.models import Pet


class MedicalRecord(models.Model):
    """Maps to `medical_records` table."""
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='medical_records')
    vet = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='authored_records')
    diagnosis = models.TextField(blank=True)
    treatment = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'medical_records'
        ordering = ['-created_at']

    def __str__(self):
        return f'Record for {self.pet.name} - {self.created_at.date()}'


class Prescription(models.Model):
    """Maps to `prescriptions` table."""
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='prescriptions')
    vet = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='authored_prescriptions')
    medication_name = models.CharField(max_length=255)
    dosage = models.CharField(max_length=100, blank=True)
    duration = models.CharField(max_length=100, blank=True)
    instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'prescriptions'
        ordering = ['-created_at']

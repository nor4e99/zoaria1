from django.db import models
from apps.users.models import User
from apps.pets.models import Pet


class Appointment(models.Model):
    """Maps to `appointments` table."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments_as_owner')
    vet = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments_as_vet')
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='appointments')
    appointment_time = models.DateTimeField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'appointments'
        ordering = ['appointment_time']


class Reminder(models.Model):
    """Maps to `reminders` table."""
    REMINDER_TYPES = [
        ('vaccination', 'Vaccination'),
        ('deworming', 'Deworming'),
        ('appointment', 'Appointment'),
        ('medication', 'Medication'),
        ('custom', 'Custom'),
    ]

    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='reminders')
    reminder_type = models.CharField(max_length=100, choices=REMINDER_TYPES)
    reminder_date = models.DateField()
    repeat_interval_days = models.IntegerField(null=True, blank=True)
    title = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    sent = models.BooleanField(default=False)

    class Meta:
        db_table = 'reminders'
        ordering = ['reminder_date']

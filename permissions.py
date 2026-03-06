from django.db import models
from apps.users.models import User


class Notification(models.Model):
    """Maps to `notifications` table."""
    TYPE_CHOICES = [
        ('message', 'New Message'),
        ('appointment', 'Appointment'),
        ('vaccination', 'Vaccination Reminder'),
        ('deworming', 'Deworming Reminder'),
        ('consultation', 'Consultation Update'),
        ('system', 'System'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='system')
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

    @classmethod
    def send(cls, user, title, message, notification_type='system'):
        """Utility to create a notification."""
        return cls.objects.create(
            user=user, title=title, message=message, notification_type=notification_type
        )

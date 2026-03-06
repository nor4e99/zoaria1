from django.db import models
from apps.users.models import User


class Subscription(models.Model):
    """Maps to `subscriptions` table."""
    PLAN_CHOICES = [
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    plan_name = models.CharField(max_length=50, choices=PLAN_CHOICES, default='basic')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    active = models.BooleanField(default=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'subscriptions'

    def __str__(self):
        return f'{self.user.email} — {self.plan_name}'


class Payment(models.Model):
    """Maps to `payments` table."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='EUR')
    payment_status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payments'

    def __str__(self):
        return f'{self.user.email} — {self.amount} {self.currency} ({self.payment_status})'


class Consultation(models.Model):
    """Maps to `consultations` table."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    conversation = models.ForeignKey(
        'chat.Conversation', on_delete=models.SET_NULL, null=True, blank=True
    )
    vet = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vet_consultations')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner_consultations')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'consultations'

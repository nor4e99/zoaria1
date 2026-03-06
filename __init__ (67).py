from django.db import models
from apps.pets.models import Pet


class ActivityLog(models.Model):
    """Extended activity log with GPS and duration support."""
    ACTIVITY_TYPES = [
        ('walk',     'Walk'),
        ('run',      'Run'),
        ('play',     'Play'),
        ('swim',     'Swim'),
        ('training', 'Training'),
        ('other',    'Other'),
    ]

    pet              = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='activity_logs')
    activity_type    = models.CharField(max_length=50, choices=ACTIVITY_TYPES, default='walk')
    distance         = models.FloatField(null=True, blank=True)          # km
    duration_minutes = models.IntegerField(null=True, blank=True)        # minutes
    calories_burned  = models.FloatField(null=True, blank=True)          # kcal
    activity_date    = models.DateField()
    notes            = models.CharField(max_length=255, blank=True)

    # Optional GPS bounding-box (for map display)
    gps_start_lat  = models.FloatField(null=True, blank=True)
    gps_start_lng  = models.FloatField(null=True, blank=True)
    gps_end_lat    = models.FloatField(null=True, blank=True)
    gps_end_lng    = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'activity_logs'
        ordering = ['-activity_date', '-created_at']

    def __str__(self):
        return f'{self.pet.name} – {self.activity_type} on {self.activity_date}'

    @property
    def estimated_calories(self):
        """Estimate kcal if not manually set: uses MER-based formula."""
        if self.calories_burned:
            return self.calories_burned
        if not self.pet.weight or not self.duration_minutes:
            return None
        # MET approximations per activity type
        met = {'walk': 3.0, 'run': 6.0, 'play': 4.0, 'swim': 5.0, 'training': 4.5, 'other': 3.0}
        m = met.get(self.activity_type, 3.0)
        # kcal = MET * weight(kg) * duration(h)
        return round(m * self.pet.weight * (self.duration_minutes / 60), 1)

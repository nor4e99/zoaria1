from django.db import models
from apps.users.models import User


class Species(models.Model):
    """Maps to `species` table. Seeded from zoaria_veterinary_database.sql."""
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'species'
        verbose_name_plural = 'Species'

    def __str__(self):
        return self.name


class Breed(models.Model):
    """Maps to `breeds` table."""
    species = models.ForeignKey(Species, on_delete=models.CASCADE, related_name='breeds')
    breed_name = models.CharField(max_length=150)
    min_weight = models.FloatField(null=True, blank=True)
    max_weight = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'breeds'
        ordering = ['breed_name']

    def __str__(self):
        return f'{self.breed_name} ({self.species.name})'


class BreedCondition(models.Model):
    """Maps to `breed_conditions` table."""
    breed = models.ForeignKey(Breed, on_delete=models.CASCADE, related_name='conditions')
    condition_name = models.TextField()

    class Meta:
        db_table = 'breed_conditions'

    def __str__(self):
        return f'{self.breed.breed_name}: {self.condition_name}'


class Pet(models.Model):
    """Maps to `pets` table."""
    GENDER_CHOICES = [('male', 'Male'), ('female', 'Female'), ('unknown', 'Unknown')]
    ACTIVITY_CHOICES = [
        ('low', 'Low'),
        ('moderate', 'Moderate'),
        ('active', 'Active'),
        ('very_active', 'Very Active'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pets')
    name = models.CharField(max_length=150)
    species = models.ForeignKey(Species, on_delete=models.SET_NULL, null=True)
    breed = models.ForeignKey(Breed, on_delete=models.SET_NULL, null=True, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default='unknown')
    sterilized = models.BooleanField(default=False)
    age = models.IntegerField(null=True, blank=True)  # months
    weight = models.FloatField(null=True, blank=True)  # kg
    ideal_weight = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)  # cm
    activity_level = models.CharField(max_length=50, choices=ACTIVITY_CHOICES, default='moderate')
    chip_number = models.CharField(max_length=100, blank=True)
    medical_notes = models.TextField(blank=True)
    avatar_type = models.CharField(max_length=50, blank=True)  # icon key
    photo_url = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pets'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.owner.email})'

    @property
    def weight_status(self):
        """Returns 'underweight', 'healthy', 'overweight', or None if no breed data."""
        if not self.weight or not self.breed:
            return None
        min_w = self.breed.min_weight
        max_w = self.breed.max_weight
        if min_w is None or max_w is None:
            return None
        if self.weight < min_w:
            return 'underweight'
        elif self.weight > max_w:
            return 'overweight'
        return 'healthy'

    @property
    def bmi_normalized(self):
        """
        Returns a 0–1 float for the BMI gauge needle position.
        0 = severely underweight, 0.5 = perfectly mid-range, 1 = severely obese.
        """
        if not self.weight or not self.breed:
            return None
        min_w = self.breed.min_weight or 0
        max_w = self.breed.max_weight or 1
        mid = (min_w + max_w) / 2
        spread = (max_w - min_w) * 1.5  # allow gauge to extend 50% beyond range
        position = (self.weight - (mid - spread / 2)) / spread
        return max(0.0, min(1.0, round(position, 3)))

    @property
    def rer(self):
        """Resting Energy Requirement (kcal/day)."""
        if not self.weight:
            return None
        return round(70 * (self.weight ** 0.75), 1)

    @property
    def mer(self):
        """Maintenance Energy Requirement (kcal/day)."""
        if not self.rer:
            return None
        factors = {'low': 1.2, 'moderate': 1.4, 'active': 1.6, 'very_active': 1.8}
        return round(self.rer * factors.get(self.activity_level, 1.4), 1)

from django.db import models
from rest_framework import serializers, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.urls import path

from apps.pets.models import Pet, Species


# ─── Models ───────────────────────────────────────────────────────────────────

class FeedingLog(models.Model):
    """Maps to `feeding_logs` table."""
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='feeding_logs')
    food_type = models.CharField(max_length=100)
    amount = models.FloatField()  # grams
    calories = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'feeding_logs'
        ordering = ['-created_at']


class FeedingGuideline(models.Model):
    """Maps to `feeding_guidelines` table (from veterinary DB)."""
    species = models.ForeignKey(Species, on_delete=models.CASCADE)
    food_category = models.CharField(max_length=100)
    food_name = models.CharField(max_length=150)

    class Meta:
        db_table = 'feeding_guidelines'


# ─── Serializers ──────────────────────────────────────────────────────────────

class FeedingLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedingLog
        fields = ['id', 'food_type', 'amount', 'calories', 'created_at']
        read_only_fields = ['id', 'created_at']


class FeedingGuidelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedingGuideline
        fields = ['id', 'food_category', 'food_name']


# ─── Views ────────────────────────────────────────────────────────────────────

class FeedingLogView(generics.ListCreateAPIView):
    serializer_class = FeedingLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        pet = get_object_or_404(Pet, id=self.kwargs['pet_id'], owner=self.request.user)
        return FeedingLog.objects.filter(pet=pet)

    def perform_create(self, serializer):
        pet = get_object_or_404(Pet, id=self.kwargs['pet_id'], owner=self.request.user)
        serializer.save(pet=pet)


class FeedingGuidelinesView(APIView):
    """Returns feeding options for a given species."""
    permission_classes = [AllowAny]

    def get(self, request, species_id):
        guidelines = FeedingGuideline.objects.filter(species_id=species_id)
        # Also add vitamin C warning for guinea pigs (species_id=5)
        data = FeedingGuidelineSerializer(guidelines, many=True).data
        warnings = []
        try:
            species = Species.objects.get(id=species_id)
            if species.name == 'Guinea Pig':
                warnings.append({
                    'type': 'vitamin_c',
                    'message': '⚠️ Guinea pigs cannot synthesize Vitamin C. Ensure daily supplementation through fresh vegetables or supplements.',
                })
        except Species.DoesNotExist:
            pass
        return Response({'guidelines': data, 'warnings': warnings})


class CalorieCalculatorView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pet_id):
        pet = get_object_or_404(Pet, id=pet_id, owner=request.user)
        if not pet.weight:
            return Response({'error': 'Pet weight is required.'}, status=400)
        return Response({
            'weight_kg': pet.weight,
            'activity_level': pet.activity_level,
            'rer': pet.rer,
            'mer': pet.mer,
            'note': 'RER = 70 × weight^0.75 | MER = RER × activity factor',
        })


# ─── URLs ─────────────────────────────────────────────────────────────────────

urlpatterns = [
    path('pets/<int:pet_id>/feeding/', FeedingLogView.as_view(), name='feeding-log'),
    path('pets/<int:pet_id>/calories/', CalorieCalculatorView.as_view(), name='calorie-calculator'),
    path('guidelines/<int:species_id>/', FeedingGuidelinesView.as_view(), name='feeding-guidelines'),
]

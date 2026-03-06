from rest_framework import serializers, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import FeedingLog, FeedingGuideline
from apps.pets.models import Pet, Species


class FeedingLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedingLog
        fields = ['id', 'food_type', 'amount', 'calories', 'created_at']
        read_only_fields = ['id', 'created_at']


class FeedingGuidelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedingGuideline
        fields = ['id', 'food_category', 'food_name']


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
    permission_classes = [AllowAny]

    def get(self, request, species_id):
        guidelines = FeedingGuideline.objects.filter(species_id=species_id)
        data = FeedingGuidelineSerializer(guidelines, many=True).data
        warnings = []
        try:
            species = Species.objects.get(id=species_id)
            if species.name == 'Guinea Pig':
                warnings.append({
                    'type': 'vitamin_c',
                    'message': '⚠️ Guinea pigs cannot synthesize Vitamin C. Ensure daily supplementation.',
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
            'formula': 'RER = 70 × weight^0.75 | MER = RER × activity_factor',
        })

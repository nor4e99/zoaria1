from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Pet, Species, Breed, BreedCondition
from .serializers import (
    PetSerializer,
    PetListSerializer,
    SpeciesSerializer,
    BreedSerializer,
    BreedListSerializer,
    BreedConditionSerializer,
)
from apps.payments.permissions import SubscriptionPermission


class IsOwnerPermission:
    """Mixin: user can only access their own pets."""
    def get_queryset(self):
        return Pet.objects.filter(owner=self.request.user).select_related('species', 'breed')


# ─── Species & Breeds (public) ────────────────────────────────────────────────

class SpeciesListView(generics.ListAPIView):
    serializer_class = SpeciesSerializer
    permission_classes = [AllowAny]
    queryset = Species.objects.all().order_by('name')


class BreedListView(generics.ListAPIView):
    serializer_class = BreedListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        species_id = self.request.query_params.get('species')
        qs = Breed.objects.select_related('species')
        if species_id:
            qs = qs.filter(species_id=species_id)
        return qs.order_by('breed_name')


class BreedDetailView(generics.RetrieveAPIView):
    serializer_class = BreedSerializer
    permission_classes = [AllowAny]
    queryset = Breed.objects.prefetch_related('conditions').all()


class BreedConditionsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, breed_id):
        conditions = BreedCondition.objects.filter(breed_id=breed_id)
        return Response(BreedConditionSerializer(conditions, many=True).data)


# ─── Pets CRUD ────────────────────────────────────────────────────────────────

class PetListCreateView(IsOwnerPermission, generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PetListSerializer
        return PetSerializer

    def get_queryset(self):
        return Pet.objects.filter(owner=self.request.user).select_related('species', 'breed')

    def perform_create(self, serializer):
        # Subscription limit check
        user = self.request.user
        pet_count = Pet.objects.filter(owner=user).count()
        plan = self._get_plan(user)
        limits = {'basic': 1, 'standard': 2, 'premium': None}
        limit = limits.get(plan)
        if limit is not None and pet_count >= limit:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied(
                f'Your {plan} plan allows up to {limit} pet(s). Upgrade to add more.'
            )
        serializer.save(owner=user)

    def _get_plan(self, user):
        try:
            from apps.payments.models import Subscription
            sub = Subscription.objects.filter(user=user, active=True).order_by('-start_date').first()
            return sub.plan_name if sub else 'basic'
        except Exception:
            return 'basic'


class PetDetailView(IsOwnerPermission, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PetSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(Pet, id=self.kwargs['pk'], owner=self.request.user)


class PetBMIView(APIView):
    """Returns computed BMI data for a pet."""
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        pet = get_object_or_404(Pet, id=pk, owner=request.user)
        if not pet.weight or not pet.breed:
            return Response({'error': 'Pet needs weight and breed for BMI calculation.'}, status=400)

        return Response({
            'pet_id': pet.id,
            'weight': pet.weight,
            'breed_min': pet.breed.min_weight,
            'breed_max': pet.breed.max_weight,
            'weight_status': pet.weight_status,
            'bmi_normalized': pet.bmi_normalized,
            'rer': pet.rer,
            'mer': pet.mer,
            'activity_level': pet.activity_level,
        })

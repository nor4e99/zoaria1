from rest_framework import serializers, generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Avg, Count
from datetime import date, timedelta

from .models import ActivityLog
from apps.pets.models import Pet


class ActivityLogSerializer(serializers.ModelSerializer):
    estimated_calories = serializers.ReadOnlyField()

    class Meta:
        model = ActivityLog
        fields = [
            'id', 'activity_type', 'distance', 'duration_minutes',
            'calories_burned', 'estimated_calories', 'activity_date', 'notes',
            'gps_start_lat', 'gps_start_lng', 'gps_end_lat', 'gps_end_lng',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at', 'estimated_calories']


class ActivityLogView(generics.ListCreateAPIView):
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated]

    def _get_pet(self):
        return get_object_or_404(Pet, id=self.kwargs['pet_id'], owner=self.request.user)

    def get_queryset(self):
        pet = self._get_pet()
        qs  = ActivityLog.objects.filter(pet=pet)
        # Optional date range filter
        since = self.request.query_params.get('since')   # YYYY-MM-DD
        until = self.request.query_params.get('until')
        if since:
            qs = qs.filter(activity_date__gte=since)
        if until:
            qs = qs.filter(activity_date__lte=until)
        return qs

    def perform_create(self, serializer):
        pet = self._get_pet()
        serializer.save(pet=pet)


class ActivityLogDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ActivityLog.objects.filter(pet__owner=self.request.user)


class ActivityStatsView(APIView):
    """
    GET /api/activity/pets/<pet_id>/stats/?period=30
    Returns aggregated stats for the given period (default 30 days).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pet_id):
        pet    = get_object_or_404(Pet, id=pet_id, owner=request.user)
        days   = int(request.query_params.get('period', 30))
        since  = date.today() - timedelta(days=days)

        logs = ActivityLog.objects.filter(pet=pet, activity_date__gte=since)

        agg = logs.aggregate(
            total_distance=Sum('distance'),
            total_duration=Sum('duration_minutes'),
            total_calories=Sum('calories_burned'),
            sessions=Count('id'),
        )

        # Per-type breakdown
        by_type = {}
        for row in logs.values('activity_type').annotate(
            count=Count('id'),
            distance=Sum('distance'),
            duration=Sum('duration_minutes'),
        ):
            by_type[row['activity_type']] = {
                'count':    row['count'],
                'distance': row['distance'],
                'duration': row['duration'],
            }

        return Response({
            'period_days':     days,
            'sessions':        agg['sessions'] or 0,
            'total_distance':  round(agg['total_distance'] or 0, 2),
            'total_duration':  agg['total_duration'] or 0,
            'total_calories':  round(agg['total_calories'] or 0, 1),
            'by_type':         by_type,
            'avg_per_session': {
                'distance': round((agg['total_distance'] or 0) / max(agg['sessions'] or 1, 1), 2),
                'duration': round((agg['total_duration'] or 0) / max(agg['sessions'] or 1, 1), 1),
            },
        })

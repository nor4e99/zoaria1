from rest_framework import serializers, generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.urls import path

from apps.users.models import User
from apps.vets.models import VetProfile
from apps.payments.models import Payment, Subscription
from apps.pets.models import Pet


class IsAdminUserRole(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == 'admin'


# ─── Vet Approval ─────────────────────────────────────────────────────────────

class PendingVetListView(APIView):
    permission_classes = [IsAdminUserRole]

    def get(self, request):
        vets = VetProfile.objects.filter(approved=False).select_related('user__profile')
        data = [
            {
                'id': v.id,
                'user_id': v.user_id,
                'email': v.user.email,
                'name': getattr(v.user, 'profile', None) and v.user.profile.name,
                'specialization': v.specialization,
                'clinic_name': v.clinic_name,
                'license_document': v.license_document,
            }
            for v in vets
        ]
        return Response(data)


class ApproveVetView(APIView):
    permission_classes = [IsAdminUserRole]

    def post(self, request, vet_id):
        vet = get_object_or_404(VetProfile, id=vet_id)
        vet.approved = True
        vet.save()

        # Notify vet
        from apps.notifications.models import Notification
        Notification.send(
            user=vet.user,
            title='Account Approved!',
            message='Your veterinarian account has been approved by ZOARIA admin. You can now receive consultations.',
            notification_type='system',
        )
        return Response({'message': 'Vet approved successfully.'})


class RejectVetView(APIView):
    permission_classes = [IsAdminUserRole]

    def post(self, request, vet_id):
        vet = get_object_or_404(VetProfile, id=vet_id)
        reason = request.data.get('reason', 'Your application did not meet our requirements.')
        from apps.notifications.models import Notification
        Notification.send(
            user=vet.user,
            title='Application Not Approved',
            message=f'Your veterinarian application was not approved. Reason: {reason}',
            notification_type='system',
        )
        vet.user.is_active = False
        vet.user.save()
        return Response({'message': 'Vet rejected.'})


# ─── User Management ──────────────────────────────────────────────────────────

class UserListView(APIView):
    permission_classes = [IsAdminUserRole]

    def get(self, request):
        role = request.query_params.get('role')
        qs = User.objects.select_related('profile').order_by('-created_at')
        if role:
            qs = qs.filter(role=role)
        data = [
            {
                'id': u.id,
                'email': u.email,
                'role': u.role,
                'name': getattr(u, 'profile', None) and u.profile.name,
                'email_verified': u.email_verified,
                'is_active': u.is_active,
                'created_at': u.created_at,
            }
            for u in qs[:100]
        ]
        return Response(data)


class ToggleUserActiveView(APIView):
    permission_classes = [IsAdminUserRole]

    def post(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        if user.role == 'admin':
            return Response({'error': 'Cannot deactivate admin users.'}, status=400)
        user.is_active = not user.is_active
        user.save()
        return Response({'message': f'User {"activated" if user.is_active else "deactivated"}.'})


# ─── Analytics ────────────────────────────────────────────────────────────────

class AnalyticsDashboardView(APIView):
    permission_classes = [IsAdminUserRole]

    def get(self, request):
        from django.db.models import Sum, Count

        total_users = User.objects.count()
        total_owners = User.objects.filter(role='owner').count()
        total_vets = User.objects.filter(role='vet').count()
        approved_vets = VetProfile.objects.filter(approved=True).count()
        pending_vets = VetProfile.objects.filter(approved=False).count()
        total_pets = Pet.objects.count()
        total_payments = Payment.objects.filter(payment_status='succeeded').aggregate(
            total=Sum('amount'), count=Count('id')
        )
        active_subscriptions = {
            'basic': Subscription.objects.filter(active=True, plan_name='basic').count(),
            'standard': Subscription.objects.filter(active=True, plan_name='standard').count(),
            'premium': Subscription.objects.filter(active=True, plan_name='premium').count(),
        }

        return Response({
            'users': {
                'total': total_users,
                'owners': total_owners,
                'vets': total_vets,
            },
            'vets': {
                'approved': approved_vets,
                'pending': pending_vets,
            },
            'pets': total_pets,
            'revenue': {
                'total': str(total_payments['total'] or 0),
                'transactions': total_payments['count'] or 0,
            },
            'subscriptions': active_subscriptions,
        })


urlpatterns = [
    path('vets/pending/', PendingVetListView.as_view(), name='pending-vets'),
    path('vets/<int:vet_id>/approve/', ApproveVetView.as_view(), name='approve-vet'),
    path('vets/<int:vet_id>/reject/', RejectVetView.as_view(), name='reject-vet'),
    path('users/', UserListView.as_view(), name='admin-users'),
    path('users/<int:user_id>/toggle-active/', ToggleUserActiveView.as_view(), name='toggle-user'),
    path('analytics/', AnalyticsDashboardView.as_view(), name='analytics'),
]

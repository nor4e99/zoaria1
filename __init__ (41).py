from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, UserProfile, EmailVerificationToken, PasswordResetToken
from .serializers import (
    RegisterOwnerSerializer,
    RegisterVetSerializer,
    ZoariaTokenObtainPairSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
)


def send_verification_email(user):
    """Send email verification link."""
    token_obj, _ = EmailVerificationToken.objects.update_or_create(
        user=user,
        defaults={
            'expires_at': timezone.now() + timedelta(hours=24),
        }
    )
    verify_url = f"{settings.FRONTEND_URL}/verify-email?token={token_obj.token}"
    send_mail(
        subject='Verify your ZOARIA account',
        message=f'Click to verify your email: {verify_url}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )


class RegisterOwnerView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterOwnerSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_verification_email(user)
            return Response(
                {'message': 'Registration successful. Please verify your email.'},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterVetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterVetSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_verification_email(user)
            # Handle license upload separately
            if 'license' in request.FILES:
                from apps.vets.models import VetProfile
                vet_profile = VetProfile.objects.get(user=user)
                # Store as file path or upload to cloud
                vet_profile.license_document = str(request.FILES['license'])
                vet_profile.save()
            return Response(
                {'message': 'Vet registration submitted. Verify email and await admin approval.'},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get('token')
        if not token:
            return Response({'error': 'Token is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token_obj = EmailVerificationToken.objects.select_related('user').get(token=token)
        except EmailVerificationToken.DoesNotExist:
            return Response({'error': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)

        if token_obj.is_expired():
            return Response({'error': 'Token has expired. Please request a new one.'}, status=status.HTTP_400_BAD_REQUEST)

        user = token_obj.user
        user.email_verified = True
        user.save(update_fields=['email_verified'])
        # Fire async welcome email
        try:
            from apps.tasks.reminders import send_welcome_email
            send_welcome_email.delay(user.id)
        except Exception:
            pass
        token_obj.delete()

        return Response({'message': 'Email verified successfully. You can now log in.'})


class ResendVerificationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            if user.email_verified:
                return Response({'message': 'Email already verified.'})
            send_verification_email(user)
            return Response({'message': 'Verification email sent.'})
        except User.DoesNotExist:
            # Don't reveal if email exists
            return Response({'message': 'If that email exists, a verification link has been sent.'})


class ZoariaTokenObtainPairView(TokenObtainPairView):
    serializer_class = ZoariaTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            # Check email is verified
            email = request.data.get('email')
            try:
                user = User.objects.get(email=email)
                if not user.email_verified:
                    return Response(
                        {'error': 'Please verify your email before logging in.'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except User.DoesNotExist:
                pass
        return response


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
            token_obj = PasswordResetToken.objects.create(
                user=user,
                expires_at=timezone.now() + timedelta(hours=1)
            )
            reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token_obj.token}"
            send_mail(
                subject='Reset your ZOARIA password',
                message=f'Click to reset your password: {reset_url}\n\nThis link expires in 1 hour.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
        except User.DoesNotExist:
            pass  # Don't reveal existence

        return Response({'message': 'If that email exists, a reset link has been sent.'})


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            token_obj = PasswordResetToken.objects.select_related('user').get(
                token=serializer.validated_data['token'],
                used=False
            )
        except PasswordResetToken.DoesNotExist:
            return Response({'error': 'Invalid or already used token.'}, status=status.HTTP_400_BAD_REQUEST)

        if token_obj.is_expired():
            return Response({'error': 'Token has expired.'}, status=status.HTTP_400_BAD_REQUEST)

        user = token_obj.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        token_obj.used = True
        token_obj.save()

        return Response({'message': 'Password reset successfully.'})


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'error': 'Current password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': 'Password updated successfully.'})


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logged out successfully.'})
        except Exception:
            return Response({'error': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)


class MeView(APIView):
    """Returns current user info including profile and subscription."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile, _ = UserProfile.objects.get_or_create(user=user)

        # Get active subscription
        subscription = None
        try:
            from apps.payments.models import Subscription
            sub = Subscription.objects.filter(user=user, active=True).order_by('-start_date').first()
            if sub:
                subscription = {'plan': sub.plan_name, 'end_date': sub.end_date}
        except Exception:
            pass

        return Response({
            'id': user.id,
            'email': user.email,
            'role': user.role,
            'email_verified': user.email_verified,
            'profile': UserProfileSerializer(profile).data,
            'subscription': subscription or {'plan': 'basic'},
        })

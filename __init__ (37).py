from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterOwnerView,
    RegisterVetView,
    VerifyEmailView,
    ResendVerificationView,
    ZoariaTokenObtainPairView,
    ForgotPasswordView,
    ResetPasswordView,
    ProfileView,
    ChangePasswordView,
    LogoutView,
    MeView,
)

urlpatterns = [
    # Registration
    path('register/owner/', RegisterOwnerView.as_view(), name='register-owner'),
    path('register/vet/', RegisterVetView.as_view(), name='register-vet'),

    # Email verification
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('resend-verification/', ResendVerificationView.as_view(), name='resend-verification'),

    # JWT tokens
    path('login/', ZoariaTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # Password management
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),

    # Profile
    path('profile/', ProfileView.as_view(), name='profile'),
    path('me/', MeView.as_view(), name='me'),
]

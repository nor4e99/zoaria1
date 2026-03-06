from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
import uuid


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('email_verified', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model mapped to zoaria_full_platform_schema.sql `users` table.
    Extends with Django auth fields needed for admin/staff access.
    """
    ROLE_CHOICES = [
        ('owner', 'Pet Owner'),
        ('vet', 'Veterinarian'),
        ('admin', 'Administrator'),
    ]

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='owner')
    email_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f'{self.email} ({self.role})'

    @property
    def is_owner(self):
        return self.role == 'owner'

    @property
    def is_vet(self):
        return self.role == 'vet'

    @property
    def is_admin_user(self):
        return self.role == 'admin'


class UserProfile(models.Model):
    """
    Maps to `user_profiles` table in the schema.
    """
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('bg', 'Bulgarian'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    profile_image = models.TextField(blank=True)  # URL (Cloudinary)
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='en')

    class Meta:
        db_table = 'user_profiles'

    def __str__(self):
        return f'Profile: {self.user.email}'


class EmailVerificationToken(models.Model):
    """
    Stores email verification tokens for the registration flow.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='verification_token')
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = 'email_verification_tokens'

    def is_expired(self):
        return timezone.now() > self.expires_at


class PasswordResetToken(models.Model):
    """
    One-time tokens for the forgot-password flow.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    class Meta:
        db_table = 'password_reset_tokens'

    def is_expired(self):
        return timezone.now() > self.expires_at

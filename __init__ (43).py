from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User, UserProfile


# ─── Auth serializers ─────────────────────────────────────────────────────────

class RegisterOwnerSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)
    name = serializers.CharField(max_length=150, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'confirm_password', 'name']

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'Passwords do not match.'})
        try:
            validate_password(attrs['password'])
        except DjangoValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        name = validated_data.pop('name')
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            role='owner',
        )
        UserProfile.objects.create(user=user, name=name)
        return user


class RegisterVetSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)
    name = serializers.CharField(max_length=150, write_only=True)
    # License is handled separately via VetProfile creation
    specialization = serializers.CharField(required=False, allow_blank=True)
    clinic_name = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'confirm_password', 'name', 'specialization', 'clinic_name']

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'Passwords do not match.'})
        try:
            validate_password(attrs['password'])
        except DjangoValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        name = validated_data.pop('name')
        specialization = validated_data.pop('specialization', '')
        clinic_name = validated_data.pop('clinic_name', '')

        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            role='vet',
        )
        UserProfile.objects.create(user=user, name=name)

        # Import here to avoid circular
        from apps.vets.models import VetProfile
        VetProfile.objects.create(
            user=user,
            specialization=specialization,
            clinic_name=clinic_name,
            approved=False,
        )
        return user


class ZoariaTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Adds user info to JWT token response."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['role'] = user.role
        token['email_verified'] = user.email_verified
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id': self.user.id,
            'email': self.user.email,
            'role': self.user.role,
            'email_verified': self.user.email_verified,
        }
        return data


# ─── Profile serializers ──────────────────────────────────────────────────────

class UserProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    role = serializers.CharField(source='user.role', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['email', 'role', 'name', 'bio', 'location', 'profile_image', 'language']

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_new_password']:
            raise serializers.ValidationError({'confirm_new_password': 'Passwords do not match.'})
        try:
            validate_password(attrs['new_password'])
        except DjangoValidationError as e:
            raise serializers.ValidationError({'new_password': list(e.messages)})
        return attrs


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_new_password']:
            raise serializers.ValidationError({'confirm_new_password': 'Passwords do not match.'})
        return attrs

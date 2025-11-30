from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from .models import User, Address, UserActivity


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'first_name', 'last_name', 'phone_number',
            'password', 'password_confirm', 'newsletter_subscription'
        )

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Passwords don't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                              email=email, password=password)
            if not user:
                raise serializers.ValidationError(_('Invalid credentials.'))
            if not user.is_active:
                raise serializers.ValidationError(_('Account is disabled.'))
        else:
            raise serializers.ValidationError(_('Must include "email" and "password".'))

        attrs['user'] = user
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    has_complete_profile = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'date_of_birth', 'avatar', 'bio',
            'address_line1', 'address_line2', 'city', 'state',
            'country', 'postal_code', 'newsletter_subscription',
            'marketing_emails', 'sms_notifications', 'is_email_verified',
            'has_complete_profile', 'date_joined', 'last_login'
        )
        read_only_fields = ('id', 'email', 'is_email_verified', 'date_joined', 'last_login')


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'phone_number', 'date_of_birth',
            'avatar', 'bio', 'address_line1', 'address_line2', 'city',
            'state', 'country', 'postal_code', 'newsletter_subscription',
            'marketing_emails', 'sms_notifications'
        )


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, min_length=8, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords don't match."})
        return attrs


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = (
            'id', 'address_type', 'first_name', 'last_name', 'company',
            'address_line1', 'address_line2', 'city', 'state', 'country',
            'postal_code', 'phone_number', 'is_default', 'created_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate(self, attrs):
        # Ensure only one default address per type per user
        if attrs.get('is_default', False):
            user = self.context['request'].user
            address_type = attrs.get('address_type')
            
            # Remove default from other addresses of same type
            Address.objects.filter(
                user=user, 
                address_type__in=[address_type, 'both'],
                is_default=True
            ).update(is_default=False)
        
        return attrs


class UserActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserActivity
        fields = ('activity_type', 'description', 'ip_address', 'user_agent', 'created_at')
        read_only_fields = ('user', 'activity_type', 'description', 'ip_address', 'user_agent', 'created_at')


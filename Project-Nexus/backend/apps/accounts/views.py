from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import login, logout
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import uuid

from .models import User, Address, UserActivity, EmailVerification, PasswordResetToken
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer,
    UserUpdateSerializer, ChangePasswordSerializer, AddressSerializer,
    UserActivitySerializer
)
from .permissions import IsOwnerOrReadOnly


class UserRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Log user activity
            UserActivity.objects.create(
                user=user,
                activity_type='registration',
                description='User registered successfully',
                ip_address=self.get_client_ip(request)
            )
            
            # Send email verification
            self.send_verification_email(user, request)
            
            return Response({
                'message': 'User registered successfully. Please check your email for verification.',
                'user_id': user.id
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def send_verification_email(self, user, request):
        token = str(uuid.uuid4())
        expires_at = timezone.now() + timezone.timedelta(hours=24)
        
        EmailVerification.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )
        
        verification_url = f"{settings.FRONTEND_URL}/verify-email/{token}/"
        
        send_mail(
            'Verify your email address',
            f'Please click the link to verify your email: {verification_url}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )


class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            
            # Log user activity
            UserActivity.objects.create(
                user=user,
                activity_type='login',
                description='User logged in successfully',
                ip_address=self.get_client_ip(request)
            )
            
            user_serializer = UserProfileSerializer(user)
            return Response({
                'message': 'Login successful',
                'user': user_serializer.data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class UserLogoutView(APIView):
    def post(self, request):
        # Log user activity
        if request.user.is_authenticated:
            UserActivity.objects.create(
                user=request.user,
                activity_type='logout',
                description='User logged out',
                ip_address=self.get_client_ip(request)
            )
        
        logout(request)
        return Response({'message': 'Logout successful'})

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            
            # Check current password
            if not user.check_password(serializer.validated_data['current_password']):
                return Response(
                    {'current_password': 'Current password is incorrect'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Set new password
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            # Log user activity
            UserActivity.objects.create(
                user=user,
                activity_type='password_change',
                description='User changed password successfully',
                ip_address=self.get_client_ip(request)
            )
            
            return Response({'message': 'Password changed successfully'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class AddressListCreateView(generics.ListCreateAPIView):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


class UserActivityListView(generics.ListAPIView):
    serializer_class = UserActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserActivity.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_email(request, token):
    try:
        verification = EmailVerification.objects.get(token=token, is_used=False)
        
        if verification.is_valid():
            user = verification.user
            user.is_email_verified = True
            user.save()
            
            verification.is_used = True
            verification.save()
            
            # Log user activity
            UserActivity.objects.create(
                user=user,
                activity_type='email_verification',
                description='User verified email address'
            )
            
            return Response({'message': 'Email verified successfully'})
        else:
            return Response(
                {'error': 'Verification link has expired'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
    except EmailVerification.DoesNotExist:
        return Response(
            {'error': 'Invalid verification link'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def request_password_reset(request):
    email = request.data.get('email')
    
    try:
        user = User.objects.get(email=email)
        token = str(uuid.uuid4())
        expires_at = timezone.now() + timezone.timedelta(hours=1)
        
        PasswordResetToken.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )
        
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{token}/"
        
        send_mail(
            'Password Reset Request',
            f'Click the link to reset your password: {reset_url}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        
        return Response({'message': 'Password reset email sent'})
        
    except User.DoesNotExist:
        # Don't reveal whether email exists
        return Response({'message': 'If the email exists, a reset link has been sent'})


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def reset_password(request, token):
    new_password = request.data.get('new_password')
    confirm_password = request.data.get('confirm_password')
    
    if new_password != confirm_password:
        return Response(
            {'error': 'Passwords do not match'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        reset_token = PasswordResetToken.objects.get(token=token, is_used=False)
        
        if reset_token.is_valid():
            user = reset_token.user
            user.set_password(new_password)
            user.save()
            
            reset_token.is_used = True
            reset_token.save()
            
            # Log user activity
            UserActivity.objects.create(
                user=user,
                activity_type='password_reset',
                description='User reset password via email'
            )
            
            return Response({'message': 'Password reset successfully'})
        else:
            return Response(
                {'error': 'Reset link has expired'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
    except PasswordResetToken.DoesNotExist:
        return Response(
            {'error': 'Invalid reset link'},
            status=status.HTTP_400_BAD_REQUEST
        )
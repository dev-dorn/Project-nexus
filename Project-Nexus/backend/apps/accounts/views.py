from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import login, logout
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import uuid

from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import User, Address, UserActivity, EmailVerification, PasswordResetToken
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer,
    UserUpdateSerializer, ChangePasswordSerializer, AddressSerializer,
    UserActivitySerializer
)
from .permissions import IsOwnerOrReadOnly
from .utils import get_client_ip   # <--- new helper


class UserRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        request=UserRegistrationSerializer,
        responses={201: OpenApiTypes.OBJECT}
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Log
            UserActivity.objects.create(
                user=user,
                activity_type='registration',
                description='User registered successfully',
                ip_address=get_client_ip(request)
            )

            # Create verification token
            self.send_verification_email(user, request)

            return Response({
                'message': 'User registered successfully. Check your email to verify.',
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_verification_email(self, user, request):
        token = str(uuid.uuid4())
        expires_at = timezone.now() + timezone.timedelta(hours=24)

        EmailVerification.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )

        backend_url = f"{settings.BACKEND_URL}/api/auth/verify-email/{token}/"

        send_mail(
            'Verify your email address',
            f'Click the link to verify your account: {backend_url}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=True,
        )


class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        request=UserLoginSerializer,
        responses={200: UserProfileSerializer}
    )
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']

            login(request, user)

            UserActivity.objects.create(
                user=user,
                activity_type='login',
                description='User logged in successfully',
                ip_address=get_client_ip(request)
            )

            return Response({
                'message': 'Login successful',
                'user': UserProfileSerializer(user).data
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={200: OpenApiTypes.OBJECT}
    )
    def post(self, request):
        UserActivity.objects.create(
            user=request.user,
            activity_type='logout',
            description='User logged out',
            ip_address=get_client_ip(request)
        )

        logout(request)
        return Response({'message': 'Logout successful'})


@extend_schema(responses=UserProfileSerializer)
class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=ChangePasswordSerializer,
        responses={200: OpenApiTypes.OBJECT}
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user

            if not user.check_password(serializer.validated_data['current_password']):
                return Response(
                    {'current_password': 'Wrong current password'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user.set_password(serializer.validated_data['new_password'])
            user.save()

            UserActivity.objects.create(
                user=user,
                activity_type='password_change',
                description='User changed password',
                ip_address=get_client_ip(request)
            )

            return Response({'message': 'Password updated successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



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

@extend_schema(
    parameters=[OpenApiParameter("token", OpenApiTypes.STR)],
    responses={200: OpenApiTypes.OBJECT}
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_email(request, token):
    try:
        obj = EmailVerification.objects.get(token=token, is_used=False)

        if obj.expires_at < timezone.now():
            return Response({'error': 'Token expired'}, status=400)

        obj.is_used = True
        obj.save()

        user = obj.user
        user.is_email_verified = True
        user.save()

        UserActivity.objects.create(
            user=user,
            activity_type='email_verification',
            description='Email verified'
        )

        return Response({'message': 'Email verified successfully'})
    except EmailVerification.DoesNotExist:
        return Response({'error': 'Invalid token'}, status=400)


@extend_schema(
    request={'type': 'object', 'properties': {'email': {'type': 'string'}}},
    responses={200: OpenApiTypes.OBJECT}
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def request_password_reset(request):
    email = request.data.get('email')

    try:
        user = User.objects.get(email=email)

        # invalidate previous tokens
        PasswordResetToken.objects.filter(user=user, is_used=False).update(is_used=True)

        token = str(uuid.uuid4())
        expires_at = timezone.now() + timezone.timedelta(hours=1)

        PasswordResetToken.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )

        backend_url = f"{settings.BACKEND_URL}/api/auth/password-reset/{token}/"

        send_mail(
            'Reset your password',
            f'Click to reset: {backend_url}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=True,
        )

        return Response({'message': 'If the email exists, a link was sent'})
    except User.DoesNotExist:
        return Response({'message': 'If the email exists, a link was sent'})



@extend_schema(
    parameters=[OpenApiParameter("token", OpenApiTypes.STR)],
    request={
        "type": "object",
        "properties": {
            "new_password": {"type": "string"},
            "confirm_password": {"type": "string"},
        }
    },
    responses={200: OpenApiTypes.OBJECT}
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def reset_password(request, token):
    new_password = request.data.get('new_password')
    confirm_password = request.data.get('confirm_password')

    if new_password != confirm_password:
        return Response({'error': 'Passwords do not match'}, status=400)

    try:
        token_obj = PasswordResetToken.objects.get(token=token, is_used=False)

        if token_obj.expires_at < timezone.now():
            return Response({'error': 'Token expired'}, status=400)

        user = token_obj.user
        user.set_password(new_password)
        user.save()

        token_obj.is_used = True
        token_obj.save()

        UserActivity.objects.create(
            user=user,
            activity_type='password_reset',
            description='Password reset via token'
        )

        return Response({'message': 'Password reset successful'})
    except PasswordResetToken.DoesNotExist:
        return Response({'error': 'Invalid token'}, status=400)

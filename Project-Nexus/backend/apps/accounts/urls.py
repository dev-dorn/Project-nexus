from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

urlpatterns = [
    # Authentication
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    
    # Profile
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    
    # Addresses
    path('addresses/', views.AddressListCreateView.as_view(), name='address-list'),
    path('addresses/<int:pk>/', views.AddressDetailView.as_view(), name='address-detail'),
    
    # Activities
    path('activities/', views.UserActivityListView.as_view(), name='user-activities'),
    
    # Email Verification
    path('verify-email/<str:token>/', views.verify_email, name='verify-email'),
    
    # Password Reset
    path('password-reset/', views.request_password_reset, name='password-reset-request'),
    path('password-reset/<str:token>/', views.reset_password, name='password-reset-confirm'),
]
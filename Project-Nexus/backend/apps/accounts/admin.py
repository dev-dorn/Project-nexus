from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Address, EmailVerification, PasswordResetToken, UserActivity


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_email_verified', 'is_active', 'date_joined')
    list_filter = ('is_email_verified', 'is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {
            'fields': (
                'first_name', 'last_name', 'phone_number', 'date_of_birth',
                'avatar', 'bio'
            )
        }),
        (_('Address'), {
            'fields': (
                'address_line1', 'address_line2', 'city', 'state',
                'country', 'postal_code'
            )
        }),
        #_ is the gettext- it wraps the string so it can be translated into different languages
        (_('Preferences'), {
            'fields': (
                'newsletter_subscription', 'marketing_emails', 'sms_notifications'
            )
        }),
        (_('Permissions'), {
            'fields': (
                'is_active', 'is_staff', 'is_superuser', 'is_email_verified',
                'groups', 'user_permissions'
            )
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ('date_joined', 'last_login', 'updated_at')


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'address_type', 'city', 'country', 'is_default', 'created_at')
    list_filter = ('address_type', 'country', 'is_default', 'created_at')
    search_fields = ('user__email', 'first_name', 'last_name', 'city', 'country')
    raw_id_fields = ('user',)


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at', 'expires_at', 'is_used')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__email', 'token')
    readonly_fields = ('created_at', 'expires_at')
    raw_id_fields = ('user',)


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at', 'expires_at', 'is_used')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__email', 'token')
    readonly_fields = ('created_at', 'expires_at')
    raw_id_fields = ('user',)


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'ip_address', 'created_at')
    list_filter = ('activity_type', 'created_at')
    search_fields = ('user__email', 'activity_type', 'description')
    readonly_fields = ('created_at',)
    raw_id_fields = ('user',)
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
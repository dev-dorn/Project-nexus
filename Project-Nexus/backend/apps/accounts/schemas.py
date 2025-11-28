from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

# Registration Schema
registration_schema = swagger_auto_schema(
    operation_description="Register a new user account",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['email', 'first_name', 'last_name', 'password', 'password_confirm'],
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
            'first_name': openapi.Schema(type=openapi.TYPE_STRING),
            'last_name': openapi.Schema(type=openapi.TYPE_STRING),
            'phone_number': openapi.Schema(type=openapi.TYPE_STRING),
            'password': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD),
            'password_confirm': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD),
            'newsletter_subscription': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
        }
    ),
    responses={
        201: openapi.Response(
            description="User registered successfully",
            examples={
                "application/json": {
                    "message": "User registered successfully. Please check your email for verification.",
                    "user_id": 1
                }
            }
        ),
        400: "Bad Request - Invalid input data"
    }
)

# Login Schema
login_schema = swagger_auto_schema(
    operation_description="Login user with email and password",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['email', 'password'],
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
            'password': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD),
        }
    ),
    responses={
        200: openapi.Response(
            description="Login successful",
            examples={
                "application/json": {
                    "message": "Login successful",
                    "user": {
                        "id": 1,
                        "email": "user@example.com",
                        "first_name": "John",
                        "last_name": "Doe",
                        "full_name": "John Doe",
                        # ... other user fields
                    }
                }
            }
        ),
        400: "Bad Request - Invalid credentials"
    }
)

# Change Password Schema
change_password_schema = swagger_auto_schema(
    operation_description="Change user password",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['current_password', 'new_password', 'confirm_password'],
        properties={
            'current_password': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD),
            'new_password': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD),
            'confirm_password': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD),
        }
    ),
    responses={
        200: openapi.Response(
            description="Password changed successfully",
            examples={
                "application/json": {
                    "message": "Password changed successfully"
                }
            }
        ),
        400: "Bad Request - Invalid input data or incorrect current password"
    }
)

# Address Schema
address_schema = swagger_auto_schema(
    operation_description="Create a new address for the user",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['address_type', 'first_name', 'last_name', 'address_line1', 'city', 'country', 'postal_code'],
        properties={
            'address_type': openapi.Schema(
                type=openapi.TYPE_STRING,
                enum=['billing', 'shipping', 'both'],
                description="Type of address"
            ),
            'first_name': openapi.Schema(type=openapi.TYPE_STRING),
            'last_name': openapi.Schema(type=openapi.TYPE_STRING),
            'company': openapi.Schema(type=openapi.TYPE_STRING),
            'address_line1': openapi.Schema(type=openapi.TYPE_STRING),
            'address_line2': openapi.Schema(type=openapi.TYPE_STRING),
            'city': openapi.Schema(type=openapi.TYPE_STRING),
            'state': openapi.Schema(type=openapi.TYPE_STRING),
            'country': openapi.Schema(type=openapi.TYPE_STRING),
            'postal_code': openapi.Schema(type=openapi.TYPE_STRING),
            'phone_number': openapi.Schema(type=openapi.TYPE_STRING),
            'is_default': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
        }
    )
)

# Password Reset Request Schema
password_reset_request_schema = swagger_auto_schema(
    operation_description="Request password reset email",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['email'],
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
        }
    ),
    responses={
        200: openapi.Response(
            description="Reset email sent if account exists",
            examples={
                "application/json": {
                    "message": "If the email exists, a reset link has been sent"
                }
            }
        )
    }
)

# Password Reset Confirm Schema
password_reset_confirm_schema = swagger_auto_schema(
    operation_description="Reset password with token",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['new_password', 'confirm_password'],
        properties={
            'new_password': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD),
            'confirm_password': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD),
        }
    ),
    responses={
        200: openapi.Response(
            description="Password reset successful",
            examples={
                "application/json": {
                    "message": "Password reset successfully"
                }
            }
        ),
        400: "Bad Request - Invalid token or passwords don't match"
    }
)
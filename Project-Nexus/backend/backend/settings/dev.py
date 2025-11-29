import sys
from .base import *

# Hardcode development settings
SECRET_KEY = 'django-insecure-development-secret-key'
DEBUG = True
ALLOWED_HOSTS = ['*']

# Additional apps for development
INSTALLED_APPS += [
    'django_extensions',

]

# Make sure MIDDLEWARE is defined by importing from base, then modify it
MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')

# Debug toolbar configuration
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

# Email configuration for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Database configuration for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ecommerce_dev',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'db',
        'PORT': '5432',
    }
}

# Configure Django Debug Toolbar
def show_toolbar(request):
    return True

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': show_toolbar,
}

# CORS settings for development
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Media files configuration for development
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Static files configuration for development
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Add backend URL for email verification
BACKEND_URL = 'http://localhost:8000'

if 'test' in sys.argv:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }

    PASSWORD_HASHERS = [
        'django.contrib.auth.hashers.MD5PasswordHasher',
    ]

ROOT_URLCONF = 'backend.urls'

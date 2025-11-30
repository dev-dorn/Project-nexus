import os
from pathlib import Path
from datetime import timedelta
import dj_database_url


BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-development-secret-key-change-in-production')
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://your-frontend-domain.onrender.com",  # Add your frontend Render URL
]

CORS_ALLOW_ALL_ORIGINS = DEBUG 
# DRF Spectacular Settings
SPECTACULAR_SETTINGS = {
    'TITLE': 'Nexus E-Commerce API',
    'DESCRIPTION': """
    # Nexus E-Commerce Platform API
    
    A comprehensive e-commerce platform built with Django REST Framework.
    
    ## Features
    
    - **User Authentication & Management** - JWT-based authentication with email verification
    - **Product Catalog** - Complete product management with categories, brands, and variants
    - **Shopping Cart** - Session-based cart functionality
    - **Order Management** - Complete order processing workflow
    - **Payment Integration** - Multiple payment gateway support
    - **Reviews & Ratings** - Product reviews with verification system
    
    ## Authentication
    
    This API uses JWT (JSON Web Tokens) for authentication. 
    To authenticate your requests, include the following header:
    
    ```
    Authorization: Bearer <your_access_token>
    ```
    
    ## Rate Limiting
    
    - **Anonymous users**: 100 requests per hour
    - **Authenticated users**: 1000 requests per hour
    - **Premium users**: 5000 requests per hour
    
    ## Versioning
    
    Current API version: v1
    """,
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX': '/api/v1/',
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
        'filter': True,
        'syntaxHighlight': True,
        'docExpansion': 'none',
        'tagsSorter': 'alpha',
        'operationsSorter': 'alpha',
        'defaultModelsExpandDepth': 2,
        'displayRequestDuration': True,
    },
    'COMPONENT_SPLIT_REQUEST': True,
    'SORT_OPERATIONS': False,
    'ENUM_NAME_OVERRIDES': {
        'ProductStatusEnum': 'apps.products.models.Product.STATUS_CHOICES',
        'AddressTypeEnum': 'apps.accounts.models.Address.ADDRESS_TYPE_CHOICES',
        'UserRoleEnum': ['customer', 'vendor', 'admin'],
    },
    'POSTPROCESSING_HOOKS': [
        'drf_spectacular.hooks.postprocess_schema_enums',
    ],
    'TAGS': [
        {
            'name': 'Authentication',
            'description': 'User registration, login, logout, and token management'
        },
        {
            'name': 'Users',
            'description': 'User profiles, addresses, and account management'
        },
        {
            'name': 'Products',
            'description': 'Product catalog, categories, brands, and search'
        },
        {
            'name': 'Cart',
            'description': 'Shopping cart operations'
        },
        {
            'name': 'Orders',
            'description': 'Order management and tracking'
        },
        {
            'name': 'Payments',
            'description': 'Payment processing and history'
        },
        {
            'name': 'Reviews',
            'description': 'Product reviews and ratings'
        },
    ],
    'EXTENSIONS_INFO': {
        'x-logo': {
            'url': '/static/logo.png',
            'backgroundColor': '#FFFFFF',
            'altText': 'Nexus E-Commerce API'
        }
    },
    'EXTERNAL_DOCS': {
        'description': 'Project Documentation',
        'url': 'https://docs.nexus-project.com',
    },
    'CONTACT': {
        'name': 'API Support',
        'email': 'api-support@nexus-project.com',
        'url': 'https://support.nexus-project.com'
    },
    'LICENSE': {
        'name': 'MIT License',
        'url': 'https://opensource.org/licenses/MIT',
    },
    'SERVERS': [
        {
            'url': 'http://localhost:8000',
            'description': 'Development server'
        },
        {
            'url': 'https://api.nexus-project.com',
            'description': 'Production server'
        },
    ],
}

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    },
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production'),
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    'JTI_CLAIM': 'jti',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this line
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
]
# Installed Apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'rest_framework',
    'corsheaders',
    'drf_spectacular',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'django_filters',
    'debug_toolbar',
    
    # Local apps
    'apps.accounts',
    'apps.products',
    'apps.cart',
    'apps.core',
    'apps.middleware',
    'apps.orders',
    'apps.payments',
    'apps.reviews',
]

# Custom user model
AUTH_USER_MODEL = 'accounts.User'
BACKEND_URL = os.environ.get('BACKEND_URL', 'http://localhost:8000')
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # Add custom template directories if any
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,  # This enables loading templates from app directories
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=not DEBUG
    )
}
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = 'DENY'
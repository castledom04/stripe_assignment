"""
Django settings for stripe_assignment project.

Generated by 'django-admin startproject' using Django 3.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
from datetime import timedelta
from pathlib import Path


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY")


# SECURITY WARNING: don't run with debug turned on in production!
# -------------------------------------------------------------------
ENVIRONMENT = os.environ.get("ENVIRONMENT")
if ENVIRONMENT in ("production", "staging"):
    DEBUG = False
else:
    DEBUG = True


# Configure allowed hosts to increase security
# -------------------------------------------------------------------
ALLOWED_HOSTS = []
ALLOWED_HOSTS += os.environ.get("DJANGO_ALLOWED_HOSTS").split(',')


# Configure CORS
# https://github.com/adamchainz/django-cors-headers
# -------------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "https://api.superdomain.com",
]
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^http://\w+\.superdomain\.com$",
]
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True


# Application definition
# -------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party Apps
    'rest_framework',
    'django_extensions',
    'corsheaders',
    'drf_spectacular',
    # Local Apps
    'api'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTH_USER_MODEL = "api.User"

ROOT_URLCONF = 'stripe_assignment.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
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

WSGI_APPLICATION = 'stripe_assignment.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
# -------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": os.environ.get("SQL_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.environ.get("SQL_DATABASE", os.path.join(BASE_DIR, "db.sqlite3")),
        "USER": os.environ.get("SQL_USER", "user"),
        "PASSWORD": os.environ.get("SQL_PASSWORD", "password"),
        "HOST": os.environ.get("SQL_HOST", "localhost"),
        "PORT": os.environ.get("SQL_PORT", "5432"),
    }
}


# Django Rest Framework configuration
# https://www.django-rest-framework.org/api-guide/settings/
# -------------------------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated'
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'EXCEPTION_HANDLER': 'api.exception_handler.app_exception_handler',
}


# Json Web Token verifying key
# -------------------------------------------------------------------
JWT_SIGNING_KEY = ""
JWT_VERIFYING_KEY = ""
with open('jwt-signing-key.key', mode='r') as private_key_file:
    JWT_SIGNING_KEY = private_key_file.read()
with open('jwt-verifying-key.key.pub', mode='r') as public_key_file:
    JWT_VERIFYING_KEY = public_key_file.read()


ACCESS_TOKEN_MINUTES = int(os.environ.get("ACCESS_TOKEN_MINUTES", 5))
REFRESH_TOKEN_MINUTES = int(os.environ.get("REFRESH_TOKEN_MINUTES", 1440))
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=ACCESS_TOKEN_MINUTES),
    'REFRESH_TOKEN_LIFETIME': timedelta(minutes=REFRESH_TOKEN_MINUTES),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,
    'ALGORITHM': 'RS256',
    'SIGNING_KEY': JWT_SIGNING_KEY,
    'VERIFYING_KEY': JWT_VERIFYING_KEY,
    'AUTH_HEADER_TYPES': ('JWT',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'JTI_CLAIM': 'jti',
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators
# -------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/
# -------------------------------------------------------------------

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/
# -------------------------------------------------------------------

STATIC_URL = '/static/'


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field
# -------------------------------------------------------------------

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



# Swagger API docs configuration
# https://github.com/tfranzel/drf-spectacular
# -------------------------------------------------------------------
SPECTACULAR_SETTINGS = {
    'TITLE': 'Your Project API',
    'DESCRIPTION': 'Your project description',
    'VERSION': '1.0.0',
    # OTHER SETTINGS
}


# Stripe settings
# -------------------------------------------------------------------
STRIPE_API_SECRET = os.environ.get("STRIPE_API_SECRET", '')
STRIPE_BASIC_PRODUCT_PRICE_ID = os.environ.get("STRIPE_BASIC_PRODUCT_PRICE_ID", '')
STRIPE_PRO_PRODUCT_PRICE_ID = os.environ.get("STRIPE_PRO_PRODUCT_PRICE_ID", '')
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", '')
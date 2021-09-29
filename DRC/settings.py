"""

Generated by 'django-admin startproject' using Django 3.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
import os
import socket
from datetime import timedelta
from pathlib import Path

from django.core.management.commands import runserver

from .config.loggerConfig import LOGGING as LOG_CONFIG
from django.contrib import staticfiles
from dotenv import load_dotenv
from DRC.config.DRCConfig import Configuration

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent

print(os.environ)
print(os.environ.get('MAIL_PASSWORD'))

CONFIG = Configuration(BASE_DIR / 'config.yaml')
PROJECT_NAME = CONFIG.PROJECT_NAME
SERVER_PORT = os.environ.get('PORT') or 8000
DOMAIN_NAME = os.environ.get('DOMAIN_NAME') or f'localhost:{SERVER_PORT}'


runserver.default_port = SERVER_PORT

SECRET_KEY = os.environ.get('SECRET_KEY') or '$@#ij9b#15$7_#jg(f$9mws(x189f0fw28ho$zqg!^8d*b8e^t'

# Configuration
ENV_TYPE = os.environ.get('SERVER_ENV_TYPE') or ''
if ENV_TYPE.upper() == 'TEST':
    DEBUG_FLAG = False if (os.environ.get('DJANGO_DEBUG_MODE').upper() == 'FALSE') else True
    DBConfig = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db1.sqlite3',
    }
else:
    DEBUG_FLAG = True if (os.environ.get('DJANGO_DEBUG_MODE').upper() == 'TRUE') else False
    DBConfig = {
        'ENGINE': CONFIG.DB.ENGINE,
        'NAME': CONFIG.DB.NAME,
        'USER': os.environ.get('DB_USERNAME'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': CONFIG.DB.HOST,
        'PORT': CONFIG.DB.PORT,
    }
print(f'Environment Type: {ENV_TYPE} | Debug: {DEBUG_FLAG} | DBConfig: {DBConfig}')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = DEBUG_FLAG

ALLOWED_HOSTS = CONFIG.ALLOWED_HOST
if os.environ.get('DOMAIN_NAME'):
    ALLOWED_HOSTS.append(os.environ.get('DOMAIN_NAME').strip())

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Search
    'django.contrib.postgres',

    # API
    'rest_framework',
    'corsheaders',

    # My Apps
    'HOME.apps.HomeConfig',
    'PRODUCT.apps.ProductConfig',
    'SELLER.apps.SellerConfig',
    'USER.apps.UserConfig',
    'TRANSACTION.apps.TransactionConfig',

    # Extra Apps
    'django_cleanup.apps.CleanupConfig',
    'django.contrib.humanize',
    'dbbackup',  # django-dbbackup
]

# DB Backup config
DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': BASE_DIR / 'media'}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOWED_ORIGINS = CONFIG.CORS_ALLOWED_ORIGIN
CORS_ORIGIN_ALLOW_ALL = True


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
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

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

ROOT_URLCONF = 'DRC.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'builtins': [
                'SELLER.templatetags.custom_tag',
            ],
        },
    },
]
WSGI_APPLICATION = 'DRC.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases
LOCAL = False

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators
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
# https://docs.djangoproject.com/en/3.1/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/
STATIC_ROOT = 'staticfiles/'
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

MEDIA_URL = '/media/'
MEDIA_ROOT = 'media/'

# Django SMTP CONF (ZOHO)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = CONFIG.MAIL.HOST
EMAIL_USE_TLS = CONFIG.MAIL.USE_TLS
EMAIL_PORT = CONFIG.MAIL.PORT
EMAIL_HOST_USER = os.environ.get('MAIL_USERNAME')
EMAIL_HOST_PASSWORD = os.environ.get('MAIL_PASSWORD')

# for log
LOGGING = LOG_CONFIG

"""
TOPPERS – Base Settings
Shared across all environments.
"""
import os
from pathlib import Path
from datetime import timedelta
import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ─── Environment ──────────────────────────────────────────────
env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ['localhost', '127.0.0.1']),
)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env('SECRET_KEY', default='django-insecure-change-me-in-production')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env('ALLOWED_HOSTS')

# ─── Application Definition ───────────────────────────────────
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_filters',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'channels',
    'django_celery_beat',
    'django_celery_results',
]

LOCAL_APPS = [
    'apps.accounts',
    'apps.quiz',
    'apps.games',
    'apps.rewards',
    'apps.leaderboards',
    'apps.challenges',
    'apps.notifications',
    'apps.advertisements',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'toppers.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'toppers.wsgi.application'
ASGI_APPLICATION = 'toppers.routing.application'

# ─── Database ─────────────────────────────────────────────────
DATABASES = {
    'default': env.db('DATABASE_URL', default='postgres://toppers_user:password@localhost:5432/toppers_db')
}

# ─── Auth ─────────────────────────────────────────────────────
AUTH_USER_MODEL = 'accounts.CustomUser'
SITE_ID = 1

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ─── Internationalization ─────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Lagos'
USE_I18N = True
USE_TZ = True

# ─── Static & Media Files ─────────────────────────────────────
STATIC_URL = '/static/'
STATIC_ROOT = env('STATIC_ROOT', default=str(BASE_DIR / 'staticfiles'))
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = env('MEDIA_ROOT', default=str(BASE_DIR / 'media'))

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─── REST Framework ───────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'game_submit': '120/minute',
    },
}

# ─── JWT ──────────────────────────────────────────────────────
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# ─── Allauth / OAuth ──────────────────────────────────────────
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_UNIQUE_EMAIL = True

# ─── Custom Allauth Adapters ──────────────────────────
ACCOUNT_ADAPTER = 'apps.accounts.adapters.CustomAccountAdapter'
SOCIALACCOUNT_ADAPTER = 'apps.accounts.adapters.CustomSocialAccountAdapter'

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'APP': {
            'client_id': env('GOOGLE_CLIENT_ID', default=''),
            'secret': env('GOOGLE_CLIENT_SECRET', default=''),
            'key': '',
        }
    }
}

# ─── CORS ─────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]
CORS_ALLOW_CREDENTIALS = True

# ─── Redis & Channels ─────────────────────────────────────────
REDIS_URL = env('REDIS_URL', default='redis://localhost:6379/0')

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [REDIS_URL],
        },
    },
}

# ─── Celery ───────────────────────────────────────────────────
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default='redis://localhost:6379/1')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Africa/Lagos'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# ─── Email ────────────────────────────────────────────────────
EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='TOPPERS <noreply@toppers.ng>')

# ─── Paystack ─────────────────────────────────────────────────
PAYSTACK_SECRET_KEY = env('PAYSTACK_SECRET_KEY', default='')
PAYSTACK_PUBLIC_KEY = env('PAYSTACK_PUBLIC_KEY', default='')

# ─── VTPass (Airtime) ─────────────────────────────────────────
VTPASS_API_KEY = env('VTPASS_API_KEY', default='')
VTPASS_PUBLIC_KEY = env('VTPASS_PUBLIC_KEY', default='')
VTPASS_SECRET_KEY = env('VTPASS_SECRET_KEY', default='')
VTPASS_BASE_URL = env('VTPASS_BASE_URL', default='https://sandbox.vtpass.com/api')

# ─── Frontend ─────────────────────────────────────────────────
FRONTEND_URL = env('FRONTEND_URL', default='http://localhost:3000')

# ─── Game Configuration ───────────────────────────────────────
GAME_CONFIG = {
    'DAILY_GAME_LIMIT': env.int('DAILY_GAME_LIMIT', default=5),
    'POINTS_TO_NAIRA_RATE': float(env('POINTS_TO_NAIRA_RATE', default='0.05')),
    'MIN_REDEMPTION_POINTS': env.int('MIN_REDEMPTION_POINTS', default=2000),
    'REFERRAL_BONUS_POINTS': env.int('REFERRAL_BONUS_POINTS', default=500),
    'DAILY_LOGIN_BONUS': env.int('DAILY_LOGIN_BONUS', default=50),
    'STREAK_BONUS_MULTIPLIER': 1.5,
    'CHALLENGE_WIN_BONUS': 100,
    'CLASSIC_MODE_QUESTIONS': 15,
    'SURVIVAL_BASE_MULTIPLIER': 1.0,
    'SURVIVAL_MULTIPLIER_INCREMENT': 0.1,
    'SPEED_MODE_DURATION': 60,  # seconds
    'LIFELINES_PER_CLASSIC_GAME': {
        'fifty_fifty': 1,
        'phone_friend': 1,
        'ask_audience': 1,
        'skip': 1,
        'second_chance': 1,
    },
    'DIFFICULTY_POINTS': {
        'easy': 10,
        'medium': 25,
        'hard': 50,
        'expert': 100,
    },
}

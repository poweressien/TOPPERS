from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE

INTERNAL_IPS = ['127.0.0.1']

# Use console email in dev
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Simplified channel layer for dev (in-memory)
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    }
}

CORS_ALLOW_ALL_ORIGINS = True

"""
TOPPERS – Production Settings (PythonAnywhere)
"""
from .base import *
import dj_database_url

DEBUG = False

# ── MySQL for PythonAnywhere free tier ────────────────────────
# PythonAnywhere provides MySQL, not PostgreSQL.
# Install pymysql: pip install pymysql
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass  # Falls back to psycopg2 if available (e.g. paid tier with PostgreSQL)

DATABASES = {
    'default': dj_database_url.config(
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# ── No Redis on free tier — use in-memory channel layer ───────
# Live challenge WebSocket requires Redis (upgrade to paid tier for this).
# Everything else (quiz, rewards, leaderboard) works perfectly without it.
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    }
}

# ── No Celery worker on free tier — run tasks synchronously ───
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# ── Security ──────────────────────────────────────────────────
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# PythonAnywhere handles HTTPS termination — enable secure cookies
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# ── Logging — errors go to file on PythonAnywhere ─────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'error.log',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'ERROR',
    },
}

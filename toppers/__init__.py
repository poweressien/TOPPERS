# Celery is optional — not available on PythonAnywhere free tier
try:
    from .celery import app as celery_app
    __all__ = ('celery_app',)
except Exception:
    pass

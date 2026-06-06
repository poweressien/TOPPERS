web: daphne -b 0.0.0.0 -p $PORT toppers.routing:application
worker: celery -A toppers worker -l info
beat: celery -A toppers beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler

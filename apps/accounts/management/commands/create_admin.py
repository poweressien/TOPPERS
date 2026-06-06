"""
Management command: python manage.py create_admin
Creates a default superuser for development.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a default superuser for development.'

    def handle(self, *args, **options):
        if User.objects.filter(username='admin').exists():
            self.stdout.write(self.style.WARNING('Admin user already exists.'))
            return

        user = User.objects.create_superuser(
            username='admin',
            email='admin@toppers.ng',
            password='Admin@1234',
            is_email_verified=True,
        )
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Superuser created:\n'
            f'   Username : admin\n'
            f'   Email    : admin@toppers.ng\n'
            f'   Password : Admin@1234\n'
            f'   ⚠  Change this password immediately in production!\n'
        ))

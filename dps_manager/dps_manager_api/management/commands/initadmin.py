from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    def handle(self, *args, **options):
        if User.objects.count() == 0:
            for username in settings.ADMINS:
                email = f'{username}@localhost'
                password = 'password'
                print(f'Creating account for {username} ({email})')
                admin = User.objects.create_superuser(email=email, username=username, password=password)
                admin.is_active = True
                admin.is_admin = True
                admin.is_superuser = True
                admin.save()
        else:
            print('One or more admin account(s) already exist.')

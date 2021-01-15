import os
from django.conf import settings
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dps_manager_api', '0009_authtoken'),
    ]
    
    def generate_superuser(apps, schema_editor):
        from django.contrib.auth.models import User

        DJANGO_SU_NAME = os.environ.get('DJANGO_SU_NAME', 'admin')
        DJANGO_SU_EMAIL = os.environ.get('DJANGO_SU_EMAIL', 'admin@localhost')
        DJANGO_SU_PASSWORD = os.environ.get('DJANGO_SU_PASSWORD', 'password')

        superuser = User.objects.create_superuser(
            username=DJANGO_SU_NAME,
            email=DJANGO_SU_EMAIL,
            password=DJANGO_SU_PASSWORD)

        superuser.save()

    operations = [
        migrations.RunPython(generate_superuser),
    ]

"""
WSGI config for dps_manager project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from django.core.management import call_command
from dps_manager_api.models import Object

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dps_manager.settings')

# If there are no objects, initialize the default objects
if not Object.objects.all():
    call_command('loaddata', 'objects')

application = get_wsgi_application()

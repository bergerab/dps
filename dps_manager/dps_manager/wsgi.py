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
from dps_manager_api.views import SystemAPI

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dps_manager.settings')

# If there are no systems, initialize the default objects
# This is a bit hacky, should probably put some object into the
# database when this is loaded, and check a version on that object.
if not Object.objects.filter(kind=SystemAPI.kind).first():
    call_command('loaddata', 'objects')

application = get_wsgi_application()

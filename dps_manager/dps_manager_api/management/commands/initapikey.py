import os
import json

from django.core.management.base import BaseCommand
from dps_manager_api.models import Object
from dps_manager_api.views import APIKeyAPI

class Command(BaseCommand):
    def handle(self, *args, **options):
        secret = os.getenv('BATCH_PROCESSOR_API_KEY')        
        if not Object.objects.filter(kind=APIKeyAPI.kind, name=secret).first():
            if not secret:
                raise Exception('You must specify the BATCH_PROCESSOR_API_KEY environment variable (it should contain the secret token).')
            key = {
                'name': 'Batch Processor',
                'key': secret,
            }
            key = Object.objects.create(kind=APIKeyAPI.kind,
                                        name=key['key'],
                                        value=json.dumps(key))
            key.save()
            print('Created initial API key.')
        else:
            print('One or more api key(s) already exist.')

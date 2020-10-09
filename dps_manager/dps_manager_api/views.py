from django.conf import settings
from django.http import Http404, HttpResponse, JsonResponse

from .object_api import ObjectAPI
from .serializers import \
    SystemSerializer, \
    BatchProcessSerializer, \
    ProgressSerializer

class SystemAPI(ObjectAPI):
    serializer = SystemSerializer
    kind = 'System'
    id_name = 'system_id'
    api_name = 'system'
    plural_api_name = 'systems'

    def after_update(self, data):
        print('after_update', data)

    def after_delete(self, data):
        # delete all KPIResults for this system
        print('after_delete', data)

class BatchProcessAPI(ObjectAPI):
    serializer = BatchProcessSerializer
    kind = 'BatchProcess'
    id_name = 'batch_process_id'
    api_name = 'batch_process'    
    plural_api_name = 'batch_processes'

class ProgressAPI(ObjectAPI):
    serializer = ProgressSerializer
    kind = 'Progress'
    id_name = 'progress_id'
    api_name = 'progress'
    plural_api_name = 'progresses'

def info(request):
    return JsonResponse({
        'type': 'dps-manager',
        'version': '1.0.0',
        'protocols': ['application/json'],
        'debug': settings.DEBUG,
    })

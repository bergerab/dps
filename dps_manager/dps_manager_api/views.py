import json

from django.conf import settings
from django.http import Http404, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .object_api import ObjectAPI
from .serializers import \
    SystemSerializer, \
    BatchProcessSerializer, \
    ProgressSerializer, \
    RequiredMappingsRequestSerializer

from dplib import BatchProcess, KPI

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

@csrf_exempt
def get_required_mappings(request):
    serializer = RequiredMappingsRequestSerializer(data=json.loads(request.body))
    if not serializer.is_valid():
        return JsonResponse(serializer.errors, status=400)
    data = serializer.validated_data
    
    parameter_names = []
    for parameter in data['parameters']:
        if parameter['identifier']:
            parameter_names.append(parameter['identifier'])
        else:
            parameter_names.append(parameter['name'])            

    bp = BatchProcess()
    for kpi in data['kpis']:
        bp.add(kpi['identifier'] or kpi['name'], KPI(kpi['computation']))

    signals = []
    parameters = []
    for name in bp.get_required_inputs():
        if name in parameter_names:
            parameters.append(name)
        else:
            signals.append(name)
        
    return JsonResponse({
        'signals': signals,
        'parameters': parameters,
    })

def info(request):
    return JsonResponse({
        'type': 'dps-manager',
        'version': '1.0.0',
        'protocols': ['application/json'],
        'debug': settings.DEBUG,
    })

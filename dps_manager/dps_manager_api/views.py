import json

from django.conf import settings
from django.http import Http404, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Object

from .object_api import ObjectAPI
from .serializers import \
    SystemSerializer, \
    BatchProcessSerializer, \
    ProgressSerializer, \
    RequiredMappingsRequestSerializer, \
    SystemMappingSerializer

from dplib import Component, KPI

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

class SystemMappingAPI(ObjectAPI):
    serializer = SystemMappingSerializer
    kind = 'SystemMapping'
    id_name = 'system_mapping_id'
    api_name = 'system_mapping'
    plural_api_name = 'system_mappings'
    ref_name = 'system_id'

@csrf_exempt
def get_required_mappings(request):
    serializer = RequiredMappingsRequestSerializer(data=json.loads(request.body))
    if not serializer.is_valid():
        return JsonResponse(serializer.errors, status=400)
    data = serializer.validated_data
    system = data['system']
    kpi_names = data['kpi_names']
    
    parameter_names = []
    parameter_id_to_parameter = {}
    for parameter in system['parameters']:
        name = None
        if parameter['identifier']:
            name = parameter['identifier']
        else:
            name = parameter['name']
        parameter_names.append(name)
        parameter_id_to_parameter[name] = parameter

    c = Component('Temp', parameters=parameter_names)
    for kpi in system['kpis']:
        identifier = kpi.get('identifier')
        if identifier == '':
            identifier = None
        c.add(kpi['name'], kpi['computation'], id=identifier)

    signals = []
    parameters = []
    for name in c.get_required_inputs(kpi_names):
        if name in parameter_names:
            parameter = parameter_id_to_parameter[name]
            if not parameter['hidden']:
                parameters.append(parameter['name'])
        else:
            signals.append(name)
        
    return JsonResponse({
        'signals': signals,
        'parameters': parameters,
    })

@csrf_exempt
def get_system_mapping(request):
    serializer = GetSystemMappingSerializer(data=json.loads(request.body))
    if not serializer.is_valid():
        return JsonResponse(serializer.errors, status=400)
    data = serializer.validated_data
    
    obj = Object.objects.filter(kind='SystemMapping', ref=data['system_id']).first()
    serializer = SystemMappingSerializer(obj)
    return serializer.data

def info(request):
    return JsonResponse({
        'type': 'dps-manager',
        'version': '1.0.0',
        'protocols': ['application/json'],
        'debug': settings.DEBUG,
    })

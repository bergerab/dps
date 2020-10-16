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
    JobSerializer, \
    ResultsSerializer, \
    GetKPIsSerializer

from dplib import Component, KPI

class SystemAPI(ObjectAPI):
    serializer = SystemSerializer
    kind = 'System'
    id_name = 'system_id'
    api_name = 'system'
    plural_api_name = 'systems'

class BatchProcessAPI(ObjectAPI):
    serializer = BatchProcessSerializer
    kind = 'BatchProcess'
    id_name = 'batch_process_id'
    api_name = 'batch_process'    
    plural_api_name = 'batch_processes'
    ref_name = 'system_id'

    def after_create(self, data, obj):
        Object.objects.create(kind=JobAPI.kind,
                              ref=obj.object_id,
                              value=json.dumps({
                                  'batch_process_id': obj.object_id,
                                  'batch_process': data,
                                  'database_manager_url': 'TODO',
                              }))

class ProgressAPI(ObjectAPI):
    serializer = ProgressSerializer
    kind = 'Progress'
    id_name = 'progress_id'
    api_name = 'progress'
    plural_api_name = 'progresses'

class JobAPI(ObjectAPI):
    serializer = JobSerializer
    kind = 'Job'
    id_name = 'job_id'
    api_name = 'job'
    plural_api_name = 'jobs'

class ResultsAPI(ObjectAPI):
    serializer = ResultsSerializer
    kind = 'Result'
    id_name = 'result_id'
    api_name = 'result'
    plural_api_name = 'results'
    ref_name = 'batch_process_id'

    def after_update(self, data, obj):
        if data['complete']:
            bp_obj = Object.objects.filter(object_id=data['batch_process_id']).first()
            bp = json.loads(bp_obj.value)
            system_id = bp['system_id']
            results = data['results']
            for mapping in results:
                key = mapping['key']
                value = mapping['value']
                Object.objects.create(
                    name=key,
                    kind='KPIResult',
                    ref=system_id,
                    value=json.dumps({
                        'name': key,
                        'value': value,
                        'system_id': system_id,
                        'batch_process_id': bp_obj.object_id,
                    }))

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
def pop_job(request):
    # TODO: add a mutex here for if more than one batch processor is supported
    job_obj = Object.objects.filter(kind=JobAPI.kind).order_by('created_at').first()
    if not job_obj:
        return JsonResponse({}, status=404)
    response = JsonResponse(
        json.loads(job_obj.value)
    )
    job_obj.delete()
    return response

@csrf_exempt
def get_kpis(request):
    serializer = GetKPIsSerializer(data=json.loads(request.body))
    if not serializer.is_valid():
        return JsonResponse(serializer.errors, status=400)
    data = serializer.validated_data
    system_id = data['system_id']
    objs = Object.objects.filter(kind='KPIResult', ref=system_id) \
                         .order_by('-created_at').all()
        # .distinct('name')

    SEEN = set()
    kpis = []
    for obj in objs:
        if obj.name not in SEEN:
            d = json.loads(obj.value)
            d['created_at'] = obj.created_at
            kpis.append(d)
            SEEN.add(obj.name)        
        
    return JsonResponse({ 'kpis': kpis })

def info(request):
    return JsonResponse({
        'type': 'dps-manager',
        'version': '1.0.0',
        'protocols': ['application/json'],
        'debug': settings.DEBUG,
    })

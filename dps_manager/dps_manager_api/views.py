import json
from threading import Lock

from django.conf import settings
from django.http import Http404, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

import math

import requests
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta

import dps_services.util as util

from .models import Object

from .object_api import ObjectAPI
from .serializers import \
    SystemSerializer, \
    BatchProcessSerializer, \
    RequiredMappingsRequestSerializer, \
    JobSerializer, \
    ResultsSerializer, \
    GetKPIsSerializer, \
    RegisterDatabaseManagerSerializer, \
    BatchProcessRequestSerializer

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
                              }))

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
        if data['status'] == 2: # If complete
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

# Mutex to ensure if multiple batch processes exist, they are
# assigned separate jobs. If DPS Manager is clustered, this mutex
# will have to reside somewhere else (e.g. database), so that the
# memory is shared in the cluster.
job_mutex = Lock()
@csrf_exempt
def pop_job(request):
    job_mutex.acquire()
    try:
        job_obj = Object.objects.filter(kind=JobAPI.kind).order_by('created_at').first()
        if not job_obj:
            return JsonResponse({}, status=404)
        value = json.loads(job_obj.value)
        response = JsonResponse(
            value,
        )
        job_obj.delete()
        return response
    except Exception as e:
        return JsonResponse({ 'error': e }, status=500)        
    finally:
        job_mutex.release()

@csrf_exempt
def get_kpis(request):
    serializer = GetKPIsSerializer(data=json.loads(request.body))
    if not serializer.is_valid():
        return JsonResponse(serializer.errors, status=400)
    data = serializer.validated_data
    system_id = data['system_id']
    objs = Object.objects.filter(kind='KPIResult', ref=system_id) \
                         .order_by('-created_at').all()
        # .distinct('name') # TODO: after updating database backend, uncomment

    SEEN = set()
    kpis = []
    for obj in objs:
        if obj.name not in SEEN:
            d = json.loads(obj.value)
            d['created_at'] = obj.created_at
            kpis.append(d)
            SEEN.add(obj.name)        
        
    return JsonResponse({ 'kpis': kpis })

@csrf_exempt
def batch_process_results(request):
    serializer = BatchProcessRequestSerializer(data=json.loads(request.body))
    if not serializer.is_valid():
        return JsonResponse(serializer.errors, status=400)
    data = serializer.validated_data
    
    page_size       = data['page_size']
    page_number     = data['page_number']
    system_id       = data['system_id']
    search          = data['search']
    order_direction = data.get('order_direction', '') 
    
    offset = page_size * page_number
    limit  = page_size

    order = 'created_at' if order_direction == 'asc' else '-created_at'
    count = Object.objects.filter(kind=BatchProcessAPI.kind, ref=system_id, name__contains=search).count()
    objs  = Object.objects.filter(kind=BatchProcessAPI.kind, ref=system_id, name__contains=search) \
                          .order_by(order).all()[offset:offset+limit]
    results = []
    for obj in objs:
        result = get_result(obj)
        results.append(result)
    return JsonResponse({
        'total': count,
        'page': page_number,
        'data': results,
    })


@csrf_exempt
def signal_names_table(request):
    jo = json.loads(request.body)
    
    page_size       = jo['page_size']
    page_number     = jo['page_number']
    dataset         = jo['dataset']    
    search          = jo['search']
    order_direction = jo.get('order_direction', '') 
    
    offset = page_size * page_number
    limit  = page_size

    resp = requests.post(settings.DBM_URL + '/api/v1/get_signal_names', json={
        'dataset': dataset,
        'query':   search,
        'offset':  offset,
        'limit':   limit,
    }).json()['results'][0]

    total = resp['total']
    queries = []
    for value in resp['values']:
        queries.append({
            'signals': [value],
            'aggregation': 'count',
            'dataset': dataset,
        })

    resp = requests.post(settings.DBM_URL + '/api/v1/query', json={
        'queries': queries,
    }).json()['results']

    results = []
    for result in resp:
        results.append({
            'name': result['query']['signals'][0],
            'count': result['values'][0],
        })

    return JsonResponse({
        'total': total,
        'page': page_number,
        'data': results,
    })

@csrf_exempt
def get_batch_process_result(request, id):
    obj = Object.objects.filter(object_id=id).first()
    if not obj:
        return JsonResponse({}, status=404)
    result = get_result(obj)
    return JsonResponse(result)

def get_result(batch_process_obj):
    '''
    A helper function for `get_batch_process_result` and `batch_process_results`.

    It takes a batch process, and returns some results object for it (even if it has to create a fake one).
    '''
    result_obj = Object.objects.filter(kind=ResultsAPI.kind, ref=batch_process_obj.object_id).first()
    # If no result, make a fake one
    if result_obj:
        result = json.loads(result_obj.value)
        result['batch_process_result_id'] = result_obj.object_id
    else:
        result = {
            'batch_process_id': batch_process_obj.object_id,
            'results': [],
            'status': 3, # Queued
        }
    bp = json.loads(batch_process_obj.value)
    result['batch_process']      = bp
    result['batch_process_time'] = batch_process_obj.created_at
    return result
        
def info(request):
    return JsonResponse({
        'type':      'dps-manager',
        'version':   '1.0.0',
        'protocols': ['application/json'],
        'debug':     settings.DEBUG,
    })

@csrf_exempt
def get_signal_names(request):
    jo = json.loads(request.body)
    resp = requests.post(settings.DBM_URL + '/api/v1/get_signal_names', json={
        'dataset': jo['dataset'],
        'query':   jo['query'],
        'offset':  jo['offset'],
        'limit':   jo['limit'],
    }).json()['results'][0]
    return JsonResponse(resp)

@csrf_exempt
def get_chart_data(request):
    '''
    The request should be like this:
    {
        "series": [
            {
                'signal': 'Va',
                'dataset': '',
                'aggregation': 'max'
            },
            {
                'signal': 'Vb',
                'dataset': '',
                'aggregation': 'avg'
            }
        ],
        "interval": {
            "start": "...",
            "end":   "..."
        },
        "samples": 10
    }

    The result should be like this:
    {
        "series": [
            {
                "label": "Va",
                "data":  [[t0, v0], [t1, v1], [t2, v2]]
            },
            {
                "label": "Vb",
                "data":  [[t0, v0], [t1, v1], [t2, v2]]
            }
        ]
    }

    Where t0 - t2 indicate times, and v0 - v2 are values. This response matches the API for "react-charts"
    which is why I decided to do it this way.
    '''
    jo = json.loads(request.body)

    # We will be building up several "query" objects that the Database Manager understands
    queries = []
    
    series    = jo['series']
    interval  = jo['interval']
    samples   = jo['samples']
    intervals = get_sample_ranges(util.parse_datetime(interval['start']),
                                  util.parse_datetime(interval['end']),
                                  samples)
    for s in series:
        signal      = s['signal']
        dataset     = s['dataset']
        aggregation = s['aggregation']

        for start, end in intervals:
            queries.append({
                'signals':     [signal],
                'dataset':     dataset,
                'aggregation': aggregation,
                'interval': {
                    'start': util.format_datetime(start),
                    'end':   util.format_datetime(end),
                }
            })
        
    resp = requests.post(settings.DBM_URL + '/api/v1/query', json={
        'queries': queries,
    }).json()['results']

    results = []
    for i, s in enumerate(series):
        data = []
        for j, (start, end) in enumerate(intervals):
            result = resp[(i * samples) + j]
            
            # Get the time between start and end to use in chart
            # dt = end - start
            # start += dt/2
            data.append({
                'x': start,
                'y': result['values'][0],
            })
        results.append({ 'label': s['signal'],
                         'data':  data })
    return JsonResponse({ 'datasets': results })

def get_interval(start_time, end_time):
    d = end_time - start_time
    seconds = int(d.total_seconds())    
    microseconds = int(d.total_seconds() * 1e6)
    if d.days / 365 > 4:
        return 'years'
    elif d.days / 30 > 2:
        return 'months'
    elif d.days > 5:
        return 'days'
    elif d.seconds / 3600 > 3:
        return 'hours'
    elif seconds / 60 > 3:
        return 'minutes'
    elif seconds / 30 > 3:
        return 'halfminutes'
    elif seconds / 10 > 3:
        return 'tenseconds'
    elif seconds > 3:
        return 'seconds'
    elif microseconds/100000 > 5:
        return 'deciseconds'
    elif microseconds/10000 > 5:
        return 'centiseconds'
    return 'milliseconds'
        
def get_sample_ranges(start_time, end_time, _):
    interval = get_interval(start_time, end_time)
    print('interval', interval)
    if interval == 'years':
        start_time = start_time.replace(month=0, day=0, hour=0, minute=0, second=0, microsecond=0)
    elif interval == 'months':
        start_time = start_time.replace(day=0, hour=0, minute=0, second=0, microsecond=0)
        step = timedelta(months=1)
    elif interval == 'days':
        start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
        step = timedelta(days=1)        
    elif interval == 'hours':
        start_time = start_time.replace(minute=0, second=0, microsecond=0)
        step = timedelta(hours=1)                
    elif interval == 'minutes':
        start_time = start_time.replace(second=0, microsecond=0)
        step = timedelta(minutes=1)
    elif interval == 'halfminutes':
        start_time = start_time.replace(second=0, microsecond=0)
        step = timedelta(minutes=1/2)
    elif interval == 'tenseconds':
        start_time = start_time.replace(microsecond=0)
        step = timedelta(seconds=10)
    elif interval == 'seconds':
        start_time = start_time.replace(microsecond=0)
        step = timedelta(seconds=1)
    elif interval == 'deciseconds':
        start_time = start_time.replace(microsecond=math.floor(start_time.microsecond/100000) * 100000)
        step = timedelta(microseconds=100000)                                
    elif interval == 'centiseconds':
        start_time = start_time.replace(microsecond=math.floor(start_time.microsecond/10000) * 10000)
        step = timedelta(microseconds=10000)                                
    elif interval == 'milliseconds':
        start_time = start_time.replace(microsecond=math.floor(start_time.microsecond/1000) * 1000)
        step = timedelta(microseconds=1000)                                
    elif interval == 'microseconds':
        step = timedelta(microseconds=1)

    print(start_time, step)

    dt   = end_time - start_time
    t0   = start_time
    t1   = start_time + step
    
    ranges = [(t0, t1)]
    while t1 <= end_time:
        t0 += step
        t1 += step
        ranges.append((t0, t1))
    return ranges
    

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
    ScheduleSerializer, \
    AuthTokenSerializer, \
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
        pass
        # I used to have this code uncommented. It was a way to look at KPIs for each system
        # instead of looking at KPIs for each batch process:
        #
        # if data['status'] == 2: # If complete
        #     bp_obj = Object.objects.filter(object_id=data['batch_process_id']).first()
        #     bp = json.loads(bp_obj.value)
        #     system_id = bp['system_id']
        #     results = data['results']
        #     for mapping in results:
        #         key = mapping['key']
        #         value = mapping.get('value', None)
        #         object_value = mapping.get('object_value', None)                
        #         Object.objects.create(
        #             name=key,
        #             kind='KPIResult',
        #             ref=system_id,
        #             value=json.dumps({
        #                 'name': key,
        #                 'value': value,
        #                 'object_value': object_value,
        #                 'system_id': system_id,
        #                 'batch_process_id': bp_obj.object_id,
        #             }))

class ScheduleAPI(ObjectAPI):
    serializer = ScheduleSerializer
    kind = 'Schedule'
    id_name = 'schedule_id'
    api_name = 'schedule'
    plural_api_name = 'schedules'
    name_attr = 'dataset' # Use the dataset name as the name for the object

class AuthTokenAPI(ObjectAPI):
    serializer = AuthTokenSerializer
    kind = 'AuthToken'
    id_name = 'auth_token_id'
    api_name = 'auth_token'
    plural_api_name = 'auth_tokens'
    name_attr = 'token'

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

    # Filter out any reserved names
    signals = list(filter(lambda x: x != 'Nothing', signals))
        
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
    }).json()

    if 'results' not in resp:
        return JsonResponse(resp, status=500)
    
    resp = resp['results'][0]

    total = resp['total']
    queries = []
    for value in resp['values']:
        queries.append({
            'signals': [value],
            'aggregation': 'count',
            'dataset': dataset,
        })

    if not queries:
        return JsonResponse({
            'total': total,
            'page': page_number,
            'data': [],
        })

    resp = requests.post(settings.DBM_URL + '/api/v1/query', json={
        'queries': queries,
    }).json()

    if 'results' not in resp:
        return JsonResponse(resp, status=500)

    resp = resp['results']

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
def dataset_table(request):
    jo = json.loads(request.body)
    
    page_size       = jo['page_size']
    page_number     = jo['page_number']
    search          = jo['search']
    order_direction = jo.get('order_direction', '') 
    
    offset = page_size * page_number
    limit  = page_size

    resp = requests.post(settings.DBM_URL + '/api/v1/get_dataset_names', json={
        'query':   search,
        'offset':  offset,
        'limit':   limit,
    }).json()

    if 'results' not in resp:
        return JsonResponse(resp, status=500)

    return JsonResponse({
        'total': resp['results'][0]['total'],
        'page': page_number,
        'data': list(map(lambda x: { 'name': x }, resp['results'][0]['values'])),
    })

@csrf_exempt
def add_dataset(request):
    jo = json.loads(request.body)
    
    name = jo['name']

    resp = requests.post(settings.DBM_URL + '/api/v1/insert', json={
        'inserts': [{
            'dataset': name,
            'signals': [],
            'samples': [],
            'times': [],
        }],
    })

    if resp.status_code >= 400:
        return HttpResponse(resp, status=500)
    
    return JsonResponse({
        'message': 'OK',
    })

@csrf_exempt
def dataset_table(request):
    jo = json.loads(request.body)
    
    page_size       = jo['page_size']
    page_number     = jo['page_number']
    search          = jo['search']
    order_direction = jo.get('order_direction', '') 
    
    offset = page_size * page_number
    limit  = page_size

    resp = requests.post(settings.DBM_URL + '/api/v1/get_dataset_names', json={
        'query':   search,
        'offset':  offset,
        'limit':   limit,
    }).json()

    if 'results' not in resp:
        return JsonResponse(resp, status=500)

    return JsonResponse({
        'total': resp['results'][0]['total'],
        'page': page_number,
        'data': list(map(lambda x: { 'name': x }, resp['results'][0]['values'])),
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
    }).json()
    if 'results' not in resp:
        return JsonResponse(resp, status=500)
    resp = resp['results'][0]
    return JsonResponse(resp)

@csrf_exempt
def get_dataset_names(request):
    jo = json.loads(request.body)
    resp = requests.post(settings.DBM_URL + '/api/v1/get_dataset_names', json={
        'query':   jo['query'],
        'offset':  jo['offset'],
        'limit':   jo['limit'],
    }).json()['results'][0]
    return JsonResponse(resp)

@csrf_exempt
def delete_batch_process(request, id):
    # Delete the actual batch process KPIs stored in TimescaleDB
    resp = requests.post(settings.DBM_URL + '/api/v1/delete_dataset', json={
        'dataset':   'batch_process_' + str(id),
    })
    if resp.status_code >= 400:
        return JsonResponse(resp, status=500)
    resp = resp.json()

    # Delete any jobs that haven't been popped yet
    Object.objects.filter(kind=JobAPI.kind,
                          ref=id).delete()

    # Delete all batch process results
    Object.objects.filter(kind=ResultsAPI.kind,
                          ref=id).delete()

    

    # Delete the actual batch process object
    Object.objects.filter(kind=BatchProcessAPI.kind,
                          object_id=id).delete()
    
    return JsonResponse(resp)

@csrf_exempt
def delete_dataset(request):
    jo = json.loads(request.body)
    resp = requests.post(settings.DBM_URL + '/api/v1/delete_dataset', json={
        'dataset':   jo['dataset'],
    })

    if resp.status_code >= 400:
        return HttpResponse(resp, status=500)
    
    resp = resp.json()

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
        "offset": 5
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

    Where t0 - t2 indicate times, and v0 - v2 are values. This response matches the API for Chart.js
    which is why I decided to do it this way.
    '''
    jo = json.loads(request.body)

    # We will be building up several "query" objects that the Database Manager understands
    queries = []
    
    series    = jo['series']
    interval  = jo['interval']
    offset    = jo['offset'] # How many hours away from UTC the time is
    pad       = jo.get('pad', True) # Whether or not to add an additional time unit to the beginning and end of the time range
    infer     = jo.get('infer', False) # Whether or not to infer the time range (has priority over interval)
    interval_start = util.parse_datetime(interval['start'])
    interval_end = util.parse_datetime(interval['end'])
    
    if infer:
        # Inferred time range
        # Used if the user doesn't know what time range to look for data.
        # We look for the range in all of the signals, and include all of the data
        # in the range.
        inferred_start_time = None
        inferred_end_time = None

    if infer:
        for s in series:
            signal      = s['signal']
            dataset     = s['dataset']

            # Infer what the correct time range should be
            resp = requests.post(settings.DBM_URL + '/api/v1/get_range', json={
                'dataset': dataset,
                'signal': signal,
            }).json()['results'][0]
            first = resp['first']
            last = resp['last']
            if first:
                if not inferred_start_time:
                    inferred_start_time = util.parse_datetime(first)
                else:
                    inferred_start_time = min(inferred_start_time, util.parse_datetime(first))                
            if last:
                if not inferred_end_time:
                    inferred_end_time = util.parse_datetime(last)
                else:
                    inferred_end_time = max(inferred_end_time, util.parse_datetime(last))
        interval_start = inferred_start_time
        interval_end = inferred_end_time

    intervals = get_sample_ranges(interval_start,
                                  interval_end,
                                  offset,
                                  pad)

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
    }).json()

    if 'results' not in resp:
        return JsonResponse(resp, status=500)

    resp = resp['results']

    results = []
    for i, s in enumerate(series):
        data = []
        for j, (start, end) in enumerate(intervals):
            result = resp[(i * len(intervals)) + j]
            
            # Get the time between start and end to use in chart
            # dt = end - start
            # start += dt/2
            y = result['values'][0]
            if y is not None: # skip nulls
                data.append({
                    'x': start,
                    'y': y,
                })
        results.append({ 'label': s['signal'],
                         'data':  data })
    return JsonResponse({
        'datasets': results,
        'interval': {
            'start': util.format_datetime(interval_start),
            'end':   util.format_datetime(interval_end),
        }
    })

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
    elif seconds / 3600 > 10:
        return 'hours'
    elif seconds / (3600 / 2) > 5:
        return 'halfhours'
    elif seconds / 60 > 5:
        return 'minutes'
    elif seconds / 30 > 5:
        return 'halfminutes'
    elif seconds / 10 > 5:
        return 'tenseconds'
    elif seconds > 5:
        return 'seconds'
    elif microseconds/100000 > 5:
        return 'deciseconds'
    elif microseconds/10000 > 5:
        return 'centiseconds'
    return 'milliseconds'
        
def get_sample_ranges(start_time, end_time, offset, pad=False):
    interval = get_interval(start_time, end_time)
    if interval == 'years':
        start_time = start_time.replace(month=0, day=0, hour=0, minute=0, second=0, microsecond=0)
        start_time -= timedelta(hours=offset)
    elif interval == 'months':
        start_time = start_time.replace(day=0, hour=0, minute=0, second=0, microsecond=0)
        step = timedelta(months=1)
        start_time -= timedelta(hours=offset)        
    elif interval == 'days':
        start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
        step = timedelta(days=1)
        start_time -= timedelta(hours=offset)        
    elif interval == 'hours':
        start_time = start_time.replace(minute=0, second=0, microsecond=0)
        step = timedelta(hours=1)
    elif interval == 'halfhours':
        start_time = start_time.replace(minute=0, second=0, microsecond=0)
        step = timedelta(hours=1/2)
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

    dt   = end_time - start_time
    t0   = start_time
    t1   = start_time + step

    if pad:
        # Add an extra interval to the beginning, so that the chart doesn't start abruptly
        ranges = [(t0 - step, t0), (t0, t1)]
    else:
        ranges = [(t0, t1)]
        
    while t1 <= end_time:
        t0 += step
        t1 += step
        ranges.append((t0, t1))

    if pad:
        # Add an extra interval to the end, so that the chart doesn't end abruptly
        ranges.append((t1, t1 + step))
    return ranges
    

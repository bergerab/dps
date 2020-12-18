import json
from threading import Lock
import uuid
import math
import uuid

from django.conf import settings
from django.http import Http404, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, render
from django.contrib.auth import authenticate
from django.utils import timezone

import requests
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta


import dps_services.util as util

from .auth import require_auth
from .models import Object, AuthToken
from .writers import CSVStream

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
    APIKeySerializer, \
    UserSerializer, \
    BatchProcessRequestSerializer

from dplib import Component, KPI

def dbm_post(endpoint, json):
    return requests.post(settings.DBM_URL + '/api/v1/' + endpoint,
                         json=json,
                         headers={
                             'Authorization': 'API ' + DPS_MANAGER_SECRET_API_KEY,
                         })

User = get_user_model()
class UserAPI(ObjectAPI):
    # This API involves a lot of copy and pasting from object_api.py
    # If I had more time I would design object_api to support other models besides Object.
    
    serializer = UserSerializer
    kind = 'User'
    id_name = 'user_id'
    api_name = 'user'
    plural_api_name = 'users'
    name_attr = 'username'

    def serialize(self, user):
        return {
            'username': user.username,
            'email': user.email,            
            'is_admin': user.is_superuser,
            'last_login': user.last_login,
            'created_at': user.date_joined,
            'user_id': user.id,
        }

    def get(self, request, id=None):
        if id:
            user = get_object_or_404(User, pk=id)
            return self.serialize(user)
        else:
            # If no id was provided, list all objects
            users = User.objects.order_by('username').all()
            data = []
            for user in users:
                data.append(self.serialize(user))
            return {
                'users': data,
            }

    def table(self, request):
        # An API that supports react-table for querying over data
        jo = json.loads(request.body)
        
        page_size       = jo['page_size']
        page_number     = jo['page_number']
        search          = jo['search']
        order_direction = jo.get('order_direction', '')
        order_by = jo.get('order_by', 'created_at')

        offset = page_size * page_number
        limit  = page_size

        order = order_by if order_direction == 'asc' else ('-' + order_by)
        if self.name_attr is None: # If the entity has no name
            count = User.objects.count()
            objs  = User.objects.order_by(order).all()[offset:offset+limit]
        else:
            count = User.objects.filter(username__contains=search).count()
            objs  = User.objects.filter(username__contains=search) \
                                  .order_by(order).all()[offset:offset+limit]

        jos = []
        for obj in objs:
            jo = self.serialize(obj)
            jos.append(jo)

        return JsonResponse({
            'total': count,
            'data': jos,
            'page': page_number,
        })

    def post(self, request):
        if self.read_only:
            raise MethodNotAllowed()
        jo = json.loads(request.body)
        self.before_update(jo)
        serializer = self.serializer(data=jo)
        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=400)
        data = serializer.validated_data
            
        user = User.objects.create_user(data['username'],
                                       data['email'],
                                       data['password1'],
        )
        if data['is_admin']:
            user.is_superuser = True
            user.save()
        return {}

    def delete(self, request, id):
        if self.read_only:
            raise MethodNotAllowed()
        if id:
            user = get_object_or_404(User, pk=id)
            user.delete()
            return HttpResponse(204)
        else:
            return HttpResponse('You must provide an id for the user to delete.', 400)

    def put(self, request, id):
        if self.read_only:
            raise MethodNotAllowed()
        user = get_object_or_404(User, pk=id)
        jo = json.loads(request.body)
        self.before_update(jo)        
        serializer = self.serializer(data=jo)
        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=400)
        data = serializer.validated_data
        
        user.username = data['username']
        user.email = data['email']        
        if data['password_was_set']:
            user.password = data['password1']
        user.is_superuser = data['is_admin']
        user.save()
        return JsonResponse({}, status=200)
    
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

class APIKeyAPI(ObjectAPI):
    serializer = APIKeySerializer
    kind = 'APIKey'
    id_name = 'api_key_id'
    api_name = 'api_key'
    plural_api_name = 'api_keys'
    name_attr = 'key'

@csrf_exempt
@require_auth
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
@require_auth
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

@require_auth
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

@require_auth
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


@require_auth
def signal_names_table(request):
    jo = json.loads(request.body)
    
    page_size       = jo['page_size']
    page_number     = jo['page_number']
    dataset         = jo['dataset']
    search          = jo['search']
    order_direction = jo.get('order_direction', '') 
    
    offset = page_size * page_number
    limit  = page_size

    resp = dbm_post('get_signal_names', {
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

    resp = dbm_post('query', { 
        'queries': queries 
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


@require_auth
def dataset_table(request):
    jo = json.loads(request.body)
    
    page_size       = jo['page_size']
    page_number     = jo['page_number']
    search          = jo['search']
    order_direction = jo.get('order_direction', '') 
    
    offset = page_size * page_number
    limit  = page_size

    resp = dbm_post('get_dataset_names', {
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

@require_auth
def add_dataset(request):
    jo = json.loads(request.body)
    
    name = jo['name']

    resp = dbm_post('insert', {
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

@require_auth
def dataset_table(request):
    jo = json.loads(request.body)
    
    page_size       = jo['page_size']
    page_number     = jo['page_number']
    search          = jo['search']
    order_direction = jo.get('order_direction', '') 
    
    offset = page_size * page_number
    limit  = page_size

    resp = dbm_post('get_dataset_names', {
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

@require_auth
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

@require_auth
def get_signal_names(request):
    jo = json.loads(request.body)
    resp = dbm_post('get_signal_names', {
        'dataset': jo['dataset'],
        'query':   jo['query'],
        'offset':  jo['offset'],
        'limit':   jo['limit'],
    }).json()
    if 'results' not in resp:
        return JsonResponse(resp, status=500)
    resp = resp['results'][0]
    return JsonResponse(resp)

@require_auth
def get_dataset_names(request):
    jo = json.loads(request.body)
    resp = dbm_post('get_dataset_names', {
        'query':   jo['query'],
        'offset':  jo['offset'],
        'limit':   jo['limit'],
    }).json()['results'][0]
    return JsonResponse(resp)

@require_auth
def delete_batch_process(request, id):
    # Delete the actual batch process KPIs stored in TimescaleDB
    resp = dbm_post('delete_dataset', {
        'dataset':   'batch_process_' + str(id),
    })
    if resp.status_code >= 400:
        return HttpResponse(resp.text, status=500)
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

@require_auth
def export_dataset(request):
    jo = json.loads(request.body)

    dataset    = jo['dataset']
    signals    = jo['signals']
    start_time = util.parse_datetime(jo['start'])
    end_time   = util.parse_datetime(jo['end'])
    limit      = 50000 # how many samples to query for at once
    
    def data():
        nonlocal dataset, signals, start_time, end_time, limit

        # yield the header
        yield ['Time'] + signals
        
        dbm_has_data = True
        samples      = []
        times        = []
        result       = None
    
        while dbm_has_data:
            resp = None
            try:
                resp = dbm_post('query', {
                    "queries": [
                        {
                            "dataset": dataset,
                            "signals": signals,
                            "interval": {
                                "start": util.format_datetime(start_time),
                                "end": util.format_datetime(end_time),
                            },
                            "limit": limit,
                        }
                    ]
                })
            except Exception as e:            
                raise Exception('error when fetching data from DPS Database Manager. Reason: ' + str(e))
            jo = resp.json()
            if resp.status_code != 200 or 'results' not in jo:
                raise Exception(resp.text)
            
            results = jo['results'][0]
            samples += results['samples']
            times   += [util.parse_datetime(time) for time in results['times']]

            # If there is no more data after this, end the process after this batch completes.
            if len(signals) * len(samples) < limit:
                dbm_has_data = False
            else:
                # Start the next batch of data at the last time we got from this batch.
                # Don't use that batch's sample data because there is a chance the samples
                # could be missing if the limit is not a multiple of the # of signals.
                samples.pop()
                start_time = times.pop()
    
            for i in range(len(times)):
                yield ([times[i]] + samples[i])
                
            samples = []
            times = []

    def serialize(data):
        return data

    try:
        csv_stream = CSVStream()
        return csv_stream.export("myfile", data(), serialize)
    except Exception as e:
        return JsonResponse({ message: str(e) }, status=500)

@require_auth
def delete_dataset(request):
    jo = json.loads(request.body)
    resp = dbm_post('delete_dataset', {
        'dataset':   jo['dataset'],
    })

    if resp.status_code >= 400:
        return HttpResponse(resp, status=500)
    
    resp = resp.json()

    return JsonResponse(resp)

DPS_MANAGER_SECRET_API_KEY = str(uuid.uuid4()) # DPS Manager controls access to DPS Database Manager. This key is for DPS Manager to always be allowed to talk to DPS Database Manager
@csrf_exempt
def authenticate_api_key(request):
    '''
    Returns if the API key should be allowed access. This endpoint is for the DPS Database Manager to ask if API keys should be allowed.

    This isn't a great way to do the security (could be broken by tricking the DPS Database Manager to talk to some other server that always returns true). But, at the moment, we don't assume our software will be targeted by attackers in this way.
    '''
    jo = json.loads(request.body)
    key = jo['key']
    if key == DPS_MANAGER_SECRET_API_KEY:
        return JsonResponse({ 'allowed': True }, status=200)            
    if not Object.objects.filter(kind=APIKeyAPI.kind, name=key).first():
        return JsonResponse({ 'allowed': False }, status=403)
    return JsonResponse({ 'allowed': True }, status=200)    

@csrf_exempt
def login(request):
    jo = json.loads(request.body)

    username = jo['username']
    password = jo['password']

    user = authenticate(username=username, password=password)
    if user is not None:
        # Delete existing tokens
        AuthToken.objects.filter(user_id=user.id).delete()
        token = AuthToken.objects.create(user=user,
                                         uid=uuid.uuid4(),
                                         expires_at=timezone.now() + timedelta(hours=1)
        )
        return JsonResponse({ 'token': token.uid, 'expires_at': token.expires_at, 'is_admin': user.is_superuser, 'username': user.username })
    return JsonResponse({}, status=403)

@require_auth
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
            resp = dbm_post('get_range', {
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

    resp = dbm_post('query', {
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
    

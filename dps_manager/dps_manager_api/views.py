import json

from django.conf import settings
from django.shortcuts import get_object_or_404, render
from django.http import Http404, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework import viewsets
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import \
    SystemSerializer, \
    BatchProcessSerializer, \
    ProgressSerializer

from .models import Object

def extract_obj_value(obj):
    return json.loads(obj.value)

def make_api(Serializer, kind, id_name, plural_name, ref_name=None):
    @csrf_exempt
    def api(request, id=None):
        if request.method == 'GET':
            if id:
                obj = get_object_or_404(Object, pk=id)
                serializer = Serializer(extract_obj_value(obj))
                data = serializer.data
                data[id_name] = obj.object_id
                return JsonResponse(data)
            else:
                # If no id was provided, list all objects
                objs = Object.objects.filter(kind=kind).all()
                q = map(extract_obj_value, objs)
                serializer = Serializer(q, many=True)
                datas = serializer.data
                for i, data in enumerate(datas):
                    data[id_name] = objs[i].object_id
                return JsonResponse({
                    plural_name.lower(): datas,
                })
        elif request.method == 'POST':
            if id:
                return HttpResponse(400)
            
            serializer = Serializer(data=json.loads(request.body))
            if not serializer.is_valid():
                return JsonResponse(serializer.errors, status=400)
            data = serializer.validated_data
            
            kwargs = {}
            if 'name' in data:
                kwargs['name'] = data['name']
            kwargs['kind'] = kind
            if ref_name:
                kwargs['ref'] = data[ref_name]
            kwargs['value'] = json.dumps(data)
            
            obj = Object.objects.create(**kwargs)
            
            data[id_name] = obj.object_id
            
            return JsonResponse(data, status=201)
        elif request.method == 'DELETE':
            if id:
                obj = get_object_or_404(Object, pk=id)
                obj.delete()
                return HttpResponse(204)
            else:
                # Only allow for deleting all Objects in debug mode (could be malicious)
                if settings.DEBUG:
                    Object.objects.filter(kind=kind).delete()
                    return HttpResponse(204)
                else:
                    return HttpResponse(400)
        elif request.method == 'PUT':
            obj = get_object_or_404(Object, pk=id)
            
            serializer = Serializer(data=json.loads(request.body))
            if not serializer.is_valid():
                return JsonResponse(serializer.errors, status=400)
            data = serializer.validated_data

            obj.value = json.dumps(data)
            obj.save()

            data[id_name] = obj.object_id
            
            return JsonResponse(data)
        raise MethodNotAllowed()
    return api

system = make_api(SystemSerializer, 'System', 'system_id', 'systems')
batch_process = make_api(BatchProcessSerializer, 'BatchProcess', 'batch_process_id', 'batch_processes')
progress = make_api(ProgressSerializer, 'Progress', 'progress_id', 'progresses')

def info(request):
    return JsonResponse({
        'type': 'dps-manager',
        'version': '1.0.0',
        'protocols': ['application/json'],
        'debug': settings.DEBUG,
    })

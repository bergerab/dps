import json

from django.urls import path, include
from django.conf import settings
from django.shortcuts import get_object_or_404, render
from django.http import Http404, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

import dps_services.util as util

from .models import Object

class ObjectAPI:
    serializer = None
    kind = None
    id_name = None
    plural_api_name = None
    ref_name = None
    read_only = False

    def __init__(self):
        class_name = self.__class__.__name__
        if not self.kind:
            raise Exception(f'You must specify a "kind" field on the {class_name} class.')
        elif not self.id_name:
            raise Exception(f'You must specify an "id_name" field on the {class_name} class.')
        elif not self.plural_api_name:
            raise Exception(f'You must specify an "plural_api_name" field on the {class_name} class.')
        elif not self.serializer:
            raise Exception(f'You must specify a "serializer" field on the {class_name} class.')

    def add_metafields(self, data, obj):
        data[self.id_name] = obj.object_id
        data['created_at'] = obj.created_at
        data['updated_at'] = obj.updated_at  
        
    def get(self, request, id=None):
        if id:
            obj = get_object_or_404(Object, pk=id)
            serializer = self.serializer(extract_obj_value(obj))
            data = serializer.data
            self.add_metafields(data, obj)            
            return data
        else:
            # If no id was provided, list all objects
            objs = Object.objects.filter(kind=self.kind).order_by('-created_at').all()
            q = map(extract_obj_value, objs)
            serializer = self.serializer(q, many=True)
            datas = serializer.data
            for i, data in enumerate(datas):
                obj = objs[i]
                self.add_metafields(data, obj)
            return {
                self.plural_api_name.lower(): datas,
            }

    def post(self, request):
        if self.read_only:
            raise MethodNotAllowed()
        jo = json.loads(request.body)
        self.before_update(jo)
        serializer = self.serializer(data=jo)
        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=400)
        data = serializer.validated_data

        kwargs = {}
        if 'name' in data:
            kwargs['name'] = data['name']
        kwargs['kind'] = self.kind
        if self.ref_name:
            kwargs['ref'] = data[self.ref_name]

        kwargs['value'] = json.dumps(data)
            
        obj = Object.objects.create(**kwargs)

        self.after_update(data, obj)
        self.after_create(data, obj)
        
        self.add_metafields(data, obj)

        return data

    def delete(self, request, id):
        if self.read_only:
            raise MethodNotAllowed()
        if id:
            obj = get_object_or_404(Object, pk=id)
            serializer = self.serializer(extract_obj_value(obj))
            obj.delete()
            self.after_delete(serializer.data)
            return HttpResponse(204)
        else:
            # Only allow for deleting all Objects in debug mode (could be malicious)
            if settings.DEBUG:
                q = map(lambda obj: (obj, extract_obj_value(obj)), Object.objects.filter(kind=self.kind).all())
                for obj, value in q:
                    serializer = self.serializer(value)
                    obj.delete()
                    self.after_delete(serializer.data)
                return HttpResponse(204)
            else:
                return HttpResponse(400)

    def put(self, request, id):
        if self.read_only:
            raise MethodNotAllowed()
        obj = get_object_or_404(Object, pk=id)
        jo = json.loads(request.body)
        self.before_update(jo)        
        serializer = self.serializer(data=jo)
        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=400)
        data = serializer.validated_data

        obj.value = json.dumps(data)
        obj.name = data.get('name')
        obj.save()

        self.after_update(data, obj)

        self.add_metafields(data, obj)
        
        return JsonResponse(data)

    def after_update(self, data, obj):
        '''
        Called after this entity is updated or created for the first time (after it is written to the database)
        '''
        pass

    def after_create(self, data, obj):
        pass

    def before_update(self, data):
        '''
        Called before this entity is updated or created for the first time (after it is written to the database).

        This provides an opportunity to update the object before it reaches the database.
        '''
        pass

    def after_delete(self, data):
        '''
        Called after this entity is deleted
        '''
        pass

def extract_obj_value(obj):
    return json.loads(obj.value)

class Router:
    def __init__(self):
        self.classes = []

    def add(self, Class):
        self.classes.append(Class)

    def get_urls(self):
        urls = []
        for Class in self.classes:
            handler = make_api_handler(Class)
            urls.append(path(util.make_api_url(Class.api_name), handler))
            urls.append(path(util.make_api_url(f'{Class.api_name}/'), handler))
            urls.append(path(util.make_api_url(f'{Class.api_name}/<int:id>'), handler))
        return urls

def make_api_handler(API):
    api = API()
    @csrf_exempt
    def handler(request, id=None):
        if request.method == 'GET':
            resp = api.get(request, id)
            if isinstance(resp, dict):
                return JsonResponse(resp)
            return resp            
        elif request.method == 'POST':
            resp = api.post(request)
            if isinstance(resp, dict):
                return JsonResponse(resp, status=201)
            return resp
        elif request.method == 'DELETE':
            resp = api.delete(request, id)
            return resp
        elif request.method == 'PUT':
            resp = api.put(request, id)
            return resp
        raise MethodNotAllowed()
    return handler

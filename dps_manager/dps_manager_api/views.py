import json

from django.conf import settings
from django.shortcuts import get_object_or_404, render
from django.http import Http404, HttpResponse, JsonResponse

from rest_framework import viewsets
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import \
    SystemSerializer, \
    BatchProcessSerializer, \
    ProgressSerializer

from .models import Object

class SystemView(APIView):
    def get_object(self, pk):
        try:
            return Snippet.objects.get(pk=pk)
        except Snippet.DoesNotExist:
            raise Http404    

    def list(self, request):
        def add_object_id(x):
            data = json.loads(x.value)
            data['system_id'] = x.object_id
            return data
        queryset = map(add_object_id,
                       Object.objects.filter(kind='System').all())
        serializer = SystemSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        
        return Response()        

    def get(self, request, pk=None):
        o = Object.objects.filter(object_id=pk).first()
        data = json.loads(o.value)
        data['system_id'] = o.object_id
        serializer = SystemSerializer(data)
        return Response(serializer.data)

    def update(self, request, pk=None):
        return Response()

    def partial_update(self, request, pk=None):
        return Response()                        

    def destroy(self, request, pk=None):
        q = Object.objects.filter(object_id=pk)        
        if not q.count():
            return Response(status=status.HTTP_404_NOT_FOUND)
        q.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

def system(request, system_id=None):
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        pass
    elif request.method == 'DELETE':
        pass
    elif request.method == 'PUT':
        pass
    else:
        raise MethodNotAllowed()
    return HttpResponse(request.method + str(system_id))

def info(request):
    return JsonResponse({
        'type': 'dps-manager',
        'version': '1.0.0',
        'protocols': ['application/json'],
        'debug': settings.DEBUG,
    })

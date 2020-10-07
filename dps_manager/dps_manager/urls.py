from django.urls import path, include
from django.contrib import admin

from rest_framework import routers, serializers, viewsets

from dps_manager_api.models import Object

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dps_manager_api.urls')),
]

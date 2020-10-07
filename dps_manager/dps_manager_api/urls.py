from django.urls import path, include

from . import views

from rest_framework import routers, serializers, viewsets
from . import views

import dps_services.util as util

urlpatterns = [
    path('', views.info),
    path('system', views.system),
    path('system/', views.system),
    path('system/<int:system_id>', views.system),
]

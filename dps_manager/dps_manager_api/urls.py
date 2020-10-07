from django.urls import path, include

from . import views

from rest_framework import routers, serializers, viewsets
from . import views

import dps_services.util as util

urlpatterns = [
    # Info API
    path('', views.info),
    
    # System API
    path(util.make_api_url('system'), views.system),
    path(util.make_api_url('system/'), views.system),
    path(util.make_api_url('system/<int:id>'), views.system),

    # Batch Process API
    path(util.make_api_url('batch_process'), views.batch_process),
    path(util.make_api_url('batch_process/'), views.batch_process),
    path(util.make_api_url('batch_process/<int:id>'), views.batch_process),

    # Progress API
    path(util.make_api_url('progress'), views.progress),
    path(util.make_api_url('progress/'), views.progress),
    path(util.make_api_url('progress/<int:id>'), views.progress),
]

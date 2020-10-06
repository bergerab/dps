from django.urls import path, include

from . import views

from rest_framework import routers, serializers, viewsets
from .models import SystemViewSet

router = routers.DefaultRouter()
router.register(r'systems', SystemViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

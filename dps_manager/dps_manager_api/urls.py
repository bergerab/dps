from django.urls import path, include

from . import views

from .object_api import Router

router = Router()
router.add(views.SystemAPI)
router.add(views.BatchProcessAPI)
router.add(views.ProgressAPI)
router.add(views.JobAPI)

urlpatterns = router.get_urls() + [
    path('', views.info),
    path('api/v1/get_required_mappings', views.get_required_mappings),
    path('api/v1/pop_job', views.pop_job),    
]

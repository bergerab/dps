from django.urls import path, include

from . import views

from .object_api import Router

router = Router()
router.add(views.SystemAPI)
router.add(views.BatchProcessAPI)
router.add(views.JobAPI)
router.add(views.ResultsAPI)

urlpatterns = router.get_urls() + [
    path('', views.info),
    path('api/v1/get_required_mappings', views.get_required_mappings),
    path('api/v1/pop_job', views.pop_job),
    path('api/v1/get_kpis', views.get_kpis),
    path('api/v1/batch_process_results', views.batch_process_results),
    path('api/v1/get_batch_process_result/<int:id>', views.get_batch_process_result),
    path('api/v1/get_signal_names', views.get_signal_names),
    path('api/v1/signal_names_table', views.signal_names_table),            
]

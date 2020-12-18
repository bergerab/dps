from django.urls import path, include

from . import views

from .object_api import Router

router = Router()
router.add(views.SystemAPI)
router.add(views.BatchProcessAPI)
router.add(views.JobAPI)
router.add(views.ResultsAPI)
router.add(views.ScheduleAPI)
router.add(views.APIKeyAPI)
router.add(views.UserAPI)

urlpatterns = router.get_urls() + [
    path('', views.info),
    path('api/v1/login', views.login),    
    path('api/v1/get_required_mappings', views.get_required_mappings),
    path('api/v1/pop_job', views.pop_job),
    path('api/v1/get_kpis', views.get_kpis),
    path('api/v1/batch_process_results', views.batch_process_results),
    path('api/v1/get_batch_process_result/<int:id>', views.get_batch_process_result),
    path('api/v1/get_signal_names', views.get_signal_names),
    path('api/v1/get_dataset_names', views.get_dataset_names),
    path('api/v1/delete_batch_process/<int:id>', views.delete_batch_process),
    path('api/v1/delete_dataset', views.delete_dataset),            
    path('api/v1/signal_names_table', views.signal_names_table),
    path('api/v1/dataset_table', views.dataset_table),
    path('api/v1/add_dataset', views.add_dataset),
    path('api/v1/get_chart_data', views.get_chart_data),
    path('api/v1/authenticate_api_key', views.authenticate_api_key),
    path('api/v1/export_dataset', views.export_dataset),            
]

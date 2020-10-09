from django.urls import path, include

from . import views

from .object_api import Router

router = Router()
router.add(views.SystemAPI)
router.add(views.BatchProcessAPI)
router.add(views.ProgressAPI)

urlpatterns = router.get_urls() + [
    path('', views.info),
]

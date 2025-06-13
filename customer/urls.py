from rest_framework.routers import DefaultRouter
from .views import *
from django.urls import path

from .views import *

router = DefaultRouter()
router.register('delivery-request', DeliveryRequestViewSet, basename='DeliveryRequestViewSet')

urlpatterns = router.urls + [



]

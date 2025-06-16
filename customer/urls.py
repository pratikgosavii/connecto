from rest_framework.routers import DefaultRouter
from .views import *
from django.urls import path

from .views import *

router = DefaultRouter()
router.register('delivery-request', DeliveryRequestViewSet, basename='DeliveryRequestViewSet')
router.register('request-vendor', RequestVendorForDeliveryViewSet, basename='RequestVendorForDeliveryViewSet')

urlpatterns = router.urls + [

    path('search-trips/', TripSearchAPIView.as_view(), name='search-trips'),
    path('view-vendor-request/', ViewVendorRequestViewSet.as_view(), name='ViewVendorRequestViewSet'),


]

from rest_framework.routers import DefaultRouter
from .views import *
from django.urls import path

from .views import *

router = DefaultRouter()
router.register('delivery-request', DeliveryRequestViewSet, basename='DeliveryRequestViewSet')
router.register('request-vendor', RequestVendorForDeliveryViewSet, basename='RequestVendorForDeliveryViewSet')
router.register('my-shipments', MyShipmentsViewSet, basename='my_shipmentsViewSet')

urlpatterns = router.urls + [

    path('search-trips/', TripSearchAPIView.as_view(), name='search-trips'),
    path('avaiable-vendors/', avaiable_vendors.as_view(), name='avaiable_vendors'),
    path('view-vendor-request/', ViewVendorRequestViewSet.as_view(), name='ViewVendorRequestViewSet'),
    
    path('assign-parcel-to-agent/', assign_parcel_to_agent, name='assign_parcel_to_agent'),

    path('connect-with-vendor/', connect_with_agent, name='connect_with_agent'),

    path("stream/get-chat-token/", get_chat_token.as_view()),
    path("stream/get-vendor-chat-token/", get_chat_token.as_view()),


]

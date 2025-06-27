from django.urls import path

from .views import *

from django.conf import settings
from django.conf.urls.static import static




from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# router.register(r'customer-address', customer_address_ViewSet, basename='pet-test-booking')

router.register('add-trip', add_trip_ViewSet, basename='add_trip_ViewSet')
router.register('request-customer', RequestCustomerForDeliveryViewSet, basename='RequestVendorForDeliveryViewSet')
router.register('vendor-my-shipments', VendorMyShipmentsViewSet, basename='Vendormy_shipmentsViewSet')


urlpatterns = [

    path('search-parcel/', ParcelSearchAPIView.as_view(), name='search-parcel'),

    path('my-shipments/<int:pk>/update-status/', update_shipment_status, name='update-shipment-status'),

    
    path('view-customer-request/', ViewCustomerRequestViewSet.as_view(), name='ViewCustomerRequestViewSet'),
    path('show-open-parcels/', ShowOpenParcels.as_view(), name='ShowOpenParcels'),
    path('open-parcels/<int:id>/', ShowOpenParcelDetail.as_view(), name='open-parcel-detail'),

    path('reject-customer-request/', reject_customer_request, name='reject_customer_request'),


]  + router.urls

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
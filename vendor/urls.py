from django.urls import path

from .views import *

from django.conf import settings
from django.conf.urls.static import static




from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# router.register(r'customer-address', customer_address_ViewSet, basename='pet-test-booking')

router.register('add-trip', add_trip_ViewSet, basename='add_trip_ViewSet')


urlpatterns = [


]  + router.urls

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
from django.urls import path

from .views import *

from django.conf import settings
from django.conf.urls.static import static




from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# router.register(r'customer-address', customer_address_ViewSet, basename='pet-test-booking')



urlpatterns = [

    
    path('add-coupon/', add_coupon, name='add_coupon'),
    path('update-coupon/<coupon_id>', update_coupon, name='update_coupon'),
    path('delete-coupon/<coupon_id>', delete_coupon, name='delete_coupon'),
    path('list-coupon/', list_coupon, name='list_coupon'),
    
    path('add-city/', add_city, name='add_city'),
    path('update-city/<city_id>', update_city, name='update_city'),
    path('delete-city/<city_id>', delete_city, name='delete_city'),
    path('list-city/', list_city, name='list_city'),
    path('get-city/', get_city, name='get_city'),

    path('add-home-banner/', add_home_banner, name='add_home_banner'),  # create or fetch list of admins
    path('update-home-banner/<home_banner_id>', update_home_banner, name='update_home_banner'),  # create or fetch list of admins
    path('list-home-banner/', list_home_banner, name='list_home_banner'),  # create or fetch list of admins
    path('delete-home-banner/<home_banner_id>', delete_home_banner, name='delete_home_banner'),  # create or fetch list of admins
    path('get-home-banner/', get_home_banner, name='get_home_banner'), 

    path('add-faq/', add_faq, name='add_faq'),  # create or fetch list of admins
    path('update-faq/<faq_id>', update_faq, name='update_faq'),  # create or fetch list of admins
    path('list-faq/', list_faq, name='list_faq'),  # create or fetch list of admins
    path('delete-faq/<faq_id>', delete_faq, name='delete_faq'),  # create or fetch list of admins
    path('faqs/', FAQListAPIView.as_view(), name='faq-list-api'),

    path('add-privacy-policy/', add_privacy_policy, name='add_privacy_policy'),  # create or fetch list of admins
    path('update-privacy-policy/<privacy_policy_id>', update_privacy_policy, name='update_privacy_policy'),  # create or fetch list of admins
    path('list-privacy-policy/', list_privacy_policy, name='list_privacy_policy'),  # create or fetch list of admins
    path('delete-privacy-policy/<privacy_policy_id>', delete_privacy_policy, name='delete_privacy_policy'),  # create or fetch list of admins
    path('privacy-policys/', privacy_policyListAPIView.as_view(), name='privacy_policy-list-api'),

    

]  + router.urls

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
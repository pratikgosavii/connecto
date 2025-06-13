from django.urls import path

from .views import *

from django.conf import settings
from django.conf.urls.static import static




from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# router.register(r'customer-address', customer_address_ViewSet, basename='pet-test-booking')

router.register('occupation-categories', OccupationCategoryViewSet, basename='occupation-category')
router.register('occupation-subcategories', OccupationSubcategoryViewSet, basename='occupation-subcategory')
router.register('occupations', OccupationViewSet, basename='occupation')


urlpatterns = [

    
    path('add-coupon/', add_coupon, name='add_coupon'),
    path('update-coupon/<coupon_id>', update_coupon, name='update_coupon'),
    path('delete-coupon/<coupon_id>', delete_coupon, name='delete_coupon'),
    path('list-coupon/', list_coupon, name='list_coupon'),
    
    path('add-occupation-category/', add_occupation_category, name='add_occupation_category'),
    path('update-occupation-category/<occupation_category_id>', update_occupation_category, name='update_occupation_category'),
    path('delete-occupation-category/<occupation_category_id>', delete_occupation_category, name='delete_occupation_category'),
    path('list-occupation-category/', list_occupation_category, name='list_occupation_category'),
    
    path('add-occupation-subcategory/', add_occupation_subcategory, name='add_subcategory_occupation'),
    path('update-occupation-subcategory/<occupation_subcategory_id>', update_occupation_subcategory, name='update_occupation_subcategory'),
    path('delete-occupation-subcategory/<occupation_subcategory_id>', delete_occupation_subcategory, name='delete_occupation_subcategory'),
    path('list-occupation-subcategory/', list_occupation_subcategory, name='list_occupation_subcategory'),
    
    path('add-occupation/', add_occupation, name='add_occupation'),
    path('update-occupation/<occupation_id>', update_occupation, name='update_occupation'),
    path('delete-occupation/<occupation_id>', delete_occupation, name='delete_occupation'),
    path('list-occupation/', list_occupation, name='list_occupation'),


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


    
    path('add-scam-category/', add_scam_category, name='add_scam_category'),  # create or fetch list of admins
    path('update-scam-category/<scam_category_id>', update_scam_category, name='update_scam_category'),  # create or fetch list of admins
    path('list-scam-category/', list_scam_category, name='list_scam_category'),  # create or fetch list of admins
    path('delete-/<scam_category_id>', delete_scam_category, name='delete_scam_category'),  # create or fetch list of admins
    path('scam-category/', scamcategory.as_view(), name='scam-category'),


]  + router.urls

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
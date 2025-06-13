from rest_framework.routers import DefaultRouter
from .views import ScamComplaintViewSet, UploadScamProofView
from django.urls import path

from .views import *

router = DefaultRouter()
router.register('scam', ScamComplaintViewSet, basename='scam')

urlpatterns = router.urls + [
    path('scams/upload-proof/<int:complaint_id>', UploadScamProofView.as_view(), name='upload-scam-proof'),


    
    path('search-user/', SearchUserView.as_view(), name='SearchUserView'),  # create or fetch list of admins


    path('add-complaint/', add_complaint, name='add_complaint'),  # create or fetch list of admins
    path('update-complaint/<complaint_id>', update_complaint, name='update_complaint'),  # create or fetch list of admins
    path('list-complaint/', list_complaint, name='list_complaint'),  # create or fetch list of admins
    path('delete-complaint/<complaint_id>', delete_complaint, name='delete_complaint'),  # create or fetch list of admins

    path('proof/<int:pk>/delete/', delete_proof, name='delete_proof'),



]

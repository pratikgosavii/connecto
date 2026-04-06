from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

from rest_framework.routers import DefaultRouter

from .views import (
    UserProfileViewSet,
    User_KYCViewSet,
    login_admin,
    SignupView,
    UserNotificationListView,
    mark_notification_read,
    ResetPasswordView,
    logout_page,
    user_list,
    update_credits,
    DeleteUserView,
    SendOTPView,
    VerifyOTPView,
    LoginAPIView,
    RegisterDeviceTokenAPIView,
)

router = DefaultRouter()
router.register(r'profile', UserProfileViewSet, basename='user-profile')
router.register(r'user-kyc', User_KYCViewSet, basename='user-kyc')


urlpatterns = [
    path('login-admin/', login_admin, name='login_admin'),
    path('signup/', SignupView.as_view(), name='signup'),

    # OTP-based auth endpoints
    path('send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('register-device-token/', RegisterDeviceTokenAPIView.as_view(), name='register-device-token'),

    # Notifications
    path('notifications/', UserNotificationListView.as_view(), name='user-notifications'),
    path('mark-notification-as-read/<pk>', mark_notification_read, name='mark_notification_read'),
    
    # Admin / misc
    path('reset-password/', ResetPasswordView.as_view(), name='ResetPasswordView'),
    path('logout/', logout_page, name='logout'),

    path('user_list/', user_list, name='user_list'),
    path('update-credits/<user_id>', update_credits, name='update_credits'),
    path('DeleteUserView/', DeleteUserView.as_view(), name='DeleteUserView'),
    
] + router.urls

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

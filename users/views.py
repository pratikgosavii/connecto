from email import message
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from firebase_admin import auth as firebase_auth
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .forms import *
from .models import User, UserToken
from .serializer import UserProfileSerializer
from .otp_utils import create_and_send_otp, verify_otp, clean_mobile


class SignupView(APIView):
    """
    Legacy Firebase-based signup. Kept for backwards compatibility,
    but new mobile apps should use OTP-based login instead.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        id_token = request.data.get("idToken")
        if not id_token:
            return Response({"error": "idToken is required"}, status=400)

        try:
            decoded_token = firebase_auth.verify_id_token(id_token)
            mobile = decoded_token.get("phone_number")
            uid = decoded_token.get("uid")

            if not mobile:
                return Response({"error": "Phone number not found in token"}, status=400)

            user = User.objects.filter(mobile=mobile).first()
            created = False

            if user:
                if not user.is_active:
                    user.is_active = True  # Reactivate if needed
                    user.save()

                if user.firebase_uid != uid:
                    user.firebase_uid = uid
                    user.save()
            else:
                user = User.objects.create(
                    mobile=mobile,
                    firebase_uid=uid
                )
                created = True

            # Handle optional fields from frontend
            optional_fields = [
                "email", "dob", "gender", "location", "marital_status",
                "income", "profession", "profile_photo", "is_agent"
            ]
            for field in optional_fields:
                if field in request.data:
                    setattr(user, field, request.data.get(field))

            user.save()

            user_details = UserProfileSerializer(user).data

            refresh = RefreshToken.for_user(user)
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "mobile": user.mobile,
                    "is_agent": user.is_agent,
                    "created": created,
                },
                "user_details": user_details,
            })

        except Exception:
            return Response({"error": "Invalid or expired Firebase token."}, status=400)


class SendOTPView(APIView):
    """
    POST /users/send-otp/
    Body: { "mobile": "<string>" }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        mobile = request.data.get("mobile", "")
        mobile_clean = clean_mobile(mobile)
        if not mobile_clean:
            return Response({"error": "Invalid mobile number"}, status=status.HTTP_400_BAD_REQUEST)

        otp_obj, success, message_text = create_and_send_otp(mobile_clean)
        if not success:
            return Response({"error": message_text}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"message": "OTP sent successfully", "mobile": mobile_clean},
            status=status.HTTP_200_OK,
        )


class VerifyOTPView(APIView):
    """
    POST /users/verify-otp/
    Body: { \"mobile\": \"...\", \"otp\": \"...\" }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        mobile = request.data.get("mobile", "")
        otp_code = request.data.get("otp", "")
        otp_obj, is_valid, message_text = verify_otp(mobile, otp_code)

        if not is_valid:
            return Response({"error": message_text}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"status": "verified"}, status=status.HTTP_200_OK)


class LoginAPIView(APIView):
    """
    POST /users/login/
    Body: { \"mobile\": \"...\", \"otp\": \"...\", \"user_type\": \"doctor\" | \"customer\" }

    Uses OTP verification and issues JWT tokens.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        mobile = request.data.get("mobile", "")
        otp_code = request.data.get("otp", "")
        user_type = (request.data.get("user_type") or "").strip().lower()

        mobile_clean = clean_mobile(mobile)
        if not mobile_clean:
            return Response({"error": "Invalid mobile number"}, status=status.HTTP_400_BAD_REQUEST)

        otp_obj, is_valid, message_text = verify_otp(mobile_clean, otp_code)
        if not is_valid:
            return Response({"error": message_text}, status=status.HTTP_400_BAD_REQUEST)

        # Map dentist roles to this project's roles:
        # treat "doctor" as agent, everything else as customer.
        is_agent_login = user_type in ["doctor", "agent"]

        user = User.objects.filter(mobile=mobile_clean).first()
        created = False

        if user:
            if not user.is_active:
                return Response(
                    {"error": "Your account has been deactivated. Please contact support."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Enforce type match (agent vs customer)
            if user.is_agent and not is_agent_login:
                return Response(
                    {"error": "This number is registered as an agent. Please use agent login."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            if not user.is_agent and is_agent_login:
                return Response(
                    {"error": "This number is registered as a customer. Please use customer login."},
                    status=status.HTTP_403_FORBIDDEN,
                )
        else:
            # Create new user
            user = User.objects.create(
                mobile=mobile_clean,
                is_agent=is_agent_login,
                is_active=True,
            )
            created = True

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # No subscription model in this project; always return False.
        is_subscribed = False

        user_details = UserProfileSerializer(user).data
        role = "doctor" if is_agent_login else "customer"

        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(
            {
                "access": access_token,
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "mobile": user.mobile,
                    "role": role,
                },
                "created": created,
                "is_subscribed": is_subscribed,
                "user_details": user_details,
            },
            status=status_code,
        )


class RegisterDeviceTokenAPIView(APIView):
    """
    POST /users/register-device-token/
    Body: { \"token\": \"<FCM device token>\" }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = (request.data.get("token") or "").strip()
        if not token:
            return Response({"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST)

        UserToken.objects.get_or_create(user=request.user, token=token)
        return Response(
            {"detail": "Device token registered"},
            status=status.HTTP_200_OK,
        )




from rest_framework import viewsets, mixins
from rest_framework.decorators import action


from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

class UserProfileViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]  # 👈 necessary for photo uploads

    @action(detail=False, methods=['get', 'put'], url_path='me')
    def me(self, request):
        user = request.user

        if request.method == 'GET':
            serializer = UserProfileSerializer(user)
            return Response(serializer.data)

        elif request.method == 'PUT':
            serializer = UserProfileSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




from rest_framework import viewsets, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser, JSONParser


from .serializer import *
from .models import *
from users.permissions import *


class User_KYCViewSet(viewsets.ModelViewSet):

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = User_KYCSerializer
    parser_classes = [MultiPartParser, JSONParser]

    def get_queryset(self):
        return UserKYC.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        if UserKYC.objects.filter(user=self.request.user).exists():
            raise ValidationError({"detail": "KYC already submitted for this user."})
        serializer.save(user=self.request.user)





from .permissions import *


class ResetPasswordView(APIView):
    def post(self, request):
        id_token = request.data.get("idToken")
        new_password = request.data.get("new_password")

        if not id_token or not new_password:
            return Response({"error": "idToken and new_password are required"}, status=400)

        try:
            # Decode the token to get UID
            decoded = firebase_auth.verify_id_token(id_token)
            uid = decoded.get("uid")

            # Update Firebase password
            firebase_auth.update_user(uid, password=new_password)

            return Response({"message": "Password updated successfully."})

        except Exception as e:
            return Response({"error": str(e)}, status=400)
        



def login_admin(request):

    forms = LoginForm()
    if request.method == 'POST':
        forms = LoginForm(request.POST)
        if forms.is_valid():
            mobile = forms.cleaned_data['mobile']
            password = forms.cleaned_data['password']
            print(mobile)
            print(password)
            user = authenticate(mobile=mobile, password=password)
            if user:
                login(request, user)

                if user.is_superuser:
                    print('---------------------------------')
                    print('---------------------------------')
                    print('---------------------------------')
                return redirect('dashboard')
            else:
                messages.error(request, 'wrong username password')
    context = {'form': forms}
    return render(request, 'adminLogin.html', context)

def logout_page(request):
    logout(request)
    return redirect('login_admin')

def customer_user_list(request):

    data = User.objects.all()

    return render(request, 'user_list.html', { 'data' : data})




def user_list(request):

    data = User.objects.select_related('userkyc').all()

    return render(request, 'user_list.html', { 'data' : data})




class DeleteUserView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.is_active = False
        user.save()
        return Response({"message": "User account deactivated successfully."}, status=status.HTTP_200_OK)



# views.py

from rest_framework import generics, permissions
from .models import Notification
from .serializer import NotificationSerializer

class UserNotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')


from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notification_read(request, pk):
    try:
        note = Notification.objects.get(id=pk, user=request.user)
        note.is_read = True
        note.save()
        return Response({'status': 'marked as read'})
    except Notification.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)
    




def update_credits(request, user_id):

    user_instance = User.objects.get(id = user_id)

    if request.method == 'POST':

        credits = request.POST.get("credits")

        user_credits = UserCredit.objects.get(user = user_instance)
        user_credits.credits = credits
        user_credits.save()

        return redirect('user_list')    
    
    else:

        

        context = {
            'user_instance': user_instance
        }
        return render(request, 'update_credits.html', context)

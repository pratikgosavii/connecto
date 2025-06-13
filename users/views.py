from email import message
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


from .forms import *


# def login_page(request):
#     forms = LoginForm()
#     if request.method == 'POST':
#         forms = LoginForm(request.POST)
#         if forms.is_valid():
#             username = forms.cleaned_data['username']
#             password = forms.cleaned_data['password']
#             print(username)
#             print(password)
#             user = authenticate(username=username, password=password)
#             if user:
#                 login(request, user)

#                 if user.is_doctor:
#                     print('---------------------------------')
#                     print('---------------------------------')
#                     print('---------------------------------')
#                 return redirect('dashboard')
#             else:
#                 messages.error(request, 'wrong username password')
#     context = {'form': forms}
#     return render(request, 'adminLogin.html', context)

from firebase_admin import auth as firebase_auth
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User  # Your custom user model


class SignupView(APIView):
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

            refresh = RefreshToken.for_user(user)
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "mobile": user.mobile,
                    "is_agent": user.is_agent,
                    "created": created,
                }
            })

        except Exception as e:
            return Response({"error": "Invalid or expired Firebase token."}, status=400)




from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from .serializer import UserProfileSerializer
from .models import User
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
        return user_kyc.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        if user_kyc.objects.filter(user=self.request.user).exists():
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

    data = User.objects.all()

    return render(request, 'user_list.html', { 'data' : data})

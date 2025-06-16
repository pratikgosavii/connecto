
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import *
from masters.models import *
from masters.serializers import *



from rest_framework import serializers

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'firebase_uid',
            'mobile',
            'name',
            'email',
            'profile_photo',
            'address_line1',
            'address_line2',
            'pincode',
            'state',
            'city',
            'country',
            'qualification',
            'year_of_graduation',
        ]
        read_only_fields = ['id', 'mobile', 'firebase_uid']  # Mobile comes from Firebase
        extra_kwargs = {
            'firebase_uid': {'required': True},
            'email': {'required': False, 'allow_blank': True, 'allow_null': True},
        }



class User_KYCSerializer(serializers.ModelSerializer):
    class Meta:
        model = user_kyc
        fields = ['id', 'user', 'adhar_card', 'pan_card', 'driving_licence', 'approved']
        read_only_fields = ['user', 'approved']

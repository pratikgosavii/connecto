
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import *
from masters.models import *
from masters.serializers import *


from customer.models import *


from rest_framework import serializers

class UserProfileSerializer(serializers.ModelSerializer):

    is_approved = serializers.SerializerMethodField()

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
            'is_approved',
        ]
        read_only_fields = ['id', 'mobile', 'firebase_uid', 'is_approved']

    def get_is_approved(self, obj):
        if hasattr(obj, "userkyc") and obj.userkyc:
            return obj.userkyc.is_approved
        return False
    
    def to_representation(self, instance):
        data = super().to_representation(instance)

        request = self.context.get('request')
        parcel = self.context.get('parcel')
        trip = self.context.get('trip')

        # By default, always hide mobile
        hide_mobile = True

        # If context provided and user is connected, show mobile
        if request and parcel and trip:
            is_connected = UserConnectionLog.objects.filter(
                user=request.user,
                parcel=parcel,
                trip=trip,
            ).exists()
            if is_connected:
                hide_mobile = False

        if hide_mobile:
            data.pop('mobile', None)

        try:
            data['credits'] = instance.usercredit.credits
        except UserCredit.DoesNotExist:
            data['credits'] = 0
            
        return data



class User_KYCSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserKYC
        fields = ['id', 'user', 'adhar_card', 'pan_card', 'driving_licence', 'is_approved']
        read_only_fields = ['user', 'is_approved']



# serializers.py

from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'is_read', 'created_at']

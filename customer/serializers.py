from rest_framework import serializers
from .models import *
from vendor.models import *
from vendor.serializers import *
from users.serializer import *





class DeliveryRequestSerializer(serializers.ModelSerializer):

    user = UserProfileSerializer(read_only=True)  # nest user details


    class Meta:
        model = DeliveryRequest
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'is_agent_assigned']



class RequestVendorForDeliverySerializer(serializers.ModelSerializer):

    user = UserProfileSerializer(read_only=True)  # nest user details
    trip_details = trip_Serializer(source='trip', read_only=True)
    parcel = DeliveryRequestSerializer()
    class Meta:
        model = Request_Vendor_for_Delivery
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'status', 'trip_details']


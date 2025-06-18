from rest_framework import serializers

from .models import *
from vendor.models import *
from vendor.serializers import *
from users.serializer import *


class RequestTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestType
        fields = ['id', 'name']


class DeliveryRequestSerializer(serializers.ModelSerializer):

    request_type_details = RequestTypeSerializer(source="request_type", many=True, read_only=True)

    request_type = serializers.PrimaryKeyRelatedField(
            queryset=RequestType.objects.all(),
            many=True
        )

    user = UserProfileSerializer(read_only=True)  # nest user details
    pickup_city_details = city_Serializer(source="pickup_city", read_only=True)
    destination_city_details = city_Serializer(source="destination_city", read_only=True)

    class Meta:
        model = DeliveryRequest
        fields = '__all__'
        read_only_fields = ['user', 'request_type_details', 'created_at', 'is_agent_assigned']



class RequestVendorForDeliverySerializer(serializers.ModelSerializer):

    user = UserProfileSerializer(read_only=True)  # nest user details
    trip_details = trip_Serializer(source='trip', read_only=True)
    parcel_details = DeliveryRequestSerializer(read_only=True)
    
    class Meta:
        model = Request_Vendor_for_Delivery
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'status', 'trip_details']


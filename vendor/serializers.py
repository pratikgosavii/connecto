
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import *
from masters.models import *
from masters.serializers import *



from rest_framework import serializers

from users.serializer import *

class trip_Serializer(serializers.ModelSerializer):

    user = UserProfileSerializer(read_only=True)  # nest user details
    source_details = city_Serializer(source="source", read_only=True)
    destination_details = city_Serializer(source="destination", read_only=True)

    class Meta:
        model = trip
        fields = '__all__'
        read_only_fields = ['user']



class RequestCustomerForDeliverySerializer(serializers.ModelSerializer):
    
    from customer.serializers import DeliveryRequestSerializer

    user = UserProfileSerializer(read_only=True)  # nest user details
    trip_details = trip_Serializer(read_only=True)
    parcel_details = DeliveryRequestSerializer(source='parcel', read_only=True)
    
    

    class Meta:
        model = Request_Customer_for_Delivery
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'trip_details', 'status']



# serializers.py

from rest_framework import serializers
from customer.models import Customer_Order

class VendorShipmentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer_Order
        fields = ['status']  # Only 'status' is editable


from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import *
from masters.models import *
from masters.serializers import *



from rest_framework import serializers

from users.serializer import *

class trip_Serializer(serializers.ModelSerializer):

    user = UserProfileSerializer(read_only=True)  # nest user details
    
    
    class Meta:
        model = trip
        fields = '__all__'
        read_only_fields = ['user']



class RequestCustomerForDeliverySerializer(serializers.ModelSerializer):
    
    from customer.serializers import DeliveryRequestSerializer

    user = UserProfileSerializer(read_only=True)  # nest user details
    trip_details = trip_Serializer(source = 'trip' , read_only=True)
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
    
    def validate_status(self, value):
        if value == "completed":
            raise serializers.ValidationError("Can't mark as completed")
        return value
    

class CustomerOrderStatusUpdateSerializer(serializers.ModelSerializer):
    otp = serializers.CharField(write_only=True)

    class Meta:
        model = Customer_Order
        fields = ['status', 'otp']

    def validate(self, attrs):
        instance = self.instance
        otp = attrs.get('otp')

        if otp != instance.otp:
            raise serializers.ValidationError({"otp": "OTP is incorrect"})

        if attrs.get('status') != 'delivered':
            raise serializers.ValidationError({"status": "Only 'delivered' status is allowed."})

        return attrs
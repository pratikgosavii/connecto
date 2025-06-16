from rest_framework import serializers
from .models import *
from vendor.models import *



class RequestVendorForDeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = Request_Vendor_for_Delivery
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'status']



class DeliveryRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryRequest
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'is_agent_assigned']


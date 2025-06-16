
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import *
from masters.models import *
from masters.serializers import *



from rest_framework import serializers


class trip_Serializer(serializers.ModelSerializer):
    class Meta:
        model = trip
        fields = '__all__'
        read_only_fields = ['user']



class RequestCustomerForDeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = Request_Customer_for_Delivery
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'status']
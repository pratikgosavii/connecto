
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

    user = UserProfileSerializer(read_only=True)  # nest user details


    class Meta:
        model = Request_Customer_for_Delivery
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'status']
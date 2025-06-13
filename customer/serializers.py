from rest_framework import serializers
from .models import *


class DeliveryRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryRequest
        fields = '__all__'
        read_only_fields = ['user', 'created_at']


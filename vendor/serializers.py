
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import *
from masters.models import *
from masters.serializers import *



from rest_framework import serializers


class add_trip_Serializer(serializers.ModelSerializer):
    class Meta:
        model = add_trip
        fields = '__all__'
        read_only_fields = ['user']

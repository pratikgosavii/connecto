
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import *
from masters.models import *
from masters.serializers import *



class UserProfileSerializer(serializers.ModelSerializer):
    keywords = serializers.ListField(
        child=serializers.CharField(), required=False, write_only=True
    )
    keywords_display = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ['id', 'mobile']
        extra_kwargs = {
            'is_active': {'required': False},
            'email': {'required': False, 'allow_blank': True, 'allow_null': True},
        }

    def get_keywords_display(self, obj):
        return obj.keywords.split(",") if obj.keywords else []

    def update(self, instance, validated_data):
        keywords = validated_data.pop("keywords", None)
        if keywords is not None:
            validated_data["keywords"] = ",".join(keywords)
        return super().update(instance, validated_data)

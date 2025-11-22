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

    class Meta:
        model = DeliveryRequest
        fields = '__all__'
        read_only_fields = ['user', 'request_type_details', 'created_at', 'is_agent_assigned']


class Customer_OrderSerializer(serializers.ModelSerializer):

    trip_details = trip_Serializer(source='trip', read_only=True)
    parcel_details = DeliveryRequestSerializer(source='parcel', read_only=True)


    class Meta:
        model = Customer_Order
        fields = '__all__'



class RequestVendorForDeliverySerializer(serializers.ModelSerializer):

    user = UserProfileSerializer(read_only=True)  # nest user details
    trip_details = trip_Serializer(source='trip', read_only=True)
    parcel_details = DeliveryRequestSerializer(source="parcel", read_only=True)
    
    def validate(self, attrs):
        request = self.context.get("request")
        user = request.user if request else None
        parcel = attrs.get("parcel")
        trip_instance = attrs.get("trip")
        if user and parcel and trip_instance:
            if Request_Vendor_for_Delivery.objects.filter(user=user, parcel=parcel, trip=trip_instance).exists():
                raise serializers.ValidationError({"detail": "you already request for this trip"})
        return attrs

    class Meta:
        model = Request_Vendor_for_Delivery
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'status', 'trip_details']




class DeliveryRatingSerializer(serializers.ModelSerializer):
    vendor = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    
    class Meta:
        model = DeliveryRating
        fields = ['vendor', 'rating', 'feedback', 'shipment']


class SupportTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportTicket
        fields = ['id', 'subject', 'shipment', 'is_resolved', 'created_at']
        read_only_fields = ['id', 'is_resolved', 'created_at']




class TicketMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.name', read_only=True)
    is_from_user = serializers.SerializerMethodField()

    class Meta:
        model = TicketMessage
        fields = ['id', 'ticket', 'sender', 'sender_name', 'message', 'created_at', 'is_from_user']
        read_only_fields = ['sender', 'created_at']

    def get_is_from_user(self, obj):
        request = self.context.get('request')
        return obj.sender == request.user if request else False
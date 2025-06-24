from django.shortcuts import render

# Create your views here.

from rest_framework import viewsets, permissions

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import *
from customer.models import *
from .serializers import *
from customer.serializers import *
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser



class add_trip_ViewSet(ModelViewSet):
    queryset = trip.objects.all()
    serializer_class = trip_Serializer
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]  # Handles file uploads (car photo, license, etc.)

    def perform_create(self, serializer):
        # Attach the logged-in user as the trip owner
        serializer.save(user=self.request.user)

    def get_queryset(self):
        # Return only the trips created by the current user
        return trip.objects.filter(user=self.request.user)
    


    
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend

from .filters import *

class RequestCustomerForDeliveryViewSet(viewsets.ModelViewSet):


    serializer_class = RequestCustomerForDeliverySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Request_Customer_for_Delivery.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        trip = serializer.validated_data.get('trip')
        parcel = serializer.validated_data.get('parcel')

        if Request_Customer_for_Delivery.objects.filter(trip=trip, parcel=parcel).exists():
            raise serializers.ValidationError("A request already exists for this trip and parcel.")

        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        delivery_request = self.get_object()
        if delivery_request.status in ['accepted', 'pending']:
            delivery_request.status = 'cancelled'
            delivery_request.save()
            return Response({'detail': 'Request cancelled successfully.'}, status=status.HTTP_200_OK)
        return Response({'detail': 'Cannot cancel this request.'}, status=status.HTTP_400_BAD_REQUEST)


from customer.filters import *

class ParcelSearchAPIView(generics.ListAPIView):
    queryset = DeliveryRequest.objects.all()
    serializer_class = DeliveryRequestSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = DeliveryRequestFilter




class ViewCustomerRequestViewSet(generics.ListAPIView):
    
    serializer_class = RequestVendorForDeliverySerializer
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        user = self.request.user
    
        parcel_id = self.request.query_params.get('parcel')  # ?parcel=123

        queryset = Request_Vendor_for_Delivery.objects.filter(trip__user=user)

        if parcel_id:
            queryset = queryset.filter(parcel__id = parcel_id)

        return queryset

    def post(self, request):
        action_type = request.data.get('action')   # 'accept' or 'cancel'
        request_id = request.data.get('id')        # delivery request ID

        if not request_id or action_type not in ['accept', 'cancel']:
            return Response({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            delivery_request = Request_Vendor_for_Delivery.objects.get(id=request_id, trip__user=request.user)
        except Request_Vendor_for_Delivery.DoesNotExist:
            return Response({'error': 'Request not found'}, status=status.HTTP_404_NOT_FOUND)

        # Handle actions
        if action_type == 'accept':
            if delivery_request.status == 'pending':
                delivery_request.status = 'accepted'
                delivery_request.save()
                Notification.objects.create(
                    user=delivery_request.user,
                    title='Delivery Request Accepted',
                    message=f'Your delivery request #{delivery_request.id} has been accepted.'
                )
                return Response({'detail': 'Request accepted.'})
            return Response({'error': 'Only pending requests can be accepted.'}, status=400)

        if action_type == 'cancel':
            if delivery_request.status in ['pending', 'accepted']:
                delivery_request.status = 'cancelled'
                delivery_request.save()
                Notification.objects.create(
                    user=delivery_request.user,
                    title='Delivery Request Cancelled',
                    message=f'Your delivery request #{delivery_request.id} has been cancelled.'
                )
                return Response({'detail': 'Request cancelled.'})
            return Response({'error': 'Cannot cancel this request.'}, status=400)

class RequestVendorForDeliveryViewSet(viewsets.ModelViewSet):

    serializer_class = RequestVendorForDeliverySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Request_Vendor_for_Delivery.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        request_obj = serializer.save(user=self.request.user)

        # ✅ Create notification on creation
        Notification.objects.create(
            user=self.trip.user,
            title='Delivery Request Created',
            message=f'Your delivery request #{request_obj.id} has been submitted successfully.'
        )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        delivery_request = self.get_object()
        if delivery_request.status in ['accepted', 'pending']:
            delivery_request.status = 'cancelled'
            delivery_request.save()

            # ✅ Create notification on cancel
            Notification.objects.create(
                user=request.user,
                title='Delivery Request Cancelled',
                message=f'Your delivery request #{delivery_request.id} has been cancelled.'
            )

            return Response({'detail': 'Request cancelled and notification sent.'}, status=status.HTTP_200_OK)

        return Response({'detail': 'Cannot cancel this request.'}, status=status.HTTP_400_BAD_REQUEST)


    
class ShowOpenParcels(generics.ListAPIView):
    
    serializer_class = DeliveryRequestSerializer
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        user = self.request.user
        return DeliveryRequest.objects.filter(is_agent_assigned=False)




class VendorMyShipmentsViewSet(viewsets.ModelViewSet):

    queryset = Customer_Order.objects.all()
    serializer_class = Customer_OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    

    def get_queryset(self):

        return Customer_Order.objects.filter(trip__user=self.request.user)


from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions


@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_shipment_status(request, pk):
    try:
        order = Customer_Order.objects.get(pk=pk, trip__user=request.user)
    except Customer_Order.DoesNotExist:
        return Response({'detail': 'Shipment not found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = VendorShipmentStatusSerializer(order, data=request.data, partial=True)
    if serializer.is_valid():
        instance = serializer.save()
        Notification.objects.create(
                    user=instance.user,
                    title='Delivery Status Changed',
                    message=f'Your delivery request #{instance.id} has been {instance.status}.'
                )
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
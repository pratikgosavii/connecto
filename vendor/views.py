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
from rest_framework.decorators import api_view, permission_classes




class add_trip_ViewSet(ModelViewSet):
    queryset = trip.objects.all().order_by('-id') 
    serializer_class = trip_Serializer
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]  # Handles file uploads (car photo, license, etc.)

    def perform_create(self, serializer):
        # Attach the logged-in user as the trip owner
        serializer.save(user=self.request.user)

    def get_queryset(self):
        # Return only the trips created by the current user
        return trip.objects.filter(user=self.request.user).order_by('-id') 
    


    
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
        return Request_Customer_for_Delivery.objects.filter(user=self.request.user).order_by('-id') 

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

        queryset = Request_Vendor_for_Delivery.objects.filter(trip__user=user).exclude(status__in =['cancelled_by_customer', 'rejected_by_vendor', 'accepted']).order_by('-id') 

        if parcel_id:
            queryset = queryset.filter(parcel__id = parcel_id)

        return queryset

    def post(self, request):
        request_id = request.data.get('id')
        new_status = request.data.get('status')  # should be 'accepted' or 'rejected_by_vendor'
        request_price = request.data.get('request_price')

        if not request_id or new_status not in ['accepted', 'rejected_by_vendor', 'cancelled_by_customer']:
            return Response({'error': 'Invalid status or request ID.'}, status=400)

        try:
            delivery_request = Request_Vendor_for_Delivery.objects.get(id=request_id, trip__user=request.user)
        except Request_Vendor_for_Delivery.DoesNotExist:
            return Response({'error': 'Request not found or unauthorized.'}, status=404)

        if delivery_request.status != 'pending':
            return Response({'error': 'Only pending requests can be updated.'}, status=400)

        if new_status == 'accepted_by_vendor':
            if not request_price:
                return Response({'error': 'request_price is required when accepting.'}, status=400)

            delivery_request.status = 'accepted_by_vendor'
            delivery_request.request_price = request_price
            delivery_request.save()

            Notification.objects.create(
                user=delivery_request.user,
                title='Delivery Request accepted_by_vendor',
                message=f'Your delivery request #{delivery_request.id} was accepted_by_vendor by the vendor.'
            )

            return Response({'detail': 'Request accepted_by_vendor and price updated.'}, status=200)

        elif new_status == 'rejected_by_vendor':
            delivery_request.status = 'rejected_by_vendor'
            delivery_request.save()

            Notification.objects.create(
                user=delivery_request.user,
                title='Delivery Request Rejected',
                message=f'Your delivery request #{delivery_request.id} was rejected by the vendor.'
            )

            return Response({'detail': 'Request rejected by vendor.'}, status=200)



class ShowOpenParcels(generics.ListAPIView):
    
    serializer_class = DeliveryRequestSerializer
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        return DeliveryRequest.objects.filter(is_agent_assigned=False).exclude(user = self.request.user).order_by('-id') 


class ShowOpenParcelDetail(generics.RetrieveAPIView):
    queryset = DeliveryRequest.objects.filter(is_agent_assigned=False)
    serializer_class = DeliveryRequestSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'  # or 'pk' if you use the default


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_customer_request(request):
    user = request.user
    parcel_id = request.data.get("parcel_id")
    trip_id = request.data.get("trip_id")

    try:
        parcel = DeliveryRequest.objects.get(id=parcel_id, user=user)
        trip_instance = trip.objects.get(id=trip_id)

        # Check if already connected
        try:

            request_instance = Request_Vendor_for_Delivery.objects.get(trip = trip_instance, parcel=parcel)
        except Request_Vendor_for_Delivery:
            return Response({"error": "Request not found"}, status=404)

        print('--------------------')



        if request_instance.status != "accepted":
        
            request_instance.status = "rejected_by_vendor"
            request_instance.save()

            return Response({ "message": "Request cancled successfully"}, status=200)


        else:

            return Response({ "message": "Request already accepted"}, status=200)



    except DeliveryRequest.DoesNotExist:
        return Response({"error": "Parcel not found"}, status=404)
    except trip.DoesNotExist:
        return Response({"error": "Trip not found"}, status=404)





class VendorMyShipmentsViewSet(viewsets.ModelViewSet):

    queryset = Customer_Order.objects.all().order_by('-id') 
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

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
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        delivery_request = self.get_object()
        if delivery_request.status in ['accepted', 'pending']:
            delivery_request.status = 'cancelled'
            delivery_request.save()
            return Response({'detail': 'Request cancelled successfully.'}, status=status.HTTP_200_OK)
        return Response({'detail': 'Cannot cancel this request.'}, status=status.HTTP_400_BAD_REQUEST)




class ViewCustomerRequestViewSet(generics.ListAPIView):
    
    serializer_class = RequestCustomerForDeliverySerializer
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        user = self.request.user
        return Request_Customer_for_Delivery.objects.filter(parcel__user=user)


    
class ShowOpenParcels(generics.ListAPIView):
    
    serializer_class = DeliveryRequestSerializer
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        user = self.request.user
        return DeliveryRequest.objects.filter(is_agent_assigned=False)


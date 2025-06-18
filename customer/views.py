from rest_framework import viewsets, permissions
from .models import *
from .serializers import *

class DeliveryRequestViewSet(viewsets.ModelViewSet):
    queryset = DeliveryRequest.objects.all()
    serializer_class = DeliveryRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from vendor.models import *
from vendor.serializers import *
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend

from vendor.filters import *

class TripSearchAPIView(generics.ListAPIView):
    queryset = trip.objects.all()
    serializer_class = trip_Serializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TripFilter


class avaiable_vendors(generics.ListAPIView):
    serializer_class = trip_Serializer
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        
        queryset = trip.objects.filter(
            start_date_time__gt=timezone.now(),  # only future trips
        )


        return queryset

class ViewVendorRequestViewSet(generics.ListAPIView):
    serializer_class = RequestCustomerForDeliverySerializer
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        user = self.request.user
        parcel_id = self.request.query_params.get('parcel')  # ?parcel=123

        queryset = Request_Customer_for_Delivery.objects.filter(parcel__user=user)

        if parcel_id:
            queryset = queryset.filter()

        return queryset



from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

class RequestVendorForDeliveryViewSet(viewsets.ModelViewSet):


    serializer_class = RequestVendorForDeliverySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Request_Vendor_for_Delivery.objects.filter(user=self.request.user)

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

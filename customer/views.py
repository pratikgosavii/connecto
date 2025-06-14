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

from vendor.filters import AddTripFilter

class TripSearchAPIView(generics.ListAPIView):
    queryset = add_trip.objects.all()
    serializer_class = add_trip_Serializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = AddTripFilter
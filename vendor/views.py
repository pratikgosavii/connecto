from django.shortcuts import render

# Create your views here.


from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import *
from .serializers import *
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser



class add_trip_ViewSet(ModelViewSet):
    queryset = add_trip.objects.all()
    serializer_class = add_trip_Serializer
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]  # Handles file uploads (car photo, license, etc.)

    def perform_create(self, serializer):
        # Attach the logged-in user as the trip owner
        serializer.save(user=self.request.user)

    def get_queryset(self):
        # Return only the trips created by the current user
        return add_trip.objects.filter(user=self.request.user)
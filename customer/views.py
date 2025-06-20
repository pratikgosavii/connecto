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
            departure_datetime__gt=timezone.now(),  # only future trips
        )


        return queryset
    

from django.utils import timezone  # ✅ CORRECT


class ViewVendorRequestViewSet(generics.ListAPIView):
    serializer_class = RequestCustomerForDeliverySerializer
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        user = self.request.user
        parcel_id = self.request.query_params.get('parcel')  # ?parcel=123

        print(parcel_id)
        queryset = Request_Customer_for_Delivery.objects.filter(parcel__user=user)

        if parcel_id:
            print('-------------------------------')
            print('-------------------------------')
            print('-------------------------------')
            queryset = queryset.filter(parcel__id = parcel_id)

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


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def connect_with_agent(request):
    user = request.user
    parcel_id = request.data.get("parcel_id")
    trip_id = request.data.get("trip_id")

    try:
        parcel = DeliveryRequest.objects.get(id=parcel_id, user=user)
        trip_instance = trip.objects.get(id=trip_id)

        # Check if already connected
        if UserConnectionLog.objects.filter(user=user, parcel=parcel, trip=trip_instance).exists():
            return Response({"message": "Already connected."}, status=200)

        # Check if user has credit
        user_credit = UserCredit.objects.get(user=user)
        if user_credit.credits <= 0:
            return Response({"error": "Insufficient credits"}, status=400)

        # Deduct 1 credit
        user_credit.credits -= 1
        user_credit.save()

        # Log connection
        UserConnectionLog.objects.create(user=user, parcel=parcel, trip=trip_instance)

        agent_data = UserProfileSerializer(trip_instance.user, context={'request': request,'parcel': parcel,'trip': trip_instance}).data
        return Response({
            "message": "Connected successfully",
            "agent": agent_data
        }, status=200)



    except DeliveryRequest.DoesNotExist:
        return Response({"error": "Parcel not found"}, status=404)
    except trip.DoesNotExist:
        return Response({"error": "Trip not found"}, status=404)





from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_parcel_to_agent(request):
    user = request.user
    parcel_id = request.data.get('parcel_id')
    trip_id = request.data.get('trip_id')

    if not parcel_id or not trip_id:
        return Response({"error": "parcel_id and trip_id are required"}, status=400)

    try:
        parcel = DeliveryRequest.objects.get(id=parcel_id, user=user)
        trip_instance = trip.objects.get(id=trip_id)
        agent_user = trip_instance.user  # Assuming trip.user is the agent

        # Check if user is connected with this agent for this parcel & trip
        if not UserConnectionLog.objects.filter(user=user, parcel=parcel, trip=trip_instance).exists():
            return Response({"error": "You are not connected with this agent for this parcel"}, status=403)

        # Check if already assigned to prevent duplicates or logic for update
        if Customer_Order.objects.filter(parcel=parcel, agent=agent_user).exists():
            return Response({"message": "Parcel already assigned to this agent"}, status=200)

        # Create Customer_Order / assignment
        order = Customer_Order.objects.create(
            parcel=parcel,
            agent=agent_user,
            user=user,
            status='assigned',
            assigned_at=timezone.now(),
        )

        return Response({
            "message": "Parcel assigned successfully",
            "order_id": order.id,
            "status": order.status
        })

    except DeliveryRequest.DoesNotExist:
        return Response({"error": "Parcel not found"}, status=404)
    except trip.DoesNotExist:
        return Response({"error": "Trip not found"}, status=404)




# views.py
from stream_chat import StreamChat
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
import os

from .utils import generate_channel_id


class get_chat_token(APIView):
    
    permission_classes = [IsAuthenticated]

    def get(self, request):
        api_key = os.getenv("STREAM_API_KEY")
        api_secret = os.getenv("STREAM_API_SECRET")

        print("✅ STREAM_API_KEY from .env:", os.getenv("STREAM_API_KEY"))

        print(api_key)
        print(api_secret)

        if not api_key or not api_secret:
            return Response({"error": "Missing Stream credentials"}, status=500)

        UserConnectionLog_id = request.GET.get("UserConnectionLog_id")
        user_id = str(request.user.id)

        if not UserConnectionLog_id:
            return Response({"error": "Missing UserConnectionLog_id"}, status=400)

        try:
            UserConnectionLog_instance = UserConnectionLog.objects.get(id=UserConnectionLog_id, user = request.user)
        except UserConnectionLog.DoesNotExist:
            return Response({"error": "Please use connect first"}, status=404)

        vendor_user_id = str(UserConnectionLog_instance.trip.user.id)

        # Generate consistent channel ID
        channel_id = generate_channel_id(user_id, vendor_user_id)

        # Initialize Stream client
        client = StreamChat(api_key=api_key, api_secret=api_secret)

        # Upsert both users
        client.upsert_user({"id": user_id})
        client.upsert_user({"id": vendor_user_id})

        # Create token for authenticated user
        token = client.create_token(user_id)

        return Response({
            "user_id": user_id,
            "token": token,
            "channel_id": channel_id,
            "api_key": api_key,  # for frontend use
        })



class get_chat_vendor_token(APIView):
    
    permission_classes = [IsAuthenticated]

    def get(self, request):
        api_key = os.getenv("STREAM_API_KEY")
        api_secret = os.getenv("STREAM_API_SECRET")

        print("✅ STREAM_API_KEY from .env:", os.getenv("STREAM_API_KEY"))

        print(api_key)
        print(api_secret)

        if not api_key or not api_secret:
            return Response({"error": "Missing Stream credentials"}, status=500)

        UserConnectionLog_id = request.GET.get("UserConnectionLog_id")
        vendor_user_id = str(request.user.id)

        if not UserConnectionLog_id:
            return Response({"error": "Missing UserConnectionLog_id"}, status=400)

        try:
            UserConnectionLog_instance = UserConnectionLog.objects.get(id=UserConnectionLog_id, user = request.user)
        except UserConnectionLog.DoesNotExist:
            return Response({"error": "Please use connect first"}, status=404)

        user_id = str(UserConnectionLog_instance.user.id)

        # Generate consistent channel ID
        channel_id = generate_channel_id(user_id, vendor_user_id)

        # Initialize Stream client
        client = StreamChat(api_key=api_key, api_secret=api_secret)

        # Upsert both users
        client.upsert_user({"id": user_id})
        client.upsert_user({"id": vendor_user_id})

        # Create token for authenticated user
        token = client.create_token(user_id)

        return Response({
            "user_id": user_id,
            "token": token,
            "channel_id": channel_id,
            "api_key": api_key,  # for frontend use
        })

from rest_framework import viewsets, permissions
from .models import *
from .serializers import *

class DeliveryRequestViewSet(viewsets.ModelViewSet):
    queryset = DeliveryRequest.objects.all().order_by('-id') 
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

        queryset = Request_Customer_for_Delivery.objects.filter(
            parcel__user=user
        ).exclude(
            status__in=['rejected_by_vendor', 'rejected_by_customer', 'cancelled_by_customer']
        ).order_by('-id')

        if parcel_id:
            queryset = queryset.filter(parcel__id=parcel_id)

        return queryset



from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

class RequestVendorForDeliveryViewSet(viewsets.ModelViewSet):

    serializer_class = RequestVendorForDeliverySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Request_Vendor_for_Delivery.objects.filter(user=self.request.user).order_by('-id')

    def perform_create(self, serializer):
        request_obj = serializer.save(user=self.request.user)

        # ✅ Create notification on creation
       
   

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def connect_with_agent(request):
    user = request.user
    parcel_id = request.data.get("parcel_id")
    trip_id = request.data.get("trip_id")
    request_origin = request.data.get("request_origin")

    print('--------------------')

    print(request_origin)

    try:

        parcel = DeliveryRequest.objects.get(id=parcel_id, user=user)
        trip_instance = trip.objects.get(id=trip_id)

        # Check if already connected
        if UserConnectionLog.objects.filter(user=user, parcel=parcel, trip=trip_instance).exists():
            agent_data = UserProfileSerializer(trip_instance.user, context={'request': request,'parcel': parcel,'trip': trip_instance}).data

            instance = UserConnectionLog.objects.get(user=user, parcel=parcel, trip=trip_instance)

            if request_origin == "customer":
                print('----------1----------')

                request_instance = Request_Vendor_for_Delivery.objects.get(
                    user=request.user, trip=trip_instance, parcel=parcel
                )
                request_instance.status = "accepted"
                request_instance.save()

            elif request_origin == "vendor":

                print('----------2----------')

                request_instance = Request_Customer_for_Delivery.objects.get(
                    trip=trip_instance, parcel=parcel
                )
                request_instance.status = "accepted"
                request_instance.save()



            return Response({
                "message": "Already connected",
                "agent": agent_data,
                "connect_id" : instance.id,

            }, status=200)

        # Check if user has credit
        user_credit = UserCredit.objects.get(user=user)
        if user_credit.credits <= 0:
            return Response({"error": "Insufficient credits"}, status=400)

        # Deduct 1 credit
        user_credit.credits -= 1
        user_credit.save()

        # Log connection
        instance = UserConnectionLog.objects.create(user=user, parcel=parcel, trip=trip_instance)


        if request_origin == "customer":
            print('----------1----------')

            request_instance = Request_Vendor_for_Delivery.objects.get(
                user=request.user, trip=trip_instance, parcel=parcel
            )
            request_instance.status = "accepted"
            request_instance.save()

        elif request_origin == "vendor":

            print('----------2----------')

            request_instance = Request_Customer_for_Delivery.objects.get(
                user=request.user, trip=trip_instance, parcel=parcel
            )
            request_instance.status = "accepted"
            request_instance.save()

        if Customer_Order.objects.filter(parcel=parcel, trip=trip_instance).exists():
            assigned = True
        else:    
            assigned = True
        agent_data = UserProfileSerializer(trip_instance.user, context={'request': request,'parcel': parcel,'trip': trip_instance}).data
        return Response({
            "message": "Connected successfully",
            "connect_id" : instance.id,
            "agent": agent_data,
            "assigned" : assigned
        }, status=200)



    except DeliveryRequest.DoesNotExist:
        return Response({"error": "Parcel not found"}, status=404)
    except trip.DoesNotExist:
        return Response({"error": "Trip not found"}, status=404)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_vendor_request(request):
    user = request.user
    parcel_id = request.data.get("parcel_id")
    trip_id = request.data.get("trip_id")

    try:
        parcel = DeliveryRequest.objects.get(id=parcel_id, user=user)
        trip_instance = trip.objects.get(id=trip_id)

        # Check if already connected
        try:

            request_instance = Request_Customer_for_Delivery.objects.get(trip = trip_instance, parcel=parcel)
        except Request_Customer_for_Delivery:
            return Response({"error": "Request not found"}, status=404)

        print('--------------------')



        if request_instance.status != "accepted":
        
            request_instance.status = "rejected_by_customer"
            request_instance.save()

            return Response({ "message": "Request cancled successfully"}, status=200)


        else:

            return Response({ "message": "Request already accepted"}, status=200)



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
        
        parcel.is_agent_assigned = True
        parcel.save()

        # Check if user is connected with this agent for this parcel & trip
        if not UserConnectionLog.objects.filter(user=user, parcel=parcel, trip=trip_instance).exists():
            return Response({"error": "You are not connected with this agent for this parcel"}, status=403)

        # Check if already assigned to prevent duplicates or logic for update
        if Customer_Order.objects.filter(parcel=parcel, trip=trip_instance).exists():
            return Response({"message": "Parcel already assigned to this agent"}, status=200)

        # Create Customer_Order / assignment
        order = Customer_Order.objects.create(
            parcel=parcel,
            trip =trip_instance,
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


class MyShipmentsViewSet(viewsets.ModelViewSet):

    queryset = Customer_Order.objects.all()
    serializer_class = Customer_OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    

    def get_queryset(self):

        return Customer_Order.objects.filter(user=self.request.user).order_by('-id')

      


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
      
        client.upsert_user({
            "id": str(user_id),
            "name": request.user.get_full_name() or request.user.username,
        })

        client.upsert_user({
            "id": str(vendor_user_id),
            "name": request.user.get_full_name() or request.user.username,
        })

        vendor_user_id = str(UserConnectionLog_instance.trip.user.id)


        # Create token for authenticated user
        token = client.create_token(user_id)

        return Response({
            "user_id": user_id,
            "vendor_user_id": vendor_user_id,
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

        vendor_user_id = str(request.user.id)



        client = StreamChat(api_key=api_key, api_secret=api_secret)
        client.upsert_user({"id": vendor_user_id})  # ensure vendor or customer is in Stream
        token = client.create_token(vendor_user_id)

        return Response({
            "vendor_user_id": vendor_user_id,
            "token": token,
            "api_key": api_key
        })


        
class ShowTripParcels(generics.ListAPIView):
    
    serializer_class = DeliveryRequestSerializer
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        return DeliveryRequest.objects.all()

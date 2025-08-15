from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions
from .models import *
from .serializers import *

class DeliveryRequestViewSet(viewsets.ModelViewSet):
    queryset = DeliveryRequest.objects.all().order_by('-id') 
    serializer_class = DeliveryRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    
    def get_queryset(self):
        return DeliveryRequest.objects.filter(user=self.request.user).order_by('-id') 

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)



from rest_framework.decorators import api_view, permission_classes

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
        ).exclude(
            status="in_transit"
        ).order_by('-departure_datetime')


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
            status__in=['rejected_by_vendor', 'rejected_by_customer', 'assigned', 'cancelled_by_customer']
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

            if Customer_Order.objects.filter(parcel=parcel, trip=trip_instance).exists():
                assigned = True
            else:    
                assigned = False

            return Response({
                "agent": agent_data,
                "connect_id" : instance.id,
                "assigned" : assigned


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
                trip=trip_instance, parcel=parcel
            )
            request_instance.status = "accepted"
            request_instance.save()

        if Customer_Order.objects.filter(parcel=parcel, trip=trip_instance).exists():
            assigned = True
        else:    
            assigned = False

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



from rest_framework.decorators import api_view, permission_classes


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



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_reserve_vendor_request(request):
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
    request_origin = request.data.get("request_origin")
    

    if not parcel_id or not trip_id:
        return Response({"error": "parcel_id and trip_id are required"}, status=400)

    try:
        parcel = DeliveryRequest.objects.get(id=parcel_id, user=user)
        trip_instance = trip.objects.get(id=trip_id)
        
        parcel.is_agent_assigned = True
        parcel.save()

        try:
            connection = UserConnectionLog.objects.get(user=user, parcel=parcel, trip=trip_instance)
        except UserConnectionLog.DoesNotExist:
            return Response({"error": "You are not connected with this agent for this parcel"}, status=403)


        # Check if already assigned to prevent duplicates or logic for update
        
        if request_origin == "customer":
            print('----------1----------')

            request_instance = Request_Vendor_for_Delivery.objects.get(
                user=request.user, trip=trip_instance, parcel=parcel
            )
            request_instance.status = "assigned"
            request_instance.save()

        elif request_origin == "vendor":

            print('----------2----------')

            request_instance = Request_Customer_for_Delivery.objects.get(
                trip=trip_instance, parcel=parcel
            )
            request_instance.status = "assigned"
            request_instance.save()


        # Create Customer_Order / assignment
        order = Customer_Order.objects.create(
            parcel=parcel,
            trip =trip_instance,
            user=user,
            status='assigned',
            connection_id = connection.id,
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
        return DeliveryRequest.objects.filter(user = self.request.user, is_agent_assigned=False).order_by('-id') 



from rest_framework import viewsets, permissions
from .models import DeliveryRating


class DeliveryRatingViewSet(viewsets.ModelViewSet):
    queryset = DeliveryRating.objects.all()
    serializer_class = DeliveryRatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        vendor_id = self.request.query_params.get('vendor_id')
        if vendor_id:
            return DeliveryRating.objects.filter(vendor_id=vendor_id)
        return DeliveryRating.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'], url_path='by-vendor/(?P<vendor_id>[^/.]+)')
    def by_vendor(self, request, vendor_id):
        try:
            rating = DeliveryRating.objects.get(user=request.user, vendor_id=vendor_id)
            serializer = self.get_serializer(rating)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except DeliveryRating.DoesNotExist:
            return Response({"detail": "Rating not found."}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_shipment_delivery(request):

    shipment_id = request.data.get("shipment_id")

    try:

        instance = Customer_Order.objects.get(id = shipment_id)

        if instance.status == "delivered":
            instance.status = "delivered_by_customer"
            instance.save()

            return Response({"message": "Shipment Marked as Devlivered"}, status=status.HTTP_200_OK)
        
        else:

            return Response({"message": "Shipment not Marked as Devlivered by Vendor yet"}, status=status.HTTP_200_OK)

        

    except Customer_Order.DoesNotExist:
        
        return Response({"detail": "Shipment not found."}, status=status.HTTP_404_NOT_FOUND)




from rest_framework import viewsets, permissions


class SupportTicketViewSet(viewsets.ModelViewSet):
    serializer_class = SupportTicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SupportTicket.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)





class TicketMessageViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        ticket_id = request.query_params.get('ticket_id')
        if not ticket_id:
            return Response({'error': 'ticket_id is required'}, status=400)

        messages = TicketMessage.objects.filter(ticket__id=ticket_id).order_by('created_at')
        serializer = TicketMessageSerializer(messages, many=True, context={'request': request})
        return Response(serializer.data)

    def create(self, request):
        ticket_id = request.data.get('ticket')
        message = request.data.get('message')

        if not ticket_id or not message:
            return Response({'error': 'ticket and message are required'}, status=400)

        ticket = get_object_or_404(SupportTicket, id=ticket_id)

        new_message = TicketMessage.objects.create(
            ticket=ticket,
            sender=request.user,
            message=message
        )

        serializer = TicketMessageSerializer(new_message, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


import requests
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.conf import settings
from django.contrib import messages


class FetchDigilockerDocumentsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        client_id = request.GET.get('client_id')
        
        user = request.user

        try:
            kyc, _ = UserKYC.objects.get_or_create(user=user)

            
            if not client_id:
                return Response({"error": "DigiLocker Client ID not found for this user."}, status=status.HTTP_400_BAD_REQUEST)

            url = f"https://kyc-api.surepass.app/api/v1/digilocker/list-documents/{client_id}"
            headers = {
                "Authorization": f"Bearer {settings.SUREPASS_TOKEN}",
                "Content-Type": "application/json"
            }

            response = requests.get(url, headers=headers)
            data = response.json()

            if not data.get("success"):
                return Response({"error": f"Surepass Error: {data.get('message', 'Unknown error')}"}, status=status.HTTP_400_BAD_REQUEST)

            documents = data["data"].get("documents", [])

            # Reset statuses
            kyc.aadhaar_status = 'pending'
            kyc.pan_status = 'pending'
            kyc.dl_status = 'pending'

            aadhaar_verified = False
            pan_verified = False
            dl_verified = False

            for doc in documents:
                doc_type = doc.get("doc_type")
                downloaded = doc.get("downloaded", False)

                if doc_type == "ADHAR" and downloaded:
                    kyc.aadhaar_status = "verified"
                    aadhaar_verified = True
                elif doc_type == "PANCR" and downloaded:
                    kyc.pan_status = "verified"
                    pan_verified = True
                elif doc_type == "DL" and downloaded:
                    kyc.dl_status = "verified"
                    dl_verified = True

            kyc.save()
            kyc.check_and_update_approval()

            # Step 2: If Aadhaar verified, fetch detailed Aadhaar info
            user_name_updated = False
            if aadhaar_verified:
                aadhaar_url = f"https://kyc-api.surepass.app/api/v1/digilocker/download-aadhaar/{client_id}"
                aadhaar_resp = requests.get(aadhaar_url, headers=headers)
                aadhaar_data = aadhaar_resp.json()
                print(aadhaar_data)

                if aadhaar_data.get("success") and "data" in aadhaar_data:
                    data_block = aadhaar_data["data"]
                    aadhaar_info = data_block.get("aadhaar_xml_data", {})

                    # Convert and save image
                    profile_image_file = save_base64_image(aadhaar_info.get("profile_image"))

                    AadhaarDetails.objects.update_or_create(
                        user=user,
                        client_id=data_block.get("client_id"),
                        defaults={
                            "name": data_block.get("digilocker_metadata", {}).get("name"),
                            "gender": data_block.get("digilocker_metadata", {}).get("gender"),
                            "dob": data_block.get("digilocker_metadata", {}).get("dob"),
                            "yob": aadhaar_info.get("yob"),
                            "zip_code": aadhaar_info.get("zip"),
                            "profile_image": profile_image_file,  # Now it's an ImageField
                            "masked_aadhaar": aadhaar_info.get("masked_aadhaar"),
                            "full_address": aadhaar_info.get("full_address"),
                            "father_name": aadhaar_info.get("father_name"),
                            "address_json": aadhaar_info.get("address"),
                            "xml_url": data_block.get("xml_url"),
                        }
                    )

                    # Update user name
                    full_name = data_block.get("digilocker_metadata", {}).get("name")
                    if full_name:
                        user.name = full_name
                        user.save()

                        # Update logged in user name
                        user.name = full_name
                        user.save()
                        user_name_updated = True

                        # Example: Call your own API to block user or other action here
                        # For example:
                        # block_user_api(user.id)

            return Response({
                "message": "Documents fetched and statuses updated successfully.",
                "aadhaar_verified": aadhaar_verified,
                "pan_verified": pan_verified,
                "aadhaar_data": aadhaar_data,
                "dl_verified": dl_verified,
                "user_name_updated": user_name_updated,
            })

        except Exception as e:
            print("Surepass KYC fetch error:", e)
            return Response({
                "error": "Something went wrong while fetching documents.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

           


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

# @csrf_exempt
# @api_view(['POST'])
# def surepass_webhook(request):
#     payload = request.data
#     client_id = payload.get("client_id")
#     status = payload.get("status")
#     data = payload.get("data", {})

#     if not client_id:
#         return Response({"error": "Missing client_id"}, status=400)

#     try:
#         kyc = UserKYC.objects.get(
#             models.Q(aadhaar_client_id=client_id) |
#             models.Q(pan_client_id=client_id) |
#             models.Q(dl_client_id=client_id)
#         )
#     except UserKYC.DoesNotExist:
#         return Response({"error": "KYC record not found"}, status=404)

#     # Identify the document type
#     if client_id == kyc.aadhaar_client_id:
#         if status == "completed" and data.get("aadhaar_linked", False):
#             kyc.aadhaar_status = "verified"
#         else:
#             kyc.aadhaar_status = "failed"

#     elif client_id == kyc.pan_client_id:
#         if status == "completed" and data.get("verified", False):
#             kyc.pan_status = "verified"
#         else:
#             kyc.pan_status = "failed"

#     elif client_id == kyc.dl_client_id:
#         if status == "completed" and data.get("verified", False):
#             kyc.dl_status = "verified"
#         else:
#             kyc.dl_status = "failed"

#     # Check if all verified
#     if (
#         kyc.aadhaar_status == "verified"
#         and kyc.pan_status == "verified"
#         and kyc.dl_status == "verified"
#     ):
#         kyc.approved = True

#     kyc.save()
#     return Response({"message": "Webhook processed successfully"})



import razorpay
import json
from django.conf import settings
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import PaymentLog

# -----------------------------
# Credit packages
# -----------------------------
CREDIT_PACKAGES = {
    "basic": {"amount": 9900, "credits": 3},    # amount in paise
    "premium": {"amount": 29900, "credits": 10},
}

# -----------------------------
# Razorpay client
# -----------------------------
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


# -----------------------------
# Create Razorpay Order
# -----------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    package_key = request.data.get("package_key")
    package = CREDIT_PACKAGES.get(package_key)
    if not package:
        return Response({"error": "Invalid package"}, status=400)

    order_data = {
        "amount": package["amount"],
        "currency": "INR",
        "receipt": f"user_{request.user.id}_package_{package_key}",
        "payment_capture": 1
    }

    order = client.order.create(order_data)

    PaymentLog.objects.create(
        user=request.user,
        order_id=order["id"],
        package_key=package_key,
        amount=package["amount"],
        status="created",
        credits_added=False,
        raw_data=order
    )

    return Response({
        "order_id": order["id"],
        "amount": package["amount"],
        "currency": "INR",
        "package_key": package_key
    })


# -----------------------------
# Razorpay Webhook
# -----------------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def razorpay_webhook(request):

    import logging
    logger = logging.getLogger(__name__)

    # Print the webhook secret to see if it's loaded
    logger.info(f"RAZORPAY_WEBHOOK_SECRET: {settings.RAZORPAY_WEBHOOK_SECRET!r}")

    # Also safe check before using
    if not settings.RAZORPAY_WEBHOOK_SECRET:
        logger.error("Webhook secret is missing! Check your .env and settings.py")
        return Response({"error": "Webhook secret not configured"}, status=500)



    webhook_body = request.body
    received_sig = request.headers.get("X-Razorpay-Signature")

    # ✅ Verify signature using Razorpay utility
    try:
        client.utility.verify_webhook_signature(webhook_body, received_sig, settings.RAZORPAY_WEBHOOK_SECRET)
    except razorpay.errors.SignatureVerificationError:
        return Response({"error": "Invalid signature"}, status=400)

    event = json.loads(webhook_body)
    payment_entity = event.get("payload", {}).get("payment", {}).get("entity", {})
    order_id = payment_entity.get("order_id")
    amount = payment_entity.get("amount")  # in paise
    receipt = payment_entity.get("notes", {}).get("receipt", "")

    # ✅ Parse receipt for user and package
    user = None
    package_key = None
    if receipt.startswith("user_"):
        parts = receipt.split("_")
        try:
            user_id = int(parts[1])
            package_key = parts[3] if len(parts) >= 4 else None
            user_credit_instance = UserCredit.objects.get(user__id=user_id)
            user = user_credit_instance.user
        except (IndexError, ValueError, UserCredit.DoesNotExist):
            user_credit_instance = None
            user = None

    # ✅ Find or create PaymentLog
    log, created = PaymentLog.objects.get_or_create(
        order_id=order_id,
        defaults={
            "user": user,
            "package_key": package_key or "",
            "amount": amount or 0,
            "status": "pending",
            "credits_added": False,
            "raw_data": event
        }
    )

    # Update log
    log.raw_data = event
    log.payment_id = payment_entity.get("id")
    log.signature = received_sig

    status_map = {
        "captured": "captured",
        "failed": "failed",
        "authorized": "pending",
        "created": "pending",
    }
    log.status = status_map.get(payment_entity.get("status"), "pending")

    # ✅ Add credits atomically
    if log.status == "captured" and user and package_key and not log.credits_added:
        package = CREDIT_PACKAGES.get(package_key)
        if package and amount == package["amount"]:
            with transaction.atomic():
                user_credit_instance = UserCredit.objects.get(user=user)
                user_credit_instance.credits += package["credits"]
                user_credit_instance.save()
                log.credits_added = True

    log.save()
    return Response({"status": "ok"})

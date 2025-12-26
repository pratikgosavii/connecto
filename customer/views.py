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
from users.models import UserCredit
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
        api_key = settings.STREAM_API_KEY
        api_secret = settings.STREAM_API_SECRET

        print("✅ STREAM_API_KEY from .env:", settings.STREAM_API_KEY)

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
        api_key = settings.STREAM_API_KEY
        api_secret = settings.STREAM_API_SECRET


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


import base64
import uuid
from django.core.files.base import ContentFile


def save_base64_image(base64_string):
    """
    Convert base64 string to a Django ContentFile so it can be saved into an ImageField.
    Returns None if input is invalid.
    """
    if not base64_string:
        return None

    try:
        # Remove header like 'data:image/png;base64,...'
        if "base64," in base64_string:
            base64_string = base64_string.split("base64,")[1]

        decoded_img = base64.b64decode(base64_string)
        file_name = f"{uuid.uuid4().hex}.png"  # generate random file name
        return ContentFile(decoded_img, name=file_name)

    except Exception as e:
        print("Error decoding base64 image:", e)
        return None


from PIL import Image, ImageDraw, ImageFont
import io

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from django.core.files.base import ContentFile


from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from django.core.files.base import ContentFile
import base64


def generate_aadhaar_card_image(data, profile_image_b64=None):
    """
    Generate Aadhaar card-like image with provided data and optional base64 profile image.
    Saves a demo PNG locally for verification and also returns a ContentFile for DB.
    """
    from PIL import Image, ImageDraw, ImageFont
    import base64, os
    from io import BytesIO
    from django.core.files.base import ContentFile

    # Card size
    img = Image.new("RGB", (800, 500), color="white")
    draw = ImageDraw.Draw(img)

    # Fonts
    try:
        font = ImageFont.truetype("arial.ttf", 20)
        bold_font = ImageFont.truetype("arialbd.ttf", 28)
    except:
        font = ImageFont.load_default()
        bold_font = ImageFont.load_default()

    # Top Tricolor Strip
    draw.rectangle([0, 0, 800, 40], fill=(255, 153, 51))  # Orange
    draw.rectangle([0, 40, 800, 80], fill=(255, 255, 255))  # White
    draw.rectangle([0, 80, 800, 120], fill=(19, 136, 8))   # Green
    draw.text((250, 45), "Government of India", fill="black", font=bold_font)

    # Aadhaar Number
    draw.text((280, 130), f"{data.get('masked_aadhaar', '')}", fill="black", font=bold_font)

    # Insert Profile Photo
    if profile_image_b64:
        try:
            # Handle "data:image/..." prefix if present
            if profile_image_b64.startswith("data:image"):
                profile_image_b64 = profile_image_b64.split(",")[1]

            profile_data = base64.b64decode(profile_image_b64)
            profile_img = Image.open(BytesIO(profile_data)).resize((150, 180))

            # Ensure same mode
            if profile_img.mode != "RGB":
                profile_img = profile_img.convert("RGB")

            img.paste(profile_img, (50, 180))
        except Exception as e:
            print("Profile photo error:", e)

    # Personal Details
    x_offset = 250
    y_offset = 180
    line_gap = 40

    draw.text((x_offset, y_offset), f"Name: {data.get('name','')}", fill="black", font=font)
    draw.text((x_offset, y_offset + line_gap), f"Father's Name: {data.get('father_name','')}", fill="black", font=font)
    draw.text((x_offset, y_offset + 2*line_gap), f"DOB: {data.get('dob','')}", fill="black", font=font)
    draw.text((x_offset, y_offset + 3*line_gap), f"Gender: {data.get('gender','')}", fill="black", font=font)
    draw.text((x_offset, y_offset + 4*line_gap), f"Address: {data.get('full_address','')}", fill="black", font=font)
    draw.text((x_offset, y_offset + 5*line_gap), f"Pincode: {data.get('zip_code','')}", fill="black", font=font)

    # Footer
    draw.text((250, 460), "Demo - Aadhaar", fill="red", font=bold_font)

    # Save to buffer
    buffer = BytesIO()
    img.save(buffer, format="PNG")

    # 🔹 Save demo image locally for testing
    demo_path = os.path.join("/tmp", "aadhaar_demo.png")  # change path if needed
    img.save(demo_path, format="PNG")
    print(f"Aadhaar card demo saved at: {demo_path}")

    return ContentFile(buffer.getvalue(), "aadhaar_card.png")





class FetchDigilockerDocumentsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        client_id = request.GET.get('client_id')
        refresh = request.GET.get('refresh', 'false').lower() == 'true'  # Force refresh from API
        
        user = request.user

        try:
            kyc, _ = UserKYC.objects.get_or_create(user=user)

            # Check if documents already exist in DB and are verified
            if not refresh:
                has_aadhaar = kyc.aadhaar_status == 'verified' and kyc.adhar_image_file
                has_pan = kyc.pan_status == 'verified' and kyc.pan_file
                has_dl = kyc.dl_status == 'verified' and kyc.dl_file
                
                # If all documents are already verified and exist, return from DB
                if has_aadhaar or has_pan or has_dl:
                    aadhaar_data = {}
                    try:
                        aadhaar_details = AadhaarDetails.objects.filter(user=user).first()
                        if aadhaar_details:
                            aadhaar_data = {
                                "name": aadhaar_details.name,
                                "gender": aadhaar_details.gender,
                                "dob": str(aadhaar_details.dob) if aadhaar_details.dob else None,
                                "yob": aadhaar_details.yob,
                                "zip_code": aadhaar_details.zip_code,
                                "masked_aadhaar": aadhaar_details.masked_aadhaar,
                                "full_address": aadhaar_details.full_address,
                                "father_name": aadhaar_details.father_name,
                            }
                    except Exception:
                        pass
                    
                    return Response({
                        "message": "Documents fetched from database.",
                        "source": "database",
                        "aadhaar_verified": has_aadhaar,
                        "dl_verified": has_dl,
                        "pan_verified": has_pan,
                        "aadhaar_data": aadhaar_data,
                        "aadhaar_status": kyc.aadhaar_status,
                        "pan_status": kyc.pan_status,
                        "dl_status": kyc.dl_status,
                        "is_approved": kyc.is_approved,
                    }, status=status.HTTP_200_OK)
            
            # If refresh is requested or documents don't exist, fetch from DigiLocker API
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
            print(documents)
            # Reset statuses
            kyc.aadhaar_status = 'pending'
            kyc.pan_status = 'pending'
            kyc.dl_status = 'pending'

            aadhaar_verified = False
            pan_verified = False
            dl_verified = False

            user_name_updated = False
            aadhaar_data = {}

            # Loop over all docs
            for doc in documents:
                doc_type = doc.get("doc_type")
                file_id = doc.get("file_id")
                downloaded = doc.get("downloaded", False)


                print(doc_type, 'file id-----------------------', file_id)

                # Aadhaar (special API)
                if doc_type == "ADHAR" and downloaded:
                    kyc.aadhaar_status = "verified"
                    aadhaar_verified = True

                    aadhaar_url = f"https://kyc-api.surepass.app/api/v1/digilocker/download-aadhaar/{client_id}"
                    aadhaar_resp = requests.get(aadhaar_url, headers=headers)
                    aadhaar_data = aadhaar_resp.json()
                    print(aadhaar_data)

                    if aadhaar_data.get("success") and "data" in aadhaar_data:
                        print('--------------------11111111111111111----------------')

                        data_block = aadhaar_data["data"]
                        aadhaar_info = data_block.get("aadhaar_xml_data", {})

                        # Convert and save image
                        profile_image_file = save_base64_image(aadhaar_info.get("profile_image"))
                        kyc.aadhaar_status = 'verified'
                
                        AadhaarDetails.objects.update_or_create(
                            user=user,
                            client_id=data_block.get("client_id"),
                            defaults={
                                "name": data_block.get("digilocker_metadata", {}).get("name"),
                                "gender": data_block.get("digilocker_metadata", {}).get("gender"),
                                "dob": data_block.get("digilocker_metadata", {}).get("dob"),
                                "yob": aadhaar_info.get("yob"),
                                "zip_code": aadhaar_info.get("zip"),
                                "profile_image": profile_image_file,
                                "masked_aadhaar": aadhaar_info.get("masked_aadhaar"),
                                "full_address": aadhaar_info.get("full_address"),
                                "father_name": aadhaar_info.get("father_name"),
                                "address_json": aadhaar_info.get("address"),
                                "xml_url": data_block.get("xml_url"),
                            }
                        )


                        aadhaar_card_file = generate_aadhaar_card_image({
                            "name": data_block.get("digilocker_metadata", {}).get("name"),
                            "gender": data_block.get("digilocker_metadata", {}).get("gender"),
                            "dob": data_block.get("digilocker_metadata", {}).get("dob"),
                            "yob": aadhaar_info.get("yob"),
                            "zip_code": aadhaar_info.get("zip"),
                            "masked_aadhaar": aadhaar_info.get("masked_aadhaar"),
                            "full_address": aadhaar_info.get("full_address"),
                            "father_name": aadhaar_info.get("father_name"),
                        }, profile_image_b64=aadhaar_info.get("profile_image"))


                        # Save Aadhaar card image in FileField
                        print('saving fileeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee')
                        kyc.adhar_image_file.save(f"{user.id}_aadhaar.png", aadhaar_card_file)
                        kyc.save()
                     

                        # Update user name
                        full_name = data_block.get("digilocker_metadata", {}).get("name")
                        if full_name:
                            user.name = full_name
                            user.save()
                            user_name_updated = True

                # PAN (download by file_id)
                if doc_type == "PANCR" and downloaded:
                    print('--------------------1--1--1--1-1-1-1-1--1----------------')

                    pan_url = f"https://kyc-api.surepass.app/api/v1/digilocker/download-document/{client_id}/{file_id}"
                    resp = requests.get(pan_url, headers=headers)
                    print('pan url:----------', pan_url)
                    print("PAN Response status:", resp.status_code)


                    if resp.status_code == 200 and resp.json().get("success"):
                        download_url = resp.json()["data"]["download_url"]

                        # Now fetch actual PDF
                        pdf_resp = requests.get(download_url)
                        if pdf_resp.status_code == 200:
                            kyc.pan_file.save(f"{user.id}_pan.pdf", ContentFile(pdf_resp.content), save=False)
                            kyc.pan_status = "verified"
                            pan_verified = True
                            print("✅ PAN file saved successfully")
                        else:
                            print("❌ Failed to download PAN PDF:", pdf_resp.text)
                    else:
                        print("PAN download failed:", resp.text)

                # Driving License (download by file_id)
                if doc_type == "DRVLC" and downloaded:
                    print('--------------------2222222222222222----------------')

                    dl_url = f"https://kyc-api.surepass.app/api/v1/digilocker/downloaddocument/{client_id}/{file_id}"
                    print('dr url:----------', dl_url)
                    resp = requests.get(dl_url, headers=headers)
                    print(resp)
                    if resp.status_code == 200:
                        kyc.dl_file.save(f"{user.id}_dl.pdf", ContentFile(resp.content), save=False)
                        kyc.dl_status = "verified"
                        dl_verified = True

            # Save KYC after processing all docs
            kyc.save()
            kyc.check_and_update_approval()

            return Response({
                "message": "Documents fetched and statuses updated successfully.",
                "source": "digilocker_api",
                "aadhaar_verified": aadhaar_verified,
                "dl_verified": dl_verified,
                "pan_verified": pan_verified,
                "aadhaar_data": aadhaar_data,
                "user_name_updated": user_name_updated,
                "aadhaar_status": kyc.aadhaar_status,
                "pan_status": kyc.pan_status,
                "dl_status": kyc.dl_status,
                "is_approved": kyc.is_approved,
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
    "premium": {"amount": 24900, "credits": 10},
}

# -----------------------------
# Razorpay client
# -----------------------------
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


# -----------------------------
# Razorpay Webhook
# -----------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    package_key = request.data.get("package_key")
    package = CREDIT_PACKAGES.get(package_key)
    if not package:
        return Response({"error": "Invalid package"}, status=400)

    receipt_val = f"user_{request.user.id}_package_{package_key}"

    order_data = {
        "amount": package["amount"],
        "currency": "INR",
        "receipt": receipt_val,
        "notes": {"receipt": receipt_val},   # <-- REQUIRED
        "payment_capture": 1
    }

    print('--------------------------order_data')
    print(order_data)

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

import logging


logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def razorpay_webhook(request):
    webhook_body = request.body.decode("utf-8")

    print("---------------webhook_body----------------------")
    received_sig = request.headers.get("X-Razorpay-Signature")
    if not received_sig:
        logger.warning("Missing X-Razorpay-Signature")
        return Response({"error": "Missing signature"}, status=400)
    print(webhook_body)
    print("webhook_body")


    # Verify that the webhook secret is configured
    if not settings.RAZORPAY_WEBHOOK_SECRET:
        logger.error("Webhook secret is missing! Check your .env and settings.py")
        return Response({"error": "Webhook secret not configured"}, status=500)

    # Verify signature using Razorpay utility
    try:
        client.utility.verify_webhook_signature(webhook_body, received_sig, settings.RAZORPAY_WEBHOOK_SECRET)
    except razorpay.errors.SignatureVerificationError:
        logger.warning("Invalid webhook signature received")
        return Response({"error": "Invalid signature"}, status=400)

    event = json.loads(webhook_body)
    payment_entity = event.get("payload", {}).get("payment", {}).get("entity", {})

    order_id = payment_entity.get("order_id")
    if not order_id:
        logger.warning("Webhook missing order_id; event ignored")
        return Response({"status": "ignored"}, status=200)
    amount = payment_entity.get("amount")  # in paise
    # Extract receipt safely
    notes = payment_entity.get("notes", {})
    receipt = notes.get("receipt") if isinstance(notes, dict) else None

    if not receipt:
        receipt = event.get("payload", {}).get("order", {}).get("entity", {}).get("receipt", "")

    print("Receipt received:", receipt)

    # Parse receipt for user and package
    user = None
    package_key = None
    user_credit_instance = None
    print('reciept : ---------------------', receipt)
    if receipt.startswith("user_"):
        print('-------------------------2------------------------------')

        parts = receipt.split("_")
        try:
            user_id = int(parts[1])
            package_key = parts[3] if len(parts) >= 4 else None
            user_credit_instance = UserCredit.objects.get(user__id=user_id)
            user = user_credit_instance.user
            print('-------------------------3------------------------------')

        except (IndexError, ValueError, UserCredit.DoesNotExist):
            print('-------------------------4------------------------------')
            logger.warning(f"Failed to parse receipt: {receipt}")


    # Find or create PaymentLog
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
    print('-------------------------5------------------------------')

    # Update log
    log.raw_data = event
    log.payment_id = payment_entity.get("id")
    log.signature = received_sig

    # Map Razorpay payment status
    status_map = {
        "captured": "captured",
        "failed": "failed",
        "authorized": "pending",
        "created": "pending",
    }
    log.status = status_map.get(payment_entity.get("status"), "pending")
    print('-------------------------6------------------------------')
    print(log)
    print(log.status)
    # Add credits atomically only once
    if log.status == "captured" and user_credit_instance and package_key and not log.credits_added:

        print('-------------------------7------------------------------')
        package = CREDIT_PACKAGES.get(package_key)
        if package and amount == package["amount"]:
            try:
                print('-------------------------8------------------------------')

                with transaction.atomic():
                    print('-------------------------9-----------------------------')

                    user_credit_instance.credits += package["credits"]
                    user_credit_instance.save()
                    log.credits_added = True
                    logger.info(f"Added {package['credits']} credits to user {user.id}")
            except Exception as e:
                print('-------------------------10------------------------------')

                logger.error(f"Failed to add credits: {e}")
    print('-------------------------11------------------------------')

    log.save()
    return Response({"status": "ok"})




class GetVendorLocationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Customer fetches vendor live location while order is active (before completion)."""
        order_id = request.query_params.get('order_id')
        if not order_id:
            return Response({"error": "order_id is required"}, status=400)

        try:
            order = Customer_Order.objects.get(id=order_id, user=request.user)
        except Customer_Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

        if order.status in ['delivered', 'delivered_by_customer', 'cancelled_by_vendor', 'cancelled_by_customer']:
            return Response({"error": "Location sharing ended"}, status=400)

        from .models import VendorLiveLocation
        try:
            live = VendorLiveLocation.objects.get(order=order)
        except VendorLiveLocation.DoesNotExist:
            return Response({"latitude": None, "longitude": None, "updated_at": None, "status": order.status}, status=200)

        return Response({
            "latitude": live.latitude,
            "longitude": live.longitude,
            "updated_at": live.updated_at,
            "status": order.status,
        }, status=200)
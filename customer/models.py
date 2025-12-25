from django.db import models
from django.contrib.auth import get_user_model

from django.db.models import Max

from vendor.models import *



class RequestType(models.Model):
    name = models.CharField(max_length=50)
    # other fields ...


class DeliveryRequest(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)

    # Parcel Details
    parcel_title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    parcel_type = models.CharField(max_length=255)
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    length = models.DecimalField(max_digits=10, decimal_places=2)
    width = models.DecimalField(max_digits=10, decimal_places=2)
    height = models.DecimalField(max_digits=10, decimal_places=2)
    item_price_worth = models.DecimalField(max_digits=10, decimal_places=2)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_date = models.DateField()

    # Pickup Location
  
    pickup_contact = models.CharField(max_length=20, blank=True, null=True)

    # Google Maps pickup metadata
    pickup_latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    pickup_longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    pickup_place_id = models.CharField(max_length=255, blank=True, null=True)
    pickup_formatted_address = models.TextField(blank=True, null=True)
    pickup_city_name = models.CharField(max_length=100, blank=True, null=True)

    request_type = models.ManyToManyField(RequestType)

    # Destination
   
    destination_contact = models.CharField(max_length=20, blank=True, null=True)

    # Google Maps destination metadata
    destination_latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    destination_longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    destination_place_id = models.CharField(max_length=255, blank=True, null=True)
    destination_formatted_address = models.TextField(blank=True, null=True)
    destination_city_name = models.CharField(max_length=100, blank=True, null=True)

    is_agent_assigned = models.BooleanField(default=False)

    fragile = models.BooleanField(default=False)
    legal_confirmation = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

     # Home Pickup Location
    home_pickup_address_line1 = models.CharField(max_length=255)
    home_pickup_address_line2 = models.CharField(max_length=255, blank=True, null=True)
    home_pickup_pincode = models.CharField(max_length=10, blank=True, null=True)
    home_pickup_state = models.CharField(max_length=100, blank=True, null=True)
    home_pickup_contact = models.CharField(max_length=20, blank=True, null=True)
    
    # Home Drop Pickup Location
    home_drop_pickup_address_line1 = models.CharField(max_length=255)
    home_drop_pickup_address_line2 = models.CharField(max_length=255, blank=True, null=True)
    home_drop_pickup_pincode = models.CharField(max_length=10, blank=True, null=True)
    home_drop_pickup_state = models.CharField(max_length=100, blank=True, null=True)
    home_drop_pickup_contact = models.CharField(max_length=20, blank=True, null=True)
    
    
class Request_Vendor_for_Delivery(models.Model):
    
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    parcel = models.ForeignKey("customer.DeliveryRequest", on_delete=models.CASCADE)
    trip = models.ForeignKey("vendor.trip", on_delete=models.CASCADE)
    requested_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    status = models.CharField(max_length=30, choices=[
        ('pending', 'Pending'),
        ('accepted_by_vendor', 'Vendor Accepted'),
        ('accepted', 'Accepted'),
        ('assigned', 'Assigned'),
        ("rejected_by_vendor", "Rejected By Vendor"),
        ("rejected_by_customer", "Rejected By Customer"),
        ('cancelled_by_customer', 'Cancelled'),
    ], default='pending')


    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.parcel} -> {self.trip} ({self.status})"
    
    class Meta:
        unique_together = ('user', 'parcel', 'trip')


    

class UserConnectionLog(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    parcel = models.ForeignKey("customer.DeliveryRequest", on_delete=models.CASCADE)
    trip = models.ForeignKey("vendor.trip", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'parcel', 'trip')



import random


class Customer_Order(models.Model):

    
    tracking_id = models.CharField(max_length=100, unique=True)
   
    otp = models.CharField(max_length=6, blank=True, null=True)  # New OTP f
    
    parcel = models.ForeignKey("customer.DeliveryRequest", on_delete=models.CASCADE)
    trip = models.ForeignKey("vendor.trip", on_delete=models.CASCADE)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="orders_user")

    STATUS_CHOICES = [
        ("assigned", "Assigned"),
        ("in_transit", "In Transit"),
        ("delivered", "Delivered"),
        ("delivered_by_customer", "Delivered By Customer"),
        ("cancelled_by_vendor", "Cancelled By Vendor"),
        ("cancelled_by_customer", "Cancelled By Customer"),
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="assigned")
    connection_id = models.IntegerField(blank=True, null=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def save(self, *args, **kwargs):
        if not self.tracking_id:
            last_id = Customer_Order.objects.aggregate(Max('id'))['id__max'] or 0
            self.tracking_id = f"TRK{last_id + 1:05d}"  # Example: TRK00001

        if not self.otp:
            self.otp = f"{random.randint(100000, 999999)}"  # Generate 6-digit random OTP

        super().save(*args, **kwargs)

 
    def __str__(self):
        return f"Order {self.tracking_id} - Parcel #{self.parcel.id}"



class VendorLiveLocation(models.Model):
    order = models.OneToOneField(Customer_Order, on_delete=models.CASCADE, related_name='live_location')
    vendor = models.ForeignKey('users.User', on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"LiveLocation for Order {self.order_id}"

        

class DeliveryRating(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='user')
    vendor = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='vendor_agent')
    shipment = models.ForeignKey('customer.customer_order', on_delete=models.CASCADE, related_name='sdsdsd')
    
    rating = models.PositiveSmallIntegerField(choices=[(i, f"{i} Star{'s' if i > 1 else ''}") for i in range(1, 6)])
    feedback = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('vendor', 'user', 'shipment')  # prevents duplicate ratings from same user
        ordering = ['-created_at']

    def __str__(self):
        return f"Rating {self.rating} by {self.user} for {self.vendor}"





class SupportTicket(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    shipment = models.ForeignKey(Customer_Order, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class TicketMessage(models.Model):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey('users.User', on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)



from django.db import models
from django.conf import settings

class PaymentLog(models.Model):
    STATUS_CHOICES = [
        ('created', 'Created'),
        ('captured', 'Captured'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=100, unique=True)
    payment_id = models.CharField(max_length=100, null=True, blank=True)
    signature = models.TextField(null=True, blank=True)
    package_key = models.CharField(max_length=50)
    amount = models.PositiveIntegerField()  # in paise
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')
    credits_added = models.BooleanField(default=False)  # prevent double credit
    raw_data = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.order_id} - {self.status}"


# models.py
class AadhaarDetails(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="aadhaar_details")
    client_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    yob = models.CharField(max_length=4, blank=True, null=True)
    zip_code = models.CharField(max_length=10, blank=True, null=True)
    profile_image = models.ImageField(upload_to="aadhaar_photos/", blank=True, null=True)  # Changed here
    masked_aadhaar = models.CharField(max_length=20, blank=True, null=True)
    full_address = models.TextField(blank=True, null=True)
    father_name = models.CharField(max_length=255, blank=True, null=True)
    address_json = models.JSONField(blank=True, null=True)
    xml_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Aadhaar of {self.user}"



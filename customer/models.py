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
    pickup_address_line1 = models.CharField(max_length=255, blank=True, null=True)
    pickup_address_line2 = models.CharField(max_length=255, blank=True, null=True)
    pickup_pincode = models.CharField(max_length=10, blank=True, null=True)
    pickup_state = models.CharField(max_length=100, blank=True, null=True)
    pickup_city = models.ForeignKey("masters.city", on_delete=models.CASCADE, related_name="pickup_city", blank=True, null=True)
    pickup_contact = models.CharField(max_length=20, blank=True, null=True)

    request_type = models.ManyToManyField(RequestType)

    # Destination
    destination_address_line1 = models.CharField(max_length=255, blank=True, null=True)
    destination_address_line2 = models.CharField(max_length=255, blank=True, null=True)
    destination_pincode = models.CharField(max_length=10, blank=True, null=True)
    destination_state = models.CharField(max_length=100, blank=True, null=True)
    destination_city = models.ForeignKey("masters.city", on_delete=models.CASCADE, related_name="destination_city", blank=True, null=True)
    destination_contact = models.CharField(max_length=20, blank=True, null=True)

    is_agent_assigned = models.BooleanField(default=False)

    legal_confirmation = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)



class Request_Vendor_for_Delivery(models.Model):
    
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    parcel = models.ForeignKey("customer.DeliveryRequest", on_delete=models.CASCADE)
    trip = models.ForeignKey("vendor.trip", on_delete=models.CASCADE)

    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ], default='pending')


    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.parcel} -> {self.trip} ({self.status})"
    

class UserConnectionLog(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    parcel = models.ForeignKey("customer.DeliveryRequest", on_delete=models.CASCADE)
    trip = models.ForeignKey("vendor.trip", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'parcel', 'trip')




class Customer_Order(models.Model):

    
    tracking_id = models.CharField(max_length=100, unique=True)

    parcel = models.ForeignKey("customer.DeliveryRequest", on_delete=models.CASCADE)
    agent = models.ForeignKey("users.User", on_delete=models.CASCADE)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="orders_user")

    STATUS_CHOICES = [
        ("assigned", "Assigned"),
        ("in_transit", "In Transit"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="assigned")

    assigned_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.tracking_id:
            last_id = Customer_Order.objects.aggregate(Max('id'))['id__max'] or 0
            self.tracking_id = f"TRK{last_id + 1:05d}"  # Example: TRK00001
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.tracking_id} - Parcel #{self.parcel.id}"
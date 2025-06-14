from django.db import models
from django.contrib.auth import get_user_model



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
    pickup_address_line1 = models.CharField(max_length=255)
    pickup_address_line2 = models.CharField(max_length=255, blank=True, null=True)
    pickup_pincode = models.CharField(max_length=10)
    pickup_state = models.CharField(max_length=100)
    pickup_city = models.ForeignKey("masters.city", on_delete=models.CASCADE, related_name="pickup_city")
    pickup_contact = models.CharField(max_length=20)

    # Destination
    destination_address_line1 = models.CharField(max_length=255)
    destination_address_line2 = models.CharField(max_length=255, blank=True, null=True)
    destination_pincode = models.CharField(max_length=10)
    destination_state = models.CharField(max_length=100)
    destination_city = models.ForeignKey("masters.city", on_delete=models.CASCADE, related_name="destination_city")
    destination_contact = models.CharField(max_length=20)

    legal_confirmation = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

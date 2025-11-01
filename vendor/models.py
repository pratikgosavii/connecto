from django.db import models

# Create your models here.



class trip(models.Model):
    
    MODE_OF_TRANSPORT_CHOICES = [
        ('private', 'Private Vehicle'),
        ('public', 'Public Vehicle'),
    ]
    PUBLIC_TRANSPORT_CHOICES = [
        ('train', 'Train'),
        ('taxi', 'Taxi'),
        ('bus', 'Bus'),
    ]
    PRIVATE_VEHICLE_CHOICES = [
        ('car', 'Car'),
        ('private_bus', 'Private Bus'),
    ]

    STATUS_CHOICES = [
        ("new", "new"),
        ("in_transit", "In Transit"),
    ]
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    description = models.TextField()
    # Source (Google Maps)
    source_latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    source_longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    source_place_id = models.CharField(max_length=255, blank=True, null=True)
    source_formatted_address = models.TextField(blank=True, null=True)
    source_city_name = models.CharField(max_length=100, blank=True, null=True)

    # Destination (Google Maps)
    destination_latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    destination_longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    destination_place_id = models.CharField(max_length=255, blank=True, null=True)
    destination_formatted_address = models.TextField(blank=True, null=True)
    destination_city_name = models.CharField(max_length=100, blank=True, null=True)
    mode_of_transport = models.CharField(max_length=20, choices=MODE_OF_TRANSPORT_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, null=True, blank=True)
    private_vehicle_type = models.CharField(max_length=20, choices=PRIVATE_VEHICLE_CHOICES, null=True, blank=True)
    public_vehicle_type = models.CharField(max_length=20, choices=PUBLIC_TRANSPORT_CHOICES, null=True, blank=True)

    # Conditional fields
    car_photo = models.ImageField(upload_to='car_photos/', null=True, blank=True)
    driving_license = models.ImageField(upload_to='licenses/', null=True, blank=True)
    car_number = models.CharField(max_length=50, null=True, blank=True)

    bus_number = models.CharField(max_length=50, null=True, blank=True)
    seat_number = models.CharField(max_length=50, null=True, blank=True)

    train_pnr = models.CharField(max_length=50, null=True, blank=True)

    parcel_capacity = models.IntegerField()
    agreed = models.BooleanField(default=False)

    # Pickup Location
    pickup_address_line1 = models.CharField(max_length=255)
    pickup_address_line2 = models.CharField(max_length=255, blank=True, null=True)
    pickup_pincode = models.CharField(max_length=10, blank=True, null=True)
    pickup_state = models.CharField(max_length=100, blank=True, null=True)
    pickup_city = models.CharField(max_length=100, blank=True, null=True)
    pickup_contact = models.CharField(max_length=20, blank=True, null=True)

    departure_datetime = models.DateTimeField()
    arrival_datetime = models.DateTimeField()


    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.source} to {self.destination}"



class Request_Customer_for_Delivery(models.Model):
    
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    parcel = models.ForeignKey("customer.DeliveryRequest", on_delete=models.CASCADE)
    trip = models.ForeignKey(trip, on_delete=models.CASCADE)
    requested_price = models.DecimalField(max_digits=10, decimal_places=2)



    status = models.CharField(max_length=30, choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('assigned', 'Assigned'),
        ("rejected_by_vendor", "Rejected By Vendor"),
        ("rejected_by_customer", "Rejected By Customer"),
        ('cancelled_by_customer', 'Cancelled'),
    ], default='pending')

   

    created_at = models.DateTimeField(auto_now_add=True)

    
    class Meta:
        unique_together = ('trip', 'parcel', 'user') 
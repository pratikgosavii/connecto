from django.db import models

# Create your models here.



class add_trip(models.Model):
    
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

    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    description = models.TextField()
    source = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    mode_of_transport = models.CharField(max_length=20, choices=MODE_OF_TRANSPORT_CHOICES)
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
    travelling_date = models.DateField()
    agreed = models.BooleanField(default=False)

    # Pickup Location
    pickup_address_line1 = models.CharField(max_length=255)
    pickup_address_line2 = models.CharField(max_length=255, blank=True, null=True)
    pickup_pincode = models.CharField(max_length=10)
    pickup_state = models.CharField(max_length=100)
    pickup_city = models.CharField(max_length=100)
    pickup_contact = models.CharField(max_length=20)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.source} to {self.destination}"





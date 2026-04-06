from django.contrib import admin

# Register your models here.


from .models import *

admin.site.register(trip)
admin.site.register(Request_Customer_for_Delivery)
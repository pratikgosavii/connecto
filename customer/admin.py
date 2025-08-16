from django.contrib import admin

# Register your models here.


from .models import *

admin.site.register(DeliveryRequest)
admin.site.register(Customer_Order)
admin.site.register(UserConnectionLog)
admin.site.register(Request_Vendor_for_Delivery)
admin.site.register(SupportTicket)
admin.site.register(TicketMessage)
admin.site.register(PaymentLog)
admin.site.register(AadhaarDetails)
from django.contrib import admin
from .models import *

# Register your models here.

from .models import *

admin.site.register(coupon)
admin.site.register(occupation_subcategory)
admin.site.register(occupation_category)
admin.site.register(occupation)
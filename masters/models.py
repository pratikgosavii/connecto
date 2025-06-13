

from django.db import models


from users.models import User
from django.utils.timezone import now
from datetime import datetime, timezone

import pytz
ist = pytz.timezone('Asia/Kolkata')



from users.models import User




class coupon(models.Model):

    TYPE_CHOICES = [
        ('percent', 'Percentage'),
        ('amount', 'Amount'),
    ]
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='percent')  # 👈 Add this

    code = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=500, null=True, blank=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    min_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='doctor_images/')
    start_date = models.DateTimeField(default=now)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code


class occupation_category(models.Model):
    name = models.CharField(max_length=225, blank=True, null=True)

    def __str__(self):
        return self.name


class occupation_subcategory(models.Model):
    
    category = models.ForeignKey("masters.occupation_category", on_delete=models.CASCADE)
    name = models.CharField(max_length=225, blank=True, null=True)

    def __str__(self):
        return self.name

class occupation(models.Model):

    category = models.ForeignKey("masters.occupation_category", on_delete=models.CASCADE)
    subcategory = models.ForeignKey("masters.occupation_subcategory", on_delete=models.CASCADE)
    name = models.CharField(max_length=225, blank=True, null=True)


class home_banner(models.Model):
    title = models.CharField(max_length=225, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='homeBanners/')
    is_for_web = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    



class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question
    
    

    
class ScamCategory(models.Model):

    name = models.CharField(max_length=255)

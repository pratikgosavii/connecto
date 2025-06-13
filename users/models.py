from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

# Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, mobile, password=None, **extra_fields):
        """Create and return a regular user with a mobile number and password."""
        if not mobile:
            raise ValueError("The Mobile field must be set")
        user = self.model(mobile=mobile, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, mobile, password=None, **extra_fields):
        """Create and return a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(mobile, password, **extra_fields)


GENDER_CHOICES = [
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'),
]

MARITAL_STATUS_CHOICES = [
    ('single', 'Single'),
    ('married', 'Married'),
    ('divorced', 'Divorced'),
    ('widowed', 'Widowed'),
]


from django.core.validators import RegexValidator, MinLengthValidator, MaxLengthValidator, EmailValidator
from django.utils.translation import gettext_lazy as _

LANGUAGE_CHOICES = [
    ('english', 'English'),
    ('hindi', 'Hindi'),
    ('marathi', 'Marathi'),
    ('gujarati', 'Gujarati'),
    ('telugu', 'Telugu'),
    ('other', 'Other'),
    # Add more languages if needed
]

from masters.models import *

class User(AbstractUser):
    firebase_uid = models.CharField(max_length=128, unique=True, null=True, blank=True)
    mobile = models.CharField(max_length=15, unique=True, db_index=True)

    name = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    email = models.EmailField(null=True, blank=True, validators=[EmailValidator(message="Enter a valid email address.")])

    is_agent = models.BooleanField(default = False)

    username = None
    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = []

    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)

    # New Address Fields
    address_line1 = models.CharField(max_length=255, null=True, blank=True)  # House/Building/Apartment
    address_line2 = models.CharField(max_length=255, null=True, blank=True)  # Street/Area
    pincode = models.CharField(max_length=10, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)

    # Education
    qualification = models.CharField(max_length=255, null=True, blank=True)
    year_of_graduation = models.PositiveIntegerField(null=True, blank=True)

    
    objects = CustomUserManager()

    def __str__(self):
        return self.mobile

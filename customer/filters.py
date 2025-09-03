import django_filters
from .models import *

# class couponFilter(django_filters.FilterSet):
#     class Meta:
#         model = coupon
#         exclude = ['image']  # ⛔ Exclude unsupported field

# class home_bannerFilter(django_filters.FilterSet):
#     class Meta:
#         model = home_banner
#         exclude = ['image']  # ⛔ Exclude unsupported field



# filters.py
import django_filters
from django import forms
from .models import DeliveryRequest
from masters.models import city
from users.models import *

class DeliveryRequestFilter(django_filters.FilterSet):
    
    
    user = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),   # adjust if your User model is custom
        field_name="user",
        label="User",
        widget=forms.Select(attrs={"class": "form-control"})
    )


    parcel_title = django_filters.CharFilter(
        field_name="parcel_title",
        lookup_expr="icontains",
        label="Parcel Title",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Search Parcel"})
    )

    pickup_city = django_filters.ModelChoiceFilter(
        queryset=city.objects.all(),
        field_name="pickup_city",
        label="Pickup City",
        widget=forms.Select(attrs={"class": "form-control"})
    )

    destination_city = django_filters.ModelChoiceFilter(
        queryset=city.objects.all(),
        field_name="destination_city",
        label="Destination City",
        widget=forms.Select(attrs={"class": "form-control"})
    )

    delivery_date_from = django_filters.DateFilter(
        field_name="delivery_date",
        lookup_expr="gte",
        label="Delivery Date From",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )

    delivery_date_to = django_filters.DateFilter(
        field_name="delivery_date",
        lookup_expr="lte",
        label="Delivery Date To",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )

    class Meta:
        model = DeliveryRequest
        fields = [
            "user",
            "parcel_title",
            "pickup_city",
            "destination_city",
            "delivery_date_from",
            "delivery_date_to",
        ]





import django_filters
from django import forms
from .models import Request_Vendor_for_Delivery
from users.models import User
from customer.models import DeliveryRequest
from vendor.models import trip


class RequestVendorDeliveryFilter(django_filters.FilterSet):
    user = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    parcel = django_filters.ModelChoiceFilter(
        queryset=DeliveryRequest.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    trip = django_filters.ModelChoiceFilter(
        queryset=trip.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    status = django_filters.ChoiceFilter(
        choices=Request_Vendor_for_Delivery._meta.get_field("status").choices,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    created_at__gte = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Created After"
    )
    created_at__lte = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Created Before"
    )

    class Meta:
        model = Request_Vendor_for_Delivery
        fields = ["user", "parcel", "trip", "status", "created_at"]



class PaymentLogFilter(django_filters.FilterSet):
    # Filter by User (dropdown)
    user = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        field_name="user",
        label="User",
        widget=forms.Select(attrs={"class": "form-control"})
    )

    # Filter by order ID
    order_id = django_filters.CharFilter(
        field_name="order_id",
        lookup_expr="icontains",
        label="Order ID",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Search Order ID"})
    )

    # Filter by payment ID
    payment_id = django_filters.CharFilter(
        field_name="payment_id",
        lookup_expr="icontains",
        label="Payment ID",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Search Payment ID"})
    )

    # Status dropdown
    status = django_filters.ChoiceFilter(
        choices=PaymentLog.STATUS_CHOICES,
        label="Status",
        widget=forms.Select(attrs={"class": "form-control"})
    )

    # Date range filter (created_at)
    created_from = django_filters.DateTimeFilter(
        field_name="created_at",
        lookup_expr="gte",
        label="Created From",
        widget=forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"})
    )
    created_to = django_filters.DateTimeFilter(
        field_name="created_at",
        lookup_expr="lte",
        label="Created To",
        widget=forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"})
    )

    class Meta:
        model = PaymentLog
        fields = [
            "user",
            "order_id",
            "payment_id",
            "status",
            "created_from",
            "created_to",
        ]
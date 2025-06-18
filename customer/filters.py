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



class DeliveryRequestFilter(django_filters.FilterSet):

    pickup_city = django_filters.CharFilter(field_name='pickup_city', lookup_expr='icontains')
    destination_city = django_filters.CharFilter(field_name='drop_city', lookup_expr='icontains')
    mode_of_transport = django_filters.CharFilter(field_name='mode_of_transport', lookup_expr='exact')
    parcel_capacity = django_filters.NumberFilter(field_name='parcel_capacity', lookup_expr='gte')
    delivery_date = django_filters.DateFilter(field_name='delivery_date', lookup_expr='exact')

    class Meta:
        model = DeliveryRequest
        fields = ['destination_city', 'mode_of_transport', 'parcel_capacity', 'delivery_date']

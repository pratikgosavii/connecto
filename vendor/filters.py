# filters.py
import django_filters
from .models import *

class TripFilter(django_filters.FilterSet):
    source = django_filters.CharFilter(field_name='source', lookup_expr='exact')
    destination = django_filters.CharFilter(field_name='destination', lookup_expr='exact')
    pickup_city = django_filters.CharFilter(field_name='pickup_city', lookup_expr='icontains')
    mode_of_transport = django_filters.CharFilter(field_name='mode_of_transport', lookup_expr='exact')
    parcel_capacity = django_filters.NumberFilter(field_name='parcel_capacity', lookup_expr='gte')
    departure_datetime = django_filters.DateFilter(field_name='departure_datetime', lookup_expr='exact')
    arrival_datetime = django_filters.DateFilter(field_name='arrival_datetime', lookup_expr='exact')

    class Meta:
        model = trip
        fields = ['source', 'destination', 'pickup_city', 'mode_of_transport', 'parcel_capacity', 'departure_datetime', 'arrival_datetime']

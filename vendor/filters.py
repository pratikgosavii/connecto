# filters.py
import django_filters
from .models import add_trip

class AddTripFilter(django_filters.FilterSet):
    source = django_filters.CharFilter(field_name='source', lookup_expr='exact')
    destination = django_filters.CharFilter(field_name='destination', lookup_expr='exact')
    pickup_city = django_filters.CharFilter(field_name='pickup_city', lookup_expr='icontains')
    mode_of_transport = django_filters.CharFilter(field_name='mode_of_transport', lookup_expr='exact')
    parcel_capacity = django_filters.NumberFilter(field_name='parcel_capacity', lookup_expr='gte')
    travelling_date = django_filters.DateFilter(field_name='travelling_date', lookup_expr='exact')

    class Meta:
        model = add_trip
        fields = ['source', 'destination', 'pickup_city', 'mode_of_transport', 'parcel_capacity', 'travelling_date']

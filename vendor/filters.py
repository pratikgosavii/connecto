import django_filters
from django import forms
from vendor.models import trip  # adjust import if app name is different
from users.models import *


class TripFilter(django_filters.FilterSet):
    # Searchable text filters
   

    # City filters (FK lookup by city name)
    user = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),   # adjust if your User model is custom
        field_name="user",
        label="User",
        widget=forms.Select(attrs={"class": "form-control"})
    )


    # Source/Destination city names from Google fields
    source_city_name = django_filters.CharFilter(
        field_name="source_city_name", lookup_expr="icontains", label="Source City",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Source City"})
    )

    destination_city_name = django_filters.CharFilter(
        field_name="destination_city_name", lookup_expr="icontains", label="Destination City",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Destination City"})
    )

    # Mode of transport
    mode_of_transport = django_filters.ChoiceFilter(
        choices=trip.MODE_OF_TRANSPORT_CHOICES, label="Mode of Transport",
        widget=forms.Select(attrs={"class": "form-select"})
    )

    status = django_filters.ChoiceFilter(
        choices=trip.STATUS_CHOICES, label="Status",
        widget=forms.Select(attrs={"class": "form-select"})
    )

    # Date range
    departure_from = django_filters.DateTimeFilter(
        field_name="departure_datetime", lookup_expr="gte", label="Departure From",
        widget=forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"})
    )
    departure_to = django_filters.DateTimeFilter(
        field_name="departure_datetime", lookup_expr="lte", label="Departure To",
        widget=forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"})
    )

    arrival_from = django_filters.DateTimeFilter(
        field_name="arrival_datetime", lookup_expr="gte", label="Arrival From",
        widget=forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"})
    )
    arrival_to = django_filters.DateTimeFilter(
        field_name="arrival_datetime", lookup_expr="lte", label="Arrival To",
        widget=forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"})
    )

    class Meta:
        model = trip
        fields = [
            "user",
            "source_city_name",
            "destination_city_name",
            "mode_of_transport",
            "status",
            "departure_from",
            "departure_to",
            "arrival_from",
            "arrival_to",
        ]


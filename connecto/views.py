from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from datetime import date, timedelta
import json

from vendor.models import trip
from customer.models import (
    DeliveryRequest,
    Product,
    Customer_Order,
    Customer_Product_Order,
    PaymentLog,
)
from users.models import User


@login_required(login_url='login_admin')
def dashboard(request):
    """
    Admin dashboard showing real metrics and simple charts.
    """
    today = date.today()

    # Core counts
    total_users = User.objects.count()

    total_trips = trip.objects.count()
    trips_today = trip.objects.filter(created_at__date=today).count()

    total_parcels = DeliveryRequest.objects.count()
    parcels_today = DeliveryRequest.objects.filter(created_at__date=today).count()

    total_products = Product.objects.count()
    products_today = Product.objects.filter(created_at__date=today).count()

    total_parcel_orders = Customer_Order.objects.count()
    total_product_orders = Customer_Product_Order.objects.count()

    # Treat successful payments as active subscriptions
    active_subscriptions = PaymentLog.objects.filter(status="captured").count()

    # Simple 7‑day chart data for shipments (parcel + product)
    labels = []
    parcel_series = []
    product_series = []

    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        labels.append(day.strftime("%d %b"))

        parcel_series.append(
            Customer_Order.objects.filter(assigned_at__date=day).count()
        )
        product_series.append(
            Customer_Product_Order.objects.filter(assigned_at__date=day).count()
        )

    context = {
        "total_users": total_users,
        "total_trips": total_trips,
        "trips_today": trips_today,
        "total_parcels": total_parcels,
        "parcels_today": parcels_today,
        "total_products": total_products,
        "products_today": products_today,
        "total_parcel_orders": total_parcel_orders,
        "total_product_orders": total_product_orders,
        "active_subscriptions": active_subscriptions,
        # Chart data (JSON for JS)
        "chart_labels": json.dumps(labels),
        "chart_parcel_series": json.dumps(parcel_series),
        "chart_product_series": json.dumps(product_series),
    }

    return render(request, 'adminDashboard.html', context)


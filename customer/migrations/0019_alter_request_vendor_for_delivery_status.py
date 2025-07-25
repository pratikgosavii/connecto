# Generated by Django 5.1.4 on 2025-06-28 07:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0018_customer_order_connection_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='request_vendor_for_delivery',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('accepted_by_vendor', 'Vendor Accepted'), ('accepted', 'Accepted'), ('assigned', 'Assigned'), ('rejected_by_vendor', 'Rejected By Vendor'), ('rejected_by_customer', 'Rejected By Customer'), ('cancelled_by_customer', 'Cancelled')], default='pending', max_length=30),
        ),
    ]

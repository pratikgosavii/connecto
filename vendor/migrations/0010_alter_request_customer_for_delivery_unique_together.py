# Generated by Django 5.1.4 on 2025-06-28 08:43

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0020_alter_request_vendor_for_delivery_unique_together'),
        ('vendor', '0009_alter_request_customer_for_delivery_status'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='request_customer_for_delivery',
            unique_together={('trip', 'parcel', 'user')},
        ),
    ]

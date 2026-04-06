# users/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserCredit

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_credit(sender, instance, created, **kwargs):
    if created:
        UserCredit.objects.create(user=instance)

# users/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserCredit, Notification, UserToken
from firebase_admin import messaging

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_credit(sender, instance, created, **kwargs):
    if created:
        UserCredit.objects.create(user=instance)

@receiver(post_save, sender=Notification)
def send_push_notification(sender, instance, created, **kwargs):
    if created:
        tokens = UserToken.objects.filter(user=instance.user)
        for user_token in tokens:
            try:
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=instance.title,
                        body=instance.message,
                    ),
                    token=user_token.token,
                )
                messaging.send(message)
                print(f"Successfully sent push notification to {instance.user.mobile} at token {user_token.token[:10]}...")
            except Exception as e:
                print(f"Error sending push notification to {instance.user.mobile}: {e}")

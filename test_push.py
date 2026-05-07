import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'connecto.settings')
django.setup()

from firebase_admin import messaging

token = "fHPgJ3RUR0KxUY3Sd-HK_g:APA91bFle7u43myzYp6s4GC3oPS3uyAW8rOEk_IvgMFh9cBYz4zaH1DrP_-AanjPTMb1BEPoviBlJJePZutBFZneVxIV0EoWJHV5W2hFdKHB6-E3cFycR3U"

message = messaging.Message(
    notification=messaging.Notification(
        title='Test Notification',
        body='This is a test notification from Connecto API!',
    ),
    token=token,
)

try:
    response = messaging.send(message)
    print("✅ Successfully sent message! Firebase response ID:", response)
except Exception as e:
    print("❌ Error sending message:", e)

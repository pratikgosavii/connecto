# chat/utils.py
def generate_channel_id(user1_id, user2_id):
    ids = sorted([str(user1_id), str(user2_id)])
    return f"chat-{ids[0]}-{ids[1]}"



# utils.py
import base64
import uuid
from django.core.files.base import ContentFile

def save_base64_image(base64_string, upload_path="aadhaar_photos/"):
    """
    Saves a base64 image to Django's MEDIA_ROOT and returns the file name.
    """
    if not base64_string:
        return None

    try:
        # Generate a unique filename
        file_name = f"{uuid.uuid4()}.jpg"
        # Decode base64 string
        decoded_image = base64.b64decode(base64_string)
        return ContentFile(decoded_image, name=file_name)
    except Exception:
        return None

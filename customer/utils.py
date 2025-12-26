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


def ensure_city_exists(city_name):
    """
    Check if a city exists in the city table, if not, create it.
    Returns the city instance.
    
    Args:
        city_name: The name of the city to check/create
        
    Returns:
        city instance if successful, None otherwise
    """
    if not city_name:
        return None
    
    try:
        from masters.models import city
        
        # Clean and validate city name
        city_name = str(city_name).strip()
        if not city_name or city_name.lower() in ['none', 'null', '']:
            return None
        
        # Check if city exists (case-insensitive)
        city_instance = city.objects.filter(name__iexact=city_name).first()
        
        if not city_instance:
            # City doesn't exist, create it
            try:
                city_instance = city.objects.create(name=city_name)
                print(f"✅ Created new city: {city_name} (ID: {city_instance.id})")
            except Exception as create_error:
                # If creation fails (e.g., duplicate key), try to get it again
                print(f"⚠️ Error creating city '{city_name}': {create_error}, trying to fetch...")
                city_instance = city.objects.filter(name__iexact=city_name).first()
                if city_instance:
                    print(f"✓ City found after creation error: {city_name}")
                else:
                    raise
        else:
            print(f"✓ City already exists: {city_name} (ID: {city_instance.id})")
        
        return city_instance
    except Exception as e:
        print(f"❌ Error ensuring city exists for '{city_name}': {e}")
        import traceback
        traceback.print_exc()
        return None


def create_no_retry_session():
    """
    Create a requests session with no automatic retries.
    This prevents "too many tries" errors when proxy blocks requests.
    """
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    
    session = requests.Session()
    # Configure retry strategy: no retries at all
    retry_strategy = Retry(
        total=0,  # No retries
        backoff_factor=0,
        status_forcelist=[],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session
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


def send_sms(phone_number, message):
    """
    Send SMS to the given phone number with the given message.
    Logs all requests to requests.log file.
    
    Args:
        phone_number: Phone number in format (e.g., "+919876543210" or "9876543210")
        message: SMS message text
        
    Returns:
        dict with 'success' (bool) and 'response' (str or dict)
    """
    import os
    import requests
    import json
    from datetime import datetime
    from django.conf import settings
    
    # Setup logging to requests.log
    log_file_path = os.path.join(settings.BASE_DIR, 'requests.log')
    
    # Clean phone number (remove spaces, dashes, etc.)
    phone_number = str(phone_number).strip().replace(' ', '').replace('-', '')
    
    # Ensure phone number starts with country code (default to +91 for India)
    if not phone_number.startswith('+'):
        if phone_number.startswith('0'):
            phone_number = '+91' + phone_number[1:]
        else:
            phone_number = '+91' + phone_number
    
    # Get SMS API configuration from settings or environment
    # You can configure these in settings.py or .env file
    SMS_API_URL = getattr(settings, 'SMS_API_URL', os.getenv('SMS_API_URL', ''))
    SMS_API_KEY = getattr(settings, 'SMS_API_KEY', os.getenv('SMS_API_KEY', ''))
    SMS_SENDER_ID = getattr(settings, 'SMS_SENDER_ID', os.getenv('SMS_SENDER_ID', 'CONNECTO'))
    
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'phone_number': phone_number,
        'message': message,
        'sms_api_url': SMS_API_URL,
        'sms_sender_id': SMS_SENDER_ID,
    }
    
    try:
        # If SMS API is not configured, log and return
        if not SMS_API_URL or not SMS_API_KEY:
            log_entry['status'] = 'skipped'
            log_entry['reason'] = 'SMS API not configured (SMS_API_URL or SMS_API_KEY missing)'
            log_entry['success'] = False
            
            # Write to log file
            with open(log_file_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
            
            print(f"⚠️ SMS not sent: {log_entry['reason']}")
            return {'success': False, 'response': log_entry['reason']}
        
        # Prepare SMS API request
        # This is a generic template - adjust based on your SMS provider
        # Common providers: MSG91, Twilio, TextLocal, etc.
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {SMS_API_KEY}' if SMS_API_KEY else None
        }
        
        # Generic payload structure (adjust based on your SMS provider)
        payload = {
            'to': phone_number,
            'message': message,
            'sender': SMS_SENDER_ID,
        }
        
        # Remove None values from headers
        headers = {k: v for k, v in headers.items() if v is not None}
        
        log_entry['request_headers'] = {k: '***' if 'key' in k.lower() or 'auth' in k.lower() else v for k, v in headers.items()}
        log_entry['request_payload'] = payload
        
        # Make API request
        session = create_no_retry_session()
        response = session.post(
            SMS_API_URL,
            json=payload,
            headers=headers,
            timeout=10
        )
        
        log_entry['response_status'] = response.status_code
        log_entry['response_body'] = response.text[:500]  # Limit response body length
        
        # Check if request was successful
        if response.status_code in [200, 201]:
            log_entry['status'] = 'success'
            log_entry['success'] = True
            try:
                log_entry['response_json'] = response.json()
            except:
                pass
        else:
            log_entry['status'] = 'failed'
            log_entry['success'] = False
            log_entry['error'] = f'HTTP {response.status_code}'
        
    except requests.exceptions.RequestException as e:
        log_entry['status'] = 'error'
        log_entry['success'] = False
        log_entry['error'] = str(e)
        log_entry['error_type'] = type(e).__name__
        print(f"❌ SMS sending error: {e}")
    
    except Exception as e:
        log_entry['status'] = 'error'
        log_entry['success'] = False
        log_entry['error'] = str(e)
        log_entry['error_type'] = type(e).__name__
        print(f"❌ Unexpected error sending SMS: {e}")
    
    finally:
        # Always write to log file
        try:
            with open(log_file_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"❌ Error writing to requests.log: {e}")
    
    return {
        'success': log_entry.get('success', False),
        'response': log_entry.get('response_body', log_entry.get('error', 'Unknown error'))
    }
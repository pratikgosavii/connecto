import logging
import random
import re
from datetime import timedelta

import requests
from django.conf import settings
from django.utils import timezone

from .models import OTP


logger = logging.getLogger("otp_service")


def clean_mobile(mobile: str) -> str:
    """
    Keep only digits from the mobile string.
    """
    if not mobile:
        return ""
    return re.sub(r"\D", "", str(mobile))


def create_and_send_otp(mobile: str):
    """
    Generate a 6-digit OTP, store it, and send via msg.msgclub.net.

    Returns: (otp_obj, success: bool, message: str)
    """
    mobile_clean = clean_mobile(mobile)
    if not mobile_clean:
        return None, False, "Invalid mobile number"

    # Generate OTP and expiry using settings
    length = getattr(settings, "OTP_LENGTH", 6)
    min_val = 10 ** (length - 1)
    max_val = (10 ** length) - 1
    otp_code = f"{random.randint(min_val, max_val)}"

    now = timezone.now()
    expiry_minutes = getattr(settings, "OTP_EXPIRY_MINUTES", 5)
    expires_at = now + timedelta(minutes=expiry_minutes)

    # Create or update OTP entry
    otp_obj = OTP.objects.create(
        mobile=mobile_clean,
        otp_code=otp_code,
        expires_at=expires_at,
        is_verified=False,
    )

    api_url = getattr(
        settings,
        "MSG_CLUB_API_URL",
        "http://msg.msgclub.net/rest/services/sendSMS/sendGroupSms",
    )
    api_key = getattr(settings, "MSG_CLUB_API_KEY", "")
    sender_id = getattr(settings, "MSG_CLUB_SENDER_ID", "")
    route_id = getattr(settings, "MSG_CLUB_ROUTE_ID", "")
    sms_content_type = getattr(settings, "MSG_CLUB_SMS_CONTENT_TYPE", "english")
    template = getattr(
        settings,
        "OTP_MESSAGE_TEMPLATE",
        "Your OTP is {otp_code}.",
    )

    if not api_key or not sender_id or not route_id:
        msg = "OTP gateway not configured (MSG_CLUB_API_KEY / MSG_CLUB_SENDER_ID / MSG_CLUB_ROUTE_ID missing)"
        logger.error(msg, extra={"mobile": mobile_clean})
        return otp_obj, False, msg

    message_text = template.format(otp_code=otp_code)

    params = {
        "AUTH_KEY": api_key,
        "message": message_text,
        "senderId": sender_id,
        "routeId": route_id,
        "mobileNos": mobile_clean,
        "smsContentType": sms_content_type,
    }

    logger.info(
        "Sending OTP via msg.msgclub",
        extra={
            "mobile": mobile_clean,
            "url": api_url,
            "senderId": sender_id,
            "routeId": route_id,
        },
    )

    try:
        resp = requests.get(api_url, params=params, timeout=20)
        text = resp.text
        try:
            data = resp.json()
        except Exception:
            data = {}

        code = str(data.get("responseCode") or data.get("code") or "").strip()
        provider_message = (
            data.get("responseMessage")
            or data.get("message")
            or text
            or "No response message"
        )

        logger.info(
            "OTP gateway response",
            extra={
                "mobile": mobile_clean,
                "status_code": resp.status_code,
                "response_code": code,
                "response_message": provider_message,
            },
        )

        # Treat standard success code 3001 as success
        if resp.status_code == 200 and (code == "3001" or not code):
            return otp_obj, True, "OTP sent successfully"

        error_msg = (
            f"Failed to send OTP: {provider_message} (Code: {code or 'unknown'})"
        )
        return otp_obj, False, error_msg

    except requests.RequestException as exc:
        logger.exception(
            "OTP sending error",
            extra={"mobile": mobile_clean, "error": str(exc)},
        )
        return otp_obj, False, f"Failed to send OTP due to network error: {exc}"


def verify_otp(mobile: str, otp_code: str):
    """
    Verify the most recent non-expired OTP for the given mobile.

    Returns: (otp_obj_or_None, is_valid: bool, message: str)
    """
    mobile_clean = clean_mobile(mobile)
    if not mobile_clean:
        return None, False, "Invalid mobile number"

    now = timezone.now()
    otp_obj = (
        OTP.objects.filter(mobile=mobile_clean, expires_at__gte=now)
        .order_by("-created_at")
        .first()
    )

    if not otp_obj:
        return None, False, "OTP expired or not found"

    if otp_obj.is_verified:
        # Allow re-use within validity window if already verified
        if otp_obj.otp_code == str(otp_code).strip():
            return otp_obj, True, "OTP already verified"
        return otp_obj, False, "Invalid OTP code"

    if otp_obj.otp_code != str(otp_code).strip():
        return otp_obj, False, "Invalid OTP code"

    # Mark as verified
    otp_obj.is_verified = True
    otp_obj.verified_at = now
    otp_obj.save(update_fields=["is_verified", "verified_at"])

    return otp_obj, True, "OTP verified successfully"


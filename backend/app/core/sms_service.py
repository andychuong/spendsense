"""SMS service for phone verification using AWS SNS."""

import secrets
import boto3
from botocore.exceptions import ClientError, BotoCoreError
from typing import Optional
import phonenumbers
from phonenumbers import NumberParseException

from app.config import settings
from app.core.redis_client import get_redis_client


# SMS message template
SMS_MESSAGE_TEMPLATE = "Your SpendSense verification code is: {code}. This code expires in 10 minutes."

# Rate limiting constants
SMS_RATE_LIMIT_HOUR = 5  # Max 5 SMS per hour per phone
SMS_RATE_LIMIT_DAY = 10  # Max 10 SMS per day per phone
CODE_EXPIRATION_SECONDS = 600  # 10 minutes
CODE_MAX_ATTEMPTS = 3  # Max 3 verification attempts per code


def validate_phone_number(phone: str) -> str:
    """
    Validate and normalize phone number to E.164 format.
    
    Args:
        phone: Phone number string
        
    Returns:
        Normalized phone number in E.164 format (e.g., +1234567890)
        
    Raises:
        ValueError: If phone number is invalid
    """
    try:
        # Parse phone number (default region is US if not specified)
        parsed = phonenumbers.parse(phone, "US")
        
        # Validate phone number
        if not phonenumbers.is_valid_number(parsed):
            raise ValueError("Invalid phone number")
        
        # Format to E.164
        e164 = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        
        return e164
    except NumberParseException as e:
        raise ValueError(f"Invalid phone number format: {str(e)}")


def generate_verification_code() -> str:
    """
    Generate a cryptographically secure 6-digit verification code.
    
    Returns:
        6-digit numeric code as string
    """
    # Generate a random number between 100000 and 999999
    code = secrets.randbelow(900000) + 100000
    return str(code)


def store_verification_code(phone: str, code: str) -> bool:
    """
    Store verification code in Redis with TTL.
    
    Args:
        phone: Phone number in E.164 format
        code: Verification code
        
    Returns:
        True if code was stored successfully, False otherwise
    """
    redis_client = get_redis_client()
    if redis_client is None:
        return False
    
    try:
        # Store code with expiration (10 minutes)
        key = f"phone_verification:{phone}"
        redis_client.setex(key, CODE_EXPIRATION_SECONDS, code)
        
        # Store attempt count (starts at 0)
        attempts_key = f"phone_verification_attempts:{phone}"
        redis_client.setex(attempts_key, CODE_EXPIRATION_SECONDS, "0")
        
        return True
    except Exception:
        return False


def verify_verification_code(phone: str, code: str) -> bool:
    """
    Verify a phone verification code.
    
    Args:
        phone: Phone number in E.164 format
        code: Verification code to verify
        
    Returns:
        True if code is valid, False otherwise
        
    Raises:
        ValueError: If max attempts exceeded
    """
    redis_client = get_redis_client()
    if redis_client is None:
        return False
    
    try:
        # Get stored code
        key = f"phone_verification:{phone}"
        stored_code = redis_client.get(key)
        
        if stored_code is None:
            return False
        
        # Check attempts
        attempts_key = f"phone_verification_attempts:{phone}"
        attempts = int(redis_client.get(attempts_key) or "0")
        
        if attempts >= CODE_MAX_ATTEMPTS:
            # Delete code to prevent further attempts
            redis_client.delete(key)
            redis_client.delete(attempts_key)
            raise ValueError("Maximum verification attempts exceeded. Please request a new code.")
        
        # Increment attempts
        redis_client.incr(attempts_key)
        
        # Verify code
        if stored_code == code:
            # Delete code and attempts on success
            redis_client.delete(key)
            redis_client.delete(attempts_key)
            return True
        
        return False
    except ValueError:
        raise
    except Exception:
        return False


def check_sms_rate_limit(phone: str) -> tuple[bool, Optional[str]]:
    """
    Check if SMS rate limit is exceeded.
    
    Args:
        phone: Phone number in E.164 format
        
    Returns:
        Tuple of (is_allowed, error_message)
        is_allowed: True if SMS can be sent, False if rate limited
        error_message: Error message if rate limited, None otherwise
    """
    redis_client = get_redis_client()
    if redis_client is None:
        # If Redis is unavailable, allow SMS (fallback)
        return True, None
    
    try:
        # Check hourly limit
        hour_key = f"sms_rate_limit_hour:{phone}"
        hour_count = int(redis_client.get(hour_key) or "0")
        
        if hour_count >= SMS_RATE_LIMIT_HOUR:
            return False, "Too many SMS requests. Please try again in an hour."
        
        # Check daily limit
        day_key = f"sms_rate_limit_day:{phone}"
        day_count = int(redis_client.get(day_key) or "0")
        
        if day_count >= SMS_RATE_LIMIT_DAY:
            return False, "Daily SMS limit exceeded. Please try again tomorrow."
        
        return True, None
    except Exception:
        # If Redis check fails, allow SMS (fallback)
        return True, None


def increment_sms_rate_limit(phone: str) -> None:
    """
    Increment SMS rate limit counters.
    
    Args:
        phone: Phone number in E.164 format
    """
    redis_client = get_redis_client()
    if redis_client is None:
        return
    
    try:
        # Increment hourly counter (1 hour TTL)
        hour_key = f"sms_rate_limit_hour:{phone}"
        redis_client.incr(hour_key)
        redis_client.expire(hour_key, 3600)  # 1 hour
        
        # Increment daily counter (24 hours TTL)
        day_key = f"sms_rate_limit_day:{phone}"
        redis_client.incr(day_key)
        redis_client.expire(day_key, 86400)  # 24 hours
    except Exception:
        # If Redis fails, continue anyway
        pass


def send_sms(phone: str, message: str) -> tuple[bool, Optional[str]]:
    """
    Send SMS message using AWS SNS.
    
    In mock mode (SMS_MOCK_MODE=true), logs the message to console instead of sending.
    This is useful for local development when AWS SNS is not available.
    
    Args:
        phone: Phone number in E.164 format
        message: SMS message text
        
    Returns:
        Tuple of (success, error_message)
        success: True if SMS was sent successfully, False otherwise
        error_message: Error message if failed, None otherwise
    """
    # Mock mode: Log to console instead of sending SMS
    if settings.sms_mock_mode:
        print("\n" + "=" * 80)
        print("📱 MOCK SMS (Development Mode)")
        print("=" * 80)
        print(f"To: {phone}")
        print(f"Message: {message}")
        print("=" * 80)
        print("NOTE: This is a mock SMS. In production, this would be sent via AWS SNS.")
        print("=" * 80 + "\n")
        return True, None
    
    try:
        # Create SNS client
        sns_client = boto3.client(
            "sns",
            region_name=settings.sns_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
        )
        
        # Send SMS
        response = sns_client.publish(
            PhoneNumber=phone,
            Message=message,
        )
        
        # Check if message was sent successfully
        message_id = response.get("MessageId")
        if message_id:
            return True, None
        else:
            return False, "Failed to send SMS: No message ID returned"
            
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        error_message = e.response.get("Error", {}).get("Message", str(e))
        return False, f"AWS SNS error ({error_code}): {error_message}"
    except BotoCoreError as e:
        return False, f"AWS SDK error: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error sending SMS: {str(e)}"


def send_verification_code(phone: str) -> tuple[bool, Optional[str]]:
    """
    Generate and send verification code via SMS.
    
    This function:
    1. Validates phone number
    2. Checks rate limits
    3. Generates verification code
    4. Stores code in Redis
    5. Sends SMS via AWS SNS
    6. Increments rate limit counters
    
    Args:
        phone: Phone number string (will be normalized to E.164)
        
    Returns:
        Tuple of (success, error_message)
        success: True if code was sent successfully, False otherwise
        error_message: Error message if failed, None otherwise
    """
    try:
        # Validate and normalize phone number
        normalized_phone = validate_phone_number(phone)
        
        # Check rate limits
        is_allowed, error_message = check_sms_rate_limit(normalized_phone)
        if not is_allowed:
            return False, error_message
        
        # Generate verification code
        code = generate_verification_code()
        
        # Store code in Redis
        if not store_verification_code(normalized_phone, code):
            return False, "Failed to store verification code"
        
        # Format SMS message
        message = SMS_MESSAGE_TEMPLATE.format(code=code)
        
        # Send SMS
        success, error_message = send_sms(normalized_phone, message)
        
        if success:
            # Increment rate limit counters
            increment_sms_rate_limit(normalized_phone)
            return True, None
        else:
            # If SMS failed, delete stored code
            redis_client = get_redis_client()
            if redis_client:
                try:
                    redis_client.delete(f"phone_verification:{normalized_phone}")
                    redis_client.delete(f"phone_verification_attempts:{normalized_phone}")
                except Exception:
                    pass
            return False, error_message
            
    except ValueError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


# C:\Users\Sonam Gavhane\OneDrive\Desktop\SmartCartAI\utils\security.py

import re
import secrets
import hashlib
import hmac
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)

def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Validate password strength
    Returns (is_valid, message)
    """
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    
    if len(password) > 50:
        return False, "Password must be less than 50 characters"
    
    # Check for at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    # Check for at least one lowercase letter
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    # Check for at least one number
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    # Check for at least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, "Password is strong"

def generate_reset_token() -> str:
    """Generate a secure password reset token"""
    return secrets.token_urlsafe(32)

def hash_token(token: str) -> str:
    """Hash a token for storage (one-way hash)"""
    return hashlib.sha256(token.encode()).hexdigest()

def sanitize_input(input_str: str) -> str:
    """
    Sanitize user input to prevent XSS attacks
    """
    if not input_str:
        return input_str
    
    # Replace potentially dangerous characters
    dangerous = ['<', '>', '"', "'", '&', ';', '--']
    for char in dangerous:
        input_str = input_str.replace(char, '')
    
    return input_str.strip()

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """Validate Indian phone number (10 digits)"""
    return bool(re.match(r'^[6-9]\d{9}$', phone))

def validate_pincode(pincode: str) -> bool:
    """Validate Indian PIN code (6 digits)"""
    return bool(re.match(r'^[1-9][0-9]{5}$', pincode))

def mask_email(email: str) -> str:
    """
    Mask email for display: john.doe@example.com -> j***e@example.com
    """
    if not email or '@' not in email:
        return email
    
    local_part, domain = email.split('@', 1)
    if len(local_part) <= 2:
        masked_local = local_part[0] + '***'
    else:
        masked_local = local_part[0] + '***' + local_part[-1]
    
    return f"{masked_local}@{domain}"

def mask_phone(phone: str) -> str:
    """
    Mask phone for display: 9876543210 -> 98*****210
    """
    if not phone or len(phone) != 10:
        return phone
    
    return phone[:2] + '*****' + phone[-3:]

def generate_session_id() -> str:
    """Generate a unique session ID"""
    return secrets.token_urlsafe(32)

def is_safe_redirect_url(url: str) -> bool:
    """
    Check if a redirect URL is safe (prevents open redirect vulnerabilities)
    """
    # Only allow relative URLs or same-domain URLs
    if url.startswith(('http://', 'https://')):
        # Check if it's our own domain
        from urllib.parse import urlparse
        parsed = urlparse(url)
        allowed_domains = ['localhost', '127.0.0.1', 'smartcartai.com', 'www.smartcartai.com']
        return parsed.netloc in allowed_domains
    
    # Allow relative URLs
    if url.startswith('/'):
        return True
    
    return False

def rate_limit_key(request) -> str:
    """
    Generate a rate limiting key based on IP and user agent
    """
    ip = request.client.host if request.client else 'unknown'
    user_agent = request.headers.get('user-agent', 'unknown')
    
    # Create a hash of IP + User Agent
    combined = f"{ip}:{user_agent}"
    return hashlib.md5(combined.encode()).hexdigest()
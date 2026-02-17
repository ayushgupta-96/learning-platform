# backend/app/utils/validators.py
import re

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Password must be at least 6 characters"""
    return len(password) >= 6

def validate_mobile(mobile):
    """Indian mobile number validation"""
    pattern = r'^[6-9]\d{9}$'
    return re.match(pattern, mobile) is not None

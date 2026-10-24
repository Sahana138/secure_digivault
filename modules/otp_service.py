# file: modules/otp_service.py

import random
import time

# CONFIGURATION

OTP_LENGTH = 6
OTP_EXPIRY_SECONDS = 60  # OTP validity window

# OTP STATE STORAGE

# Temporary in-memory OTP storage
current_otp = None
otp_time = None

# OTP GENERATION

def generate_otp():
    """
    Generate OTP and store creation timestamp.
    """

    global current_otp, otp_time

    # Random 6-digit numeric OTP
    current_otp = str(random.randint(100000,999999))
    otp_time = time.time()

    return current_otp

# OTP VERIFICATION

def verify_otp(user_otp):
    """
    Validate user-provided OTP.
    """

    global current_otp, otp_time

    # No OTP generated
    if current_otp is None:
        return False

    # Expiration protection
    if time.time() - otp_time > OTP_EXPIRY_SECONDS:
        current_otp = None
        otp_time = None
        return False

    # Successful OTP match
    if user_otp == current_otp:
        current_otp = None
        otp_time = None
        return True

    return False
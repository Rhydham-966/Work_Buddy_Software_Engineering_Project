# services/auth_service.py

import random
from datetime import datetime

from repositories.user_repository import (
    create_user,
    get_user_by_phone,
    verify_user,
    get_user_by_id as repo_get_user_by_id
)

from repositories.otp_repository import (
    create_otp,
    get_valid_otp,
    mark_otp_used
)


def generate_otp():
    return str(random.randint(100000, 999999))


# ---------------- REGISTER ----------------
def register_user(name, email, phone, password, role):
    existing_user = get_user_by_phone(phone)

    if existing_user:
        print("User already exists!")
        return None

    user_id = create_user(name, email, phone, password, role)

    otp = generate_otp()
    create_otp(user_id, otp)

    print(f"[DEBUG OTP] Your OTP is: {otp}")  # For terminal logs

    return user_id, otp


# ---------------- VERIFY OTP ----------------
def verify_otp(user_id, entered_otp):
    otp_record = get_valid_otp(user_id, entered_otp)

    if not otp_record:
        print("Invalid OTP!")
        return False

    if otp_record["expiry_time"] < datetime.now():
        print("OTP expired!")
        return False

    mark_otp_used(otp_record["id"])
    verify_user(user_id)

    print("User verified successfully!")
    return True


# ---------------- LOGIN ----------------
def login_user(phone, password):
    user = get_user_by_phone(phone)

    if not user:
        print("User not found!")
        return None

    if user["password"] != password:
        print("Wrong password!")
        return None

    if not user["is_verified"]:
        print("User not verified!")
        return None

    print("Login successful!")
    return user

def get_user_by_id(user_id):
    return repo_get_user_by_id(user_id)
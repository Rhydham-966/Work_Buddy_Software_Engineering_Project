import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import mysql.connector
from database.db import get_connection

TEST_EMAIL_SUFFIX = "@workbuddy.local.test"
TEST_PHONE_PREFIX = "T99"

def clear_test_data():
    conn = get_connection()
    if not conn:
        return
    cursor = conn.cursor()
    
    # Due to ON DELETE CASCADE on all tables, dropping test users drops EVERYTHING associated.
    cursor.execute("DELETE FROM users WHERE email LIKE %s OR phone LIKE %s", (f"%{TEST_EMAIL_SUFFIX}", f"{TEST_PHONE_PREFIX}%"))
    
    # We also need to wipe services created during tests
    cursor.execute("DELETE FROM services WHERE name LIKE '%Test Service%' OR name LIKE '%INT SERVICE%'")
    
    conn.commit()
    cursor.close()
    conn.close()

def create_raw_test_user(name, phone, role="customer", is_verified=True):
    email = f"{name.lower().replace(' ', '')}{TEST_EMAIL_SUFFIX}"
    phone = f"{TEST_PHONE_PREFIX}{phone}"
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (name, email, phone, password, role, is_verified) VALUES (%s, %s, %s, %s, %s, %s)",
        (name, email, phone, "testpass", role, is_verified)
    )
    conn.commit()
    user_id = cursor.lastrowid
    cursor.close()
    conn.close()
    
    # Return user object dict format mostly used by services
    return {
        "id": user_id,
        "name": name,
        "email": email,
        "phone": phone,
        "role": role,
        "password": "testpass"
    }

def fetch_db_otp(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT otp_code FROM otp_verification WHERE user_id = %s ORDER BY id DESC LIMIT 1", (user_id,))
    res = cursor.fetchone()
    cursor.close()
    conn.close()
    return res[0] if res else None

def create_test_service(name="Test Service A", price=100.0):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO services (name, description, base_price, estimated_time) VALUES (%s, %s, %s, %s)",
                   (name, "Test description", price, "1 hour"))
    conn.commit()
    sid = cursor.lastrowid
    cursor.close()
    conn.close()
    return sid

def create_test_professional(user_id, is_approved=False):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO professionals (user_id, experience, area, work_radius, is_approved) VALUES (%s, 5, 'TestCity', 10, %s)", (user_id, is_approved))
    conn.commit()
    pid = cursor.lastrowid
    cursor.close()
    conn.close()
    return pid


def create_test_booking(customer_id, professional_id, service_id,
                        booking_type="scheduled", payment_method="cash",
                        total_price=100.0, slot_id=None):
    """Helper: create a booking with sensible defaults for test DRY-ness."""
    from services.booking_service import create_booking
    return create_booking(
        customer_id, professional_id, service_id,
        booking_type, payment_method, total_price,
        slot_id=slot_id
    )

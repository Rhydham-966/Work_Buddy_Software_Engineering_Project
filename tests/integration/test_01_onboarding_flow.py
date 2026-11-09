# tests/integration/test_01_onboarding_flow.py
# ============================================================
# INTEGRATION TEST — User Onboarding Component
#
# Simulates the customer onboarding journey:
#   1. Register a customer
#   2. Verify OTP (auto-retrieved from DB)
#   3. Login the customer
# ============================================================

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from services.auth_service import register_user, verify_otp, login_user
from database.db import get_connection


def test_onboarding_flow(db_connection, unique_id):
    customer_user_id = None
    
    try:
        # STEP 1: Register
        phone = "99" + unique_id
        password = "flowpass123"
        customer_user_id = register_user(
            name=f"FlowCust_{unique_id}",
            email=f"onb_{unique_id}@test.com",
            phone=phone,
            password=password,
            role="customer"
        )
        assert customer_user_id is not None, "Registration failed"

        # STEP 2: Verify OTP
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT otp_code FROM otp_verification WHERE user_id = %s AND is_used = FALSE ORDER BY id DESC LIMIT 1",
            (customer_user_id,)
        )
        otp_record = cursor.fetchone()
        cursor.close()
        conn.close()

        assert verify_otp(customer_user_id, otp_record["otp_code"]) is True, "OTP verification failed"

        # STEP 3: Login
        user = login_user(phone, password)
        assert user is not None and user["id"] == customer_user_id, "Login failed"
        assert user["is_verified"] in (1, True), "User not verified after boarding"

    finally:
        # CLEANUP
        if customer_user_id:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM otp_verification WHERE user_id = %s", (customer_user_id,))
            cursor.execute("DELETE FROM users WHERE id = %s", (customer_user_id,))
            conn.commit()
            cursor.close()
            conn.close()

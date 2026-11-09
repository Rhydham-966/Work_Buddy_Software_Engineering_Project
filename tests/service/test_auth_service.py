# tests/service/test_auth_service.py
# ============================================================
# Service-layer tests for services/auth_service.py
# Tests: register_user, login_user, verify_otp
# Uses REAL MySQL — no mocking.
# ============================================================

import sys                                          # for path manipulation
import os                                           # for path joining

# -- Ensure project root is importable --
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from services.auth_service import (                 # import service functions
    register_user,                                  # registers a new user + sends OTP
    login_user,                                     # logs in with phone + password
    verify_otp                                      # verifies a user's OTP
)
from repositories.user_repository import (          # direct repo access for verification
    get_user_by_phone                               # needed to look up created users
)
from repositories.otp_repository import (           # direct repo access for OTP lookup
    get_valid_otp                                   # needed to retrieve the generated OTP
)
from database.db import get_connection              # direct DB access for cleanup


# ============================================================
# HELPER: unique values
# ============================================================


# ============================================================
# TEST 1: register_user — successful registration
# ============================================================
def test_register_user_success(db_connection, unique_id):
    """register_user should create a user and return a positive user ID."""
    phone = "99" + unique_id                        # unique phone number
    email = f"reg_{unique_id}@test.com"               # unique email
    name = f"RegUser_{unique_id}"                    # unique name
    password = "securepass"                          # password
    role = "customer"                               # role

    user_id = register_user(                        # call the service function
        name=name,                                  # user name
        email=email,                                # user email
        phone=phone,                                # user phone
        password=password,                          # user password
        role=role                                   # user role
    )

    assert user_id is not None, "register_user must return a user ID"     # not None
    assert isinstance(user_id, int), "User ID must be an integer"         # correct type
    assert user_id > 0, "User ID must be positive"                       # positive

    # -- Verify user exists in DB --
    user = get_user_by_phone(phone)                 # look up the user
    assert user is not None, "User must exist in DB after registration"   # must exist
    assert user["name"] == name, "Name must match"                       # correct name

    # -- CLEANUP: delete user (CASCADE removes OTPs) --
    conn = get_connection()                         # fresh connection
    cursor = conn.cursor()                          # open cursor
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))   # delete
    conn.commit()                                   # persist
    cursor.close()                                  # close cursor
    conn.close()                                    # close connection


# ============================================================
# TEST 2: register_user — duplicate phone returns None
# ============================================================
def test_register_user_duplicate_phone(db_connection, unique_id):
    """Registering with an already-used phone should return None."""
    phone = "99" + unique_id                        # shared phone
    email1 = f"dup1_{unique_id}@test.com"             # first email
    email2 = f"dup2_{unique_id}@test.com"             # second email
    user_id = None                                  # track first user for cleanup

    try:
        user_id = register_user(                    # first registration — should succeed
            name="DupRegTest1", email=email1,
            phone=phone, password="pass1", role="customer"
        )
        assert user_id is not None, "First registration must succeed"  # sanity check

        result = register_user(                     # second registration — same phone
            name="DupRegTest2", email=email2,
            phone=phone, password="pass2", role="customer"
        )
        assert result is None, \
            "Duplicate phone registration must return None"  # service should reject
    finally:
        # -- CLEANUP --
        if user_id:                                 # clean up the first user
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            conn.commit()
            cursor.close()
            conn.close()


# ============================================================
# TEST 3: login_user — successful login (verified user)
# ============================================================
def test_login_user_success(db_connection, test_user):
    """login_user should return the user dict for correct credentials."""
    result = login_user(                            # call service function
        phone=test_user["phone"],                   # correct phone
        password=test_user["password"]              # correct password
    )

    assert result is not None, "Login must succeed for valid credentials"  # not None
    assert result["id"] == test_user["id"], "User ID must match"          # correct user
    assert result["phone"] == test_user["phone"], "Phone must match"      # correct phone


# ============================================================
# TEST 4: login_user — wrong password returns None
# ============================================================
def test_login_user_wrong_password(db_connection, test_user):
    """login_user should return None if the password is incorrect."""
    result = login_user(                            # call with wrong password
        phone=test_user["phone"],                   # correct phone
        password="WRONG_PASSWORD_123"               # incorrect password
    )

    assert result is None, "Wrong password must return None"  # must fail


# ============================================================
# TEST 5: login_user — non-existent phone returns None
# ============================================================
def test_login_user_nonexistent_phone(db_connection, unique_id):
    """login_user should return None for a phone that doesn't exist."""
    fake_phone = "00" + unique_id                   # phone never registered

    result = login_user(                            # call with fake phone
        phone=fake_phone,                           # non-existent phone
        password="anypass"                          # any password
    )

    assert result is None, "Non-existent phone must return None"  # must fail


# ============================================================
# TEST 6: login_user — unverified user returns None
# ============================================================
def test_login_user_unverified(db_connection, unique_id):
    """login_user should return None if the user is not verified."""
    phone = "99" + unique_id                        # unique phone
    email = f"unv_{unique_id}@test.com"               # unique email
    password = "testpass"                           # password
    user_id = None                                  # for cleanup

    try:
        user_id = register_user(                    # register (creates unverified user)
            name="UnverifiedUser", email=email,
            phone=phone, password=password, role="customer"
        )
        assert user_id is not None                  # registration succeeded

        result = login_user(phone=phone, password=password)  # try to login

        assert result is None, \
            "Unverified user must not be able to login"  # must fail
    finally:
        # -- CLEANUP --
        if user_id:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            conn.commit()
            cursor.close()
            conn.close()


# ============================================================
# TEST 7: verify_otp — successful verification
# ============================================================
def test_verify_otp_success(db_connection, unique_id):
    """verify_otp should return True when given the correct OTP."""
    phone = "99" + unique_id                        # unique phone
    email = f"otp_{unique_id}@test.com"               # unique email
    user_id = None                                  # for cleanup

    try:
        user_id = register_user(                    # register the user (generates OTP)
            name="OTPUser", email=email,
            phone=phone, password="otppass", role="customer"
        )
        assert user_id is not None                  # registration succeeded

        # -- Retrieve the OTP from the DB (since it's printed in debug mode) --
        conn = get_connection()                     # fresh connection
        cursor = conn.cursor(dictionary=True)       # dictionary cursor
        cursor.execute(                             # fetch the latest OTP for this user
            """
            SELECT * FROM otp_verification
            WHERE user_id = %s AND is_used = FALSE
            ORDER BY id DESC LIMIT 1
            """,
            (user_id,)
        )
        otp_record = cursor.fetchone()              # get the OTP record
        cursor.close()                              # close cursor
        conn.close()                                # close connection

        assert otp_record is not None, "OTP record must exist after registration"

        # -- Verify the OTP --
        success = verify_otp(                       # call service function
            user_id=user_id,                        # user's ID
            entered_otp=otp_record["otp_code"]      # correct OTP code
        )

        assert success is True, "verify_otp must return True for correct OTP"

        # -- Confirm user is now verified --
        user = get_user_by_phone(phone)             # fetch user
        assert user["is_verified"] == 1 or user["is_verified"] is True, \
            "User must be verified after OTP verification"
    finally:
        # -- CLEANUP --
        if user_id:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            conn.commit()
            cursor.close()
            conn.close()


# ============================================================
# TEST 8: verify_otp — wrong OTP returns False
# ============================================================
def test_verify_otp_wrong_code(db_connection, unique_id):
    """verify_otp should return False for an incorrect OTP code."""
    phone = "99" + unique_id                        # unique phone
    email = f"wotp_{unique_id}@test.com"              # unique email
    user_id = None                                  # for cleanup

    try:
        user_id = register_user(                    # register the user
            name="WrongOTPUser", email=email,
            phone=phone, password="otppass", role="customer"
        )
        assert user_id is not None                  # registration succeeded

        result = verify_otp(                        # call with wrong OTP
            user_id=user_id,                        # correct user ID
            entered_otp="000000"                    # wrong OTP code
        )

        assert result is False, "Wrong OTP must return False"  # must fail
    finally:
        # -- CLEANUP --
        if user_id:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            conn.commit()
            cursor.close()
            conn.close()

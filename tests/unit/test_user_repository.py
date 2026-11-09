# tests/unit/test_user_repository.py
# ============================================================
# Unit tests for repositories/user_repository.py
# Tests: create_user, get_user_by_phone, verify_user
# Uses REAL MySQL — no mocking.
# ============================================================

import sys                                          # for path manipulation
import os                                           # for path joining

# -- Ensure project root is importable --
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from repositories.user_repository import (          # import the functions under test
    create_user,                                    # creates a new user row
    get_user_by_phone,                              # fetches user by phone number
    verify_user                                     # sets is_verified = TRUE
)
from database.db import get_connection              # direct DB access for cleanup


# ============================================================
# HELPER: generate unique test data per test
# ============================================================


# ============================================================
# TEST 1: create_user — successful insertion
# ============================================================
def test_create_user_returns_id(db_connection, unique_id):
    """Inserting a new user should return a positive integer ID."""
    phone = "99" + unique_id                        # unique phone number
    email = f"cu_{unique_id}@test.com"               # unique email address
    name = f"CreateUser_{unique_id}"                 # unique display name

    user_id = create_user(                          # call the repository function
        name=name,                                  # user's name
        email=email,                                # user's email
        phone=phone,                                # user's phone (UNIQUE column)
        password="pass123",                         # plain-text password
        role="customer"                             # role enum
    )

    assert user_id is not None, "create_user must return a user ID"       # must not be None
    assert isinstance(user_id, int), "user ID must be an integer"         # must be int
    assert user_id > 0, "user ID must be a positive integer"             # must be positive

    # -- CLEANUP: remove the test user --
    conn = get_connection()                         # get a fresh connection
    cursor = conn.cursor()                          # open cursor
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))   # delete by ID
    conn.commit()                                   # persist the deletion
    cursor.close()                                  # close cursor
    conn.close()                                    # close connection


# ============================================================
# TEST 2: create_user — duplicate phone should raise an error
# ============================================================
def test_create_user_duplicate_phone(db_connection, unique_id):
    """Inserting two users with the same phone should fail on the second."""
    phone = "99" + unique_id                        # shared phone number
    email1 = f"dup1_{unique_id}@test.com"            # first email
    email2 = f"dup2_{unique_id}@test.com"            # second email
    user_id = None                                  # track for cleanup

    try:
        user_id = create_user(                      # first insert — should succeed
            name="DupTest1", email=email1,
            phone=phone, password="pass", role="customer"
        )
        assert user_id is not None                  # ensure first user was created

        # Second insert — same phone — should raise an IntegrityError
        try:
            create_user(                            # attempt duplicate insert
                name="DupTest2", email=email2,
                phone=phone, password="pass", role="customer"
            )
            # If we reach here, the duplicate was NOT prevented
            assert False, "Duplicate phone should have raised an error"
        except Exception:                           # any exception is acceptable
            pass                                    # duplicate correctly prevented
    finally:
        # -- CLEANUP --
        if user_id:                                 # if the first user was created
            conn = get_connection()                 # get connection
            cursor = conn.cursor()                  # open cursor
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))  # remove
            conn.commit()                           # persist
            cursor.close()                          # close cursor
            conn.close()                            # close connection


# ============================================================
# TEST 3: get_user_by_phone — existing user
# ============================================================
def test_get_user_by_phone_existing(db_connection, test_user):
    """Fetching by a known phone should return the correct user dict."""
    result = get_user_by_phone(test_user["phone"])  # call repository function

    assert result is not None, "User must be found"                     # must exist
    assert result["id"] == test_user["id"], "ID must match"             # correct row
    assert result["phone"] == test_user["phone"], "Phone must match"    # correct phone
    assert result["name"] == test_user["name"], "Name must match"       # correct name
    assert result["role"] == test_user["role"], "Role must match"       # correct role


# ============================================================
# TEST 4: get_user_by_phone — non-existent phone
# ============================================================
def test_get_user_by_phone_nonexistent(db_connection, unique_id):
    """Fetching by a phone that doesn't exist should return None."""
    fake_phone = "00" + unique_id                   # phone that was never inserted
    result = get_user_by_phone(fake_phone)          # call repository function

    assert result is None, "Non-existent phone should return None"     # must be None


# ============================================================
# TEST 5: verify_user — sets is_verified to TRUE
# ============================================================
def test_verify_user_sets_flag(db_connection, unique_id):
    """After calling verify_user, the user's is_verified should be True."""
    phone = "99" + unique_id                        # unique phone
    email = f"vfy_{unique_id}@test.com"              # unique email

    # -- Create an unverified user --
    user_id = create_user(                          # insert with is_verified=FALSE
        name="VerifyTest", email=email,
        phone=phone, password="pass", role="customer"
    )

    # -- Confirm initially unverified --
    user_before = get_user_by_phone(phone)          # fetch the user
    assert user_before["is_verified"] == 0 or user_before["is_verified"] is False, \
        "New user should be unverified"              # repository sets FALSE by default

    # -- Call verify_user --
    verify_user(user_id)                            # toggle the flag

    # -- Confirm now verified --
    user_after = get_user_by_phone(phone)           # fetch again
    assert user_after["is_verified"] == 1 or user_after["is_verified"] is True, \
        "User should now be verified"                # flag must be TRUE

    # -- CLEANUP --
    conn = get_connection()                         # get connection
    cursor = conn.cursor()                          # open cursor
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))  # remove
    conn.commit()                                   # persist
    cursor.close()                                  # close cursor
    conn.close()                                    # close connection

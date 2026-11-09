# tests/conftest.py
# ============================================================
# Central pytest configuration and shared fixtures.
# This file is auto-loaded by pytest before every test session.
# It provides:
#   - A real MySQL database connection fixture
#   - Reusable test-data fixtures (user, service, professional, slot)
#   - Automatic cleanup so tests never pollute each other
# ============================================================

import sys                                      # needed to modify the Python import path
import os                                       # needed for path manipulation
import pytest                                   # the test framework itself
import mysql.connector                          # MySQL driver for Python
from mysql.connector import Error               # specific error class for DB errors

# ---------------------------------------------------------------------------
# PATH SETUP — ensure the project root is on sys.path so that imports like
# `from repositories.user_repository import ...` work from inside tests/.
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.abspath(                 # resolve to absolute path
    os.path.join(os.path.dirname(__file__), "..")  # go one level up from tests/
)
if PROJECT_ROOT not in sys.path:                # avoid duplicate entries
    sys.path.insert(0, PROJECT_ROOT)            # prepend so project modules take priority


# ============================================================
# FIXTURE: db_connection
# Scope: function (each test gets a fresh connection)
# Provides a live MySQL connection to the `workbuddy` database.
# Automatically closes the connection after the test finishes.
# ============================================================
from database.db import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

@pytest.fixture()
def db_connection():
    """Yield a live MySQL connection; close it after the test."""
    conn = None                                 # initialise to None for safety
    try:
        conn = mysql.connector.connect(         # open a real connection
            host=DB_HOST,                       # database host from config
            user=DB_USER,                       # database user from config
            password=DB_PASSWORD,               # database password from config
            database=DB_NAME                    # target database name from config
        )
        yield conn                              # hand the connection to the test
    except Error as e:                          # catch any connection errors
        pytest.fail(f"Database connection failed: {e}")  # fail the test clearly
    finally:
        if conn and conn.is_connected():        # if the connection is still open
            conn.close()                        # close it to free resources


# ============================================================
# FIXTURE: unique_id
# Generate collision-free IDs via pytest native context.
# This prevents UNIQUE constraint violations across test runs.
# ============================================================
@pytest.fixture()
def unique_id(request):
    """Provides a unique 8-character string for test data generation using pytest context."""
    # Generate a positive hash based on the exact pytest nodeid
    # ensuring collision-free data per test without external libraries like uuid
    return str(abs(hash(request.node.nodeid)))[:8].zfill(8)


# ============================================================
# FIXTURE: test_user
# Creates a fresh 'customer' user in the database.
# Yields the user dict (including the auto-generated `id`).
# Deletes the user row after the test completes (CASCADE handles children).
# ============================================================
@pytest.fixture()
def test_user(db_connection, unique_id):
    """Insert a test customer user and clean up after use."""
    conn = db_connection                        # reuse the connection fixture
    cursor = conn.cursor(dictionary=True)       # dictionary cursor for named access

    # -- Generate unique values to avoid UNIQUE constraint clashes --
    phone = "99" + unique_id                     # unique phone number
    email = f"test_{unique_id}@workbuddy.test"   # unique email address
    name = f"TestUser_{unique_id}"               # readable but unique name
    password = "testpass123"                     # plain-text password (matches project style)
    role = "customer"                           # role for a normal customer

    # -- INSERT the user row --
    cursor.execute(
        """
        INSERT INTO users (name, email, phone, password, role, is_verified)
        VALUES (%s, %s, %s, %s, %s, TRUE)
        """,
        (name, email, phone, password, role)    # parameterised to prevent SQL injection
    )
    conn.commit()                               # persist the insert
    user_id = cursor.lastrowid                  # capture the auto-generated ID

    # -- Build a dict that mirrors what repository functions return --
    user = {
        "id": user_id,                          # primary key
        "name": name,                           # user's display name
        "email": email,                         # user's email
        "phone": phone,                         # user's phone (unique)
        "password": password,                   # stored password
        "role": role,                           # enum role
        "is_verified": True                     # pre-verified for convenience
    }

    yield user                                  # provide user dict to the test

    # -- CLEANUP: delete the user (CASCADE removes OTPs, bookings, etc.) --
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    conn.commit()                               # persist the deletion
    cursor.close()                              # free the cursor


# ============================================================
# FIXTURE: test_service
# Creates a service row (e.g. "Plumbing") for tests to reference.
# Yields the service dict.  Cleaned up after the test.
# ============================================================
@pytest.fixture()
def test_service(db_connection, unique_id):
    """Insert a test service and clean up after use."""
    conn = db_connection                        # reuse the connection fixture
    cursor = conn.cursor(dictionary=True)       # dictionary cursor

    # -- Unique service name to avoid duplicates --
    service_name = f"TestService_{unique_id}"   # unique name
    description = "Automated test service"             # human-readable description
    base_price = 500.00                                # sample price
    estimated_time = "1 hour"                          # sample duration

    # -- INSERT the service row --
    cursor.execute(
        """
        INSERT INTO services (name, description, base_price, estimated_time)
        VALUES (%s, %s, %s, %s)
        """,
        (service_name, description, base_price, estimated_time)
    )
    conn.commit()                               # persist the insert
    service_id = cursor.lastrowid               # capture auto-generated ID

    # -- Build a dict matching repository output --
    service = {
        "id": service_id,                       # primary key
        "name": service_name,                   # service name
        "description": description,             # service description
        "base_price": base_price,               # base pricing
        "estimated_time": estimated_time        # time estimate string
    }

    yield service                               # provide to the test

    # -- CLEANUP: remove the service row (CASCADE removes professional_services) --
    cursor.execute("DELETE FROM services WHERE id = %s", (service_id,))
    conn.commit()                               # persist deletion
    cursor.close()                              # free cursor


# ============================================================
# FIXTURE: test_professional
# Creates a user with role='professional', then a professionals row.
# Also approves the professional so booking tests can use them.
# Yields a dict with both user-level and professional-level data.
# Cleans up both rows after the test (user CASCADE handles it).
# ============================================================
@pytest.fixture()
def test_professional(db_connection, unique_id):
    """Insert a test professional (approved) and clean up after use."""
    conn = db_connection                        # reuse the connection fixture
    cursor = conn.cursor(dictionary=True)       # dictionary cursor

    # -- Create the underlying user account --
    phone = "88" + unique_id                    # unique phone
    email = f"pro_{unique_id}@workbuddy.test"   # unique email
    name = f"TestPro_{unique_id}"               # unique name
    password = "propass123"                      # password
    role = "professional"                        # role

    cursor.execute(
        """
        INSERT INTO users (name, email, phone, password, role, is_verified)
        VALUES (%s, %s, %s, %s, %s, TRUE)
        """,
        (name, email, phone, password, role)
    )
    conn.commit()                               # persist user insert
    user_id = cursor.lastrowid                  # capture user ID

    # -- Create the professionals profile row --
    experience = 5                              # years of experience
    area = "TestCity"                            # service area
    work_radius = 10                            # radius in km

    cursor.execute(
        """
        INSERT INTO professionals (user_id, experience, area, work_radius, is_approved)
        VALUES (%s, %s, %s, %s, TRUE)
        """,
        (user_id, experience, area, work_radius)
    )
    conn.commit()                               # persist professional insert
    professional_id = cursor.lastrowid          # capture professional ID

    # -- Build comprehensive dict --
    professional = {
        "id": professional_id,                  # professionals.id
        "user_id": user_id,                     # users.id (FK)
        "name": name,                           # display name
        "email": email,                         # email
        "phone": phone,                         # phone
        "password": password,                   # password
        "role": role,                           # role string
        "experience": experience,               # years
        "area": area,                           # city
        "work_radius": work_radius,             # km
        "is_approved": True                     # pre-approved for testing
    }

    yield professional                          # provide to the test

    # -- CLEANUP: deleting the user cascades to professionals, slots, bookings --
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    conn.commit()                               # persist deletion
    cursor.close()                              # free cursor


# ============================================================
# FIXTURE: test_slot
# Creates a time slot for a given professional.
# Depends on test_professional so the FK is satisfied.
# Yields the slot dict.  Cleaned up after the test.
# ============================================================
@pytest.fixture()
def test_slot(db_connection, test_professional):
    """Insert a test time slot linked to test_professional, clean up after use."""
    conn = db_connection                        # reuse the connection fixture
    cursor = conn.cursor(dictionary=True)       # dictionary cursor

    professional_id = test_professional["id"]   # FK to professionals table
    slot_date = "2026-12-31"                    # far-future date to avoid collisions
    start_time = "10:00:00"                     # start time
    end_time = "11:00:00"                       # end time

    # -- INSERT the time slot --
    cursor.execute(
        """
        INSERT INTO time_slots (professional_id, slot_date, start_time, end_time, is_booked)
        VALUES (%s, %s, %s, %s, FALSE)
        """,
        (professional_id, slot_date, start_time, end_time)
    )
    conn.commit()                               # persist insert
    slot_id = cursor.lastrowid                  # capture auto-generated ID

    # -- Build dict matching repository output --
    slot = {
        "id": slot_id,                          # primary key
        "professional_id": professional_id,     # FK
        "slot_date": slot_date,                 # date string
        "start_time": start_time,               # time string
        "end_time": end_time,                   # time string
        "is_booked": False                      # initially available
    }

    yield slot                                  # provide to the test

    # -- CLEANUP: remove the slot row --
    cursor.execute("DELETE FROM time_slots WHERE id = %s", (slot_id,))
    conn.commit()                               # persist deletion
    cursor.close()                              # free cursor


# ============================================================
# FIXTURE: test_professional_with_service
# Combines test_professional + test_service and links them via
# the professional_services bridge table.
# Yields a dict containing both professional and service info.
# ============================================================
@pytest.fixture()
def test_professional_with_service(db_connection, test_professional, test_service):
    """Link test_professional to test_service via professional_services."""
    conn = db_connection                        # reuse the connection fixture
    cursor = conn.cursor(dictionary=True)       # dictionary cursor

    custom_price = 750.00                       # custom price for this pro+service combo

    # -- INSERT the bridge row --
    cursor.execute(
        """
        INSERT INTO professional_services (professional_id, service_id, custom_price)
        VALUES (%s, %s, %s)
        """,
        (test_professional["id"], test_service["id"], custom_price)
    )
    conn.commit()                               # persist the link
    ps_id = cursor.lastrowid                    # capture bridge row ID

    # -- Build a combined dict --
    data = {
        "professional": test_professional,      # full professional dict
        "service": test_service,                # full service dict
        "custom_price": custom_price,           # the custom price
        "ps_id": ps_id                          # bridge row ID (for cleanup)
    }

    yield data                                  # provide to the test

    # -- CLEANUP: remove the bridge row --
    cursor.execute("DELETE FROM professional_services WHERE id = %s", (ps_id,))
    conn.commit()                               # persist deletion
    cursor.close()                              # free cursor

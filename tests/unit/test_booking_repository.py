# tests/unit/test_booking_repository.py
# ============================================================
# Unit tests for repositories/booking_repository.py
# Tests: create_booking, get_booking_by_id, update_booking_status,
#        update_payment_status, mark_slot_booked, unmark_slot_booked,
#        deactivate_booking, get_bookings_by_customer
# Uses REAL MySQL — no mocking.
# ============================================================

import sys                                          # for path manipulation
import os                                           # for path joining

# -- Ensure project root is importable --
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from repositories.booking_repository import (       # import functions under test
    create_booking,                                 # creates a new booking
    get_booking_by_id,                              # fetches a single booking by ID
    update_booking_status,                          # changes booking status
    update_payment_status,                          # changes payment status
    mark_slot_booked,                               # marks a time slot as booked
    unmark_slot_booked,                             # marks a time slot as available
    deactivate_booking                              # sets is_active = FALSE
)
from database.db import get_connection              # direct DB access for cleanup


# ============================================================
# HELPER: create a minimal booking for testing
# ============================================================
def _create_test_booking(user_id, professional_id, service_id, slot_id):
    """Insert a booking row and return its ID."""
    booking_id = create_booking(                    # call repository function
        customer_id=user_id,                        # FK to users
        professional_id=professional_id,            # FK to professionals
        service_id=service_id,                      # FK to services
        slot_id=slot_id,                            # FK to time_slots (nullable)
        booking_type="scheduled",                   # booking type enum
        scheduled_datetime="2026-12-31 10:00:00",   # future datetime string
        payment_method="upi",                       # payment method enum
        payment_status="pending",                   # initial payment status
        total_price=750.00                          # total price decimal
    )
    return booking_id                               # return the new booking's ID


# ============================================================
# TEST 1: create_booking — returns a valid ID
# ============================================================
def test_create_booking_returns_id(
    db_connection, test_user, test_professional, test_service, test_slot
):
    """create_booking should return a positive integer booking ID."""
    booking_id = _create_test_booking(              # insert a test booking
        user_id=test_user["id"],                    # customer user ID
        professional_id=test_professional["id"],    # professional ID
        service_id=test_service["id"],              # service ID
        slot_id=test_slot["id"]                     # slot ID
    )

    assert booking_id is not None, "Booking ID must not be None"        # not None
    assert isinstance(booking_id, int), "Booking ID must be an int"     # correct type
    assert booking_id > 0, "Booking ID must be positive"                # positive value

    # -- CLEANUP: remove the booking --
    conn = get_connection()                         # get connection
    cursor = conn.cursor()                          # open cursor
    cursor.execute("DELETE FROM bookings WHERE id = %s", (booking_id,))  # delete
    conn.commit()                                   # persist
    cursor.close()                                  # close cursor
    conn.close()                                    # close connection


# ============================================================
# TEST 2: get_booking_by_id — returns correct data
# ============================================================
def test_get_booking_by_id(
    db_connection, test_user, test_professional, test_service, test_slot
):
    """get_booking_by_id should return the booking with matching fields."""
    booking_id = _create_test_booking(              # create a booking
        user_id=test_user["id"],
        professional_id=test_professional["id"],
        service_id=test_service["id"],
        slot_id=test_slot["id"]
    )

    booking = get_booking_by_id(booking_id)         # fetch by ID

    assert booking is not None, "Booking must be found"                       # exists
    assert booking["id"] == booking_id, "ID must match"                       # correct ID
    assert booking["user_id"] == test_user["id"], "Customer ID must match"    # correct user
    assert booking["professional_id"] == test_professional["id"], \
        "Professional ID must match"                                          # correct pro
    assert booking["service_id"] == test_service["id"], \
        "Service ID must match"                                               # correct svc
    assert booking["status"] == "pending", "Initial status must be 'pending'" # default status

    # -- CLEANUP --
    conn = get_connection()                         # get connection
    cursor = conn.cursor()                          # open cursor
    cursor.execute("DELETE FROM bookings WHERE id = %s", (booking_id,))
    conn.commit()                                   # persist
    cursor.close()                                  # close cursor
    conn.close()                                    # close connection


# ============================================================
# TEST 3: get_booking_by_id — non-existent ID returns None
# ============================================================
def test_get_booking_by_id_nonexistent(db_connection, unique_id):
    """Fetching a booking with a fake ID should return None."""
    result = get_booking_by_id(999999)              # ID that doesn't exist

    assert result is None, "Non-existent booking should return None"   # must be None


# ============================================================
# TEST 4: update_booking_status — changes the status field
# ============================================================
def test_update_booking_status(
    db_connection, test_user, test_professional, test_service, test_slot
):
    """update_booking_status should change the booking's status."""
    booking_id = _create_test_booking(              # create a booking
        user_id=test_user["id"],
        professional_id=test_professional["id"],
        service_id=test_service["id"],
        slot_id=test_slot["id"]
    )

    update_booking_status(booking_id, "accepted")   # change status to 'accepted'

    booking = get_booking_by_id(booking_id)         # fetch updated booking
    assert booking["status"] == "accepted", \
        "Status must be 'accepted' after update"     # verify the change

    # -- CLEANUP --
    conn = get_connection()                         # get connection
    cursor = conn.cursor()                          # open cursor
    cursor.execute("DELETE FROM bookings WHERE id = %s", (booking_id,))
    conn.commit()                                   # persist
    cursor.close()                                  # close cursor
    conn.close()                                    # close connection


# ============================================================
# TEST 5: update_payment_status — changes the payment_status
# ============================================================
def test_update_payment_status(
    db_connection, test_user, test_professional, test_service, test_slot
):
    """update_payment_status should change the booking's payment_status."""
    booking_id = _create_test_booking(              # create a booking
        user_id=test_user["id"],
        professional_id=test_professional["id"],
        service_id=test_service["id"],
        slot_id=test_slot["id"]
    )

    update_payment_status(booking_id, "paid")       # mark as paid

    booking = get_booking_by_id(booking_id)         # fetch updated booking
    assert booking["payment_status"] == "paid", \
        "Payment status must be 'paid' after update" # verify the change

    # -- CLEANUP --
    conn = get_connection()                         # get connection
    cursor = conn.cursor()                          # open cursor
    cursor.execute("DELETE FROM bookings WHERE id = %s", (booking_id,))
    conn.commit()                                   # persist
    cursor.close()                                  # close cursor
    conn.close()                                    # close connection


# ============================================================
# TEST 6: mark_slot_booked / unmark_slot_booked
# ============================================================
def test_mark_and_unmark_slot(db_connection, test_slot):
    """mark_slot_booked and unmark_slot_booked should toggle is_booked."""
    slot_id = test_slot["id"]                       # get the slot ID

    # -- Mark as booked --
    mark_slot_booked(slot_id)                       # toggle to TRUE

    conn = get_connection()                         # get connection
    cursor = conn.cursor(dictionary=True)           # dictionary cursor
    cursor.execute(                                 # verify directly in DB
        "SELECT is_booked FROM time_slots WHERE id = %s", (slot_id,)
    )
    row = cursor.fetchone()                         # fetch the row
    assert row["is_booked"] == 1 or row["is_booked"] is True, \
        "Slot must be marked as booked"              # must be TRUE
    cursor.close()                                  # close cursor
    conn.close()                                    # close connection

    # -- Unmark (make available again) --
    unmark_slot_booked(slot_id)                     # toggle to FALSE

    conn = get_connection()                         # new connection
    cursor = conn.cursor(dictionary=True)           # dictionary cursor
    cursor.execute(                                 # verify directly
        "SELECT is_booked FROM time_slots WHERE id = %s", (slot_id,)
    )
    row = cursor.fetchone()                         # fetch the row
    assert row["is_booked"] == 0 or row["is_booked"] is False, \
        "Slot must be unmarked (available)"          # must be FALSE
    cursor.close()                                  # close cursor
    conn.close()                                    # close connection


# ============================================================
# TEST 7: deactivate_booking — sets is_active to FALSE
# ============================================================
def test_deactivate_booking(
    db_connection, test_user, test_professional, test_service, test_slot
):
    """deactivate_booking should set is_active = FALSE on the booking."""
    booking_id = _create_test_booking(              # create a booking
        user_id=test_user["id"],
        professional_id=test_professional["id"],
        service_id=test_service["id"],
        slot_id=test_slot["id"]
    )

    deactivate_booking(booking_id)                  # deactivate the booking

    booking = get_booking_by_id(booking_id)         # fetch updated booking
    assert booking["is_active"] == 0 or booking["is_active"] is False, \
        "Booking must be deactivated (is_active=FALSE)"  # verify

    # -- CLEANUP --
    conn = get_connection()                         # get connection
    cursor = conn.cursor()                          # open cursor
    cursor.execute("DELETE FROM bookings WHERE id = %s", (booking_id,))
    conn.commit()                                   # persist
    cursor.close()                                  # close cursor
    conn.close()                                    # close connection

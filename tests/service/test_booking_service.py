# tests/service/test_booking_service.py
# ============================================================
# Service-layer tests for services/booking_service.py
# Tests: create_booking, cancel_booking, accept_booking,
#        reject_booking, complete_booking, state transitions
# Uses REAL MySQL — no mocking.
# ============================================================

import sys                                          # for path manipulation
import os                                           # for path joining

# -- Ensure project root is importable --
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from services.booking_service import (              # import service functions
    create_booking,                                 # creates a new booking
    cancel_booking,                                 # cancels a booking
    accept_booking,                                 # accepts a pending booking
    reject_booking,                                 # rejects a pending booking
    complete_booking,                               # completes an accepted booking
    get_available_slots_for_professional            # fetches available slots
)
from repositories.booking_repository import (       # direct repo access for verification
    get_booking_by_id                               # fetch booking for assertions
)
from repositories.time_slot_repository import (     # slot operations
    get_slot_by_id                                  # check slot booking state
)
from database.db import get_connection              # direct DB access for cleanup


# ============================================================
# HELPER: clean up a booking (and its invoice if any)
# ============================================================
def _cleanup_booking(booking_id):
    """Delete a booking and related invoices from the database."""
    conn = get_connection()                         # get connection
    cursor = conn.cursor()                          # open cursor
    # Delete invoices first (FK constraint)
    cursor.execute("DELETE FROM invoices WHERE booking_id = %s", (booking_id,))
    # Now delete the booking itself
    cursor.execute("DELETE FROM bookings WHERE id = %s", (booking_id,))
    conn.commit()                                   # persist
    cursor.close()                                  # close cursor
    conn.close()                                    # close connection


# ============================================================
# TEST 1: create_booking (scheduled) — success
# ============================================================
def test_create_booking_scheduled_success(
    db_connection, test_user, test_professional_with_service, test_slot
):
    """A scheduled booking with a valid slot should succeed."""
    pro = test_professional_with_service["professional"]   # professional dict
    svc = test_professional_with_service["service"]        # service dict

    booking_id = create_booking(                    # call service function
        customer_id=test_user["id"],                # customer's user ID
        professional_id=pro["id"],                  # professional's ID
        service_id=svc["id"],                       # service ID
        booking_type="scheduled",                   # scheduled type
        payment_method="upi",                       # payment method
        total_price=750.00,                         # total price
        slot_id=test_slot["id"]                     # specific time slot
    )

    assert booking_id is not None, "Booking ID must not be None"        # not None
    assert isinstance(booking_id, int), "Booking ID must be an integer" # correct type

    # -- Verify booking exists --
    booking = get_booking_by_id(booking_id)         # fetch the booking
    assert booking is not None, "Booking must exist in DB"              # exists
    assert booking["status"] == "pending", "Initial status must be 'pending'"  # default
    assert booking["booking_type"] == "scheduled", "Booking type must be 'scheduled'"
    assert float(booking["total_price"]) == 750.00, "Total price must match"

    # -- Verify slot is now booked --
    slot = get_slot_by_id(test_slot["id"])           # fetch the slot
    assert slot["is_booked"] == 1 or slot["is_booked"] is True, \
        "Slot must be marked as booked"              # slot should be locked

    # -- CLEANUP --
    _cleanup_booking(booking_id)                    # remove booking


# ============================================================
# TEST 2: cancel_booking — customer cancels pending booking
# ============================================================
def test_cancel_booking_success(
    db_connection, test_user, test_professional_with_service, test_slot
):
    """A customer should be able to cancel their own pending booking."""
    pro = test_professional_with_service["professional"]
    svc = test_professional_with_service["service"]

    booking_id = create_booking(                    # create a booking first
        customer_id=test_user["id"],
        professional_id=pro["id"],
        service_id=svc["id"],
        booking_type="scheduled",
        payment_method="cash",
        total_price=500.00,
        slot_id=test_slot["id"]
    )

    success, message = cancel_booking(              # cancel the booking
        booking_id=booking_id,                      # booking to cancel
        user_id=test_user["id"]                     # the cancelling user
    )

    assert success is True, f"Cancel must succeed: {message}"        # must succeed
    assert "cancelled" in message.lower(), "Message must mention cancellation"

    # -- Verify booking status is cancelled --
    booking = get_booking_by_id(booking_id)         # fetch booking
    assert booking["status"] == "cancelled", "Status must be 'cancelled'"

    # -- Verify slot is freed --
    slot = get_slot_by_id(test_slot["id"])           # fetch slot
    assert slot["is_booked"] == 0 or slot["is_booked"] is False, \
        "Slot must be freed after cancellation"

    # -- CLEANUP --
    _cleanup_booking(booking_id)


# ============================================================
# TEST 3: cancel_booking — unauthorized user cannot cancel
# ============================================================
def test_cancel_booking_unauthorized(
    db_connection, test_user, test_professional_with_service, test_slot
):
    """A different user should NOT be able to cancel someone else's booking."""
    pro = test_professional_with_service["professional"]
    svc = test_professional_with_service["service"]

    booking_id = create_booking(                    # create booking
        customer_id=test_user["id"],
        professional_id=pro["id"],
        service_id=svc["id"],
        booking_type="scheduled",
        payment_method="upi",
        total_price=500.00,
        slot_id=test_slot["id"]
    )

    success, message = cancel_booking(              # attempt cancel with wrong user
        booking_id=booking_id,
        user_id=999999                              # fake user ID (not the owner)
    )

    assert success is False, "Unauthorized cancel must fail"  # must fail

    # -- CLEANUP --
    _cleanup_booking(booking_id)


# ============================================================
# TEST 4: accept_booking — professional accepts pending booking
# ============================================================
def test_accept_booking_success(
    db_connection, test_user, test_professional_with_service, test_slot
):
    """A professional should be able to accept a pending booking."""
    pro = test_professional_with_service["professional"]
    svc = test_professional_with_service["service"]

    booking_id = create_booking(                    # create a pending booking
        customer_id=test_user["id"],
        professional_id=pro["id"],
        service_id=svc["id"],
        booking_type="scheduled",
        payment_method="upi",
        total_price=500.00,
        slot_id=test_slot["id"]
    )

    success, message = accept_booking(              # accept the booking
        booking_id=booking_id,
        professional_id=pro["id"]                   # must be the assigned professional
    )

    assert success is True, f"Accept must succeed: {message}"  # must succeed

    booking = get_booking_by_id(booking_id)         # verify status
    assert booking["status"] == "accepted", "Status must be 'accepted'"

    # -- CLEANUP --
    _cleanup_booking(booking_id)


# ============================================================
# TEST 5: reject_booking — professional rejects pending booking
# ============================================================
def test_reject_booking_success(
    db_connection, test_user, test_professional_with_service, test_slot
):
    """A professional should be able to reject a pending booking."""
    pro = test_professional_with_service["professional"]
    svc = test_professional_with_service["service"]

    booking_id = create_booking(                    # create a pending booking
        customer_id=test_user["id"],
        professional_id=pro["id"],
        service_id=svc["id"],
        booking_type="scheduled",
        payment_method="cash",
        total_price=500.00,
        slot_id=test_slot["id"]
    )

    success, message = reject_booking(              # reject the booking
        booking_id=booking_id,
        professional_id=pro["id"]
    )

    assert success is True, f"Reject must succeed: {message}"  # must succeed

    booking = get_booking_by_id(booking_id)         # verify status
    assert booking["status"] == "rejected", "Status must be 'rejected'"

    # -- Verify slot is freed --
    slot = get_slot_by_id(test_slot["id"])
    assert slot["is_booked"] == 0 or slot["is_booked"] is False, \
        "Slot must be freed after rejection"

    # -- CLEANUP --
    _cleanup_booking(booking_id)


# ============================================================
# TEST 6: complete_booking — professional completes accepted booking
# ============================================================
def test_complete_booking_success(
    db_connection, test_user, test_professional_with_service, test_slot
):
    """A professional should be able to complete an accepted booking."""
    pro = test_professional_with_service["professional"]
    svc = test_professional_with_service["service"]

    booking_id = create_booking(                    # create a pending booking
        customer_id=test_user["id"],
        professional_id=pro["id"],
        service_id=svc["id"],
        booking_type="scheduled",
        payment_method="upi",
        total_price=500.00,
        slot_id=test_slot["id"]
    )

    # -- First accept the booking (required before completion) --
    accept_booking(booking_id, pro["id"])            # transition: pending → accepted

    # -- Then complete it --
    success, message = complete_booking(            # transition: accepted → completed
        booking_id=booking_id,
        professional_id=pro["id"]
    )

    assert success is True, f"Complete must succeed: {message}"  # must succeed

    booking = get_booking_by_id(booking_id)         # verify status
    assert booking["status"] == "completed", "Status must be 'completed'"

    # -- CLEANUP --
    _cleanup_booking(booking_id)


# ============================================================
# TEST 7: invalid state transition — cannot complete a pending booking
# ============================================================
def test_complete_booking_invalid_transition(
    db_connection, test_user, test_professional_with_service, test_slot
):
    """Completing a pending booking (without accepting first) should fail."""
    pro = test_professional_with_service["professional"]
    svc = test_professional_with_service["service"]

    booking_id = create_booking(                    # create a pending booking
        customer_id=test_user["id"],
        professional_id=pro["id"],
        service_id=svc["id"],
        booking_type="scheduled",
        payment_method="cash",
        total_price=500.00,
        slot_id=test_slot["id"]
    )

    # -- Try to complete directly (skipping accept) --
    success, message = complete_booking(
        booking_id=booking_id,
        professional_id=pro["id"]
    )

    assert success is False, "Completing a pending booking must fail"  # invalid transition

    # -- CLEANUP --
    _cleanup_booking(booking_id)


# ============================================================
# TEST 8: double booking — slot already booked
# ============================================================
def test_slot_already_booked_after_booking(
    db_connection, test_user, test_professional_with_service, test_slot
):
    """After a booking, the slot should be marked as booked."""
    pro = test_professional_with_service["professional"]
    svc = test_professional_with_service["service"]

    booking_id = create_booking(                    # create a booking that claims the slot
        customer_id=test_user["id"],
        professional_id=pro["id"],
        service_id=svc["id"],
        booking_type="scheduled",
        payment_method="upi",
        total_price=500.00,
        slot_id=test_slot["id"]
    )

    # -- Verify the slot is now booked --
    slot = get_slot_by_id(test_slot["id"])
    assert slot["is_booked"] == 1 or slot["is_booked"] is True, \
        "Slot must be booked after first booking"

    # -- Available slots should NOT include this slot --
    available = get_available_slots_for_professional(pro["id"])
    available_ids = [s["id"] for s in available]    # collect available slot IDs

    assert test_slot["id"] not in available_ids, \
        "Booked slot must not appear in available slots"  # must be excluded

    # -- CLEANUP --
    _cleanup_booking(booking_id)

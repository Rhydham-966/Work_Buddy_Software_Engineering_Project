"""
test_booking.py — Comprehensive tests for the Booking Service layer.

Covers:
    - is_valid_transition() — full 25+ transition matrix
    - Booking creation (immediate/scheduled, with/without slots)
    - Booking lifecycle (accept, reject, complete, cancel)
    - Authorization checks (wrong user / wrong professional)
    - Non-existent booking operations
    - Slot locking and liberation
    - Edge cases (None booking, double operations)

Database-dependent (uses live MySQL via test_utils).
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from services.booking_service import (
    is_valid_transition,
    create_booking,
    accept_booking,
    reject_booking,
    complete_booking,
    cancel_booking,
    get_customer_bookings,
    get_customer_history,
    get_available_slots_for_professional,
)
from repositories.booking_repository import get_booking_by_id
from repositories.time_slot_repository import get_slot_by_id
from services.professional_service import add_slot
from tests.test_utils import (
    clear_test_data,
    create_raw_test_user,
    create_test_service,
    create_test_professional,
)


# ══════════════════════════════════════════════════════════
#  STATE MACHINE — is_valid_transition() pure logic tests
# ══════════════════════════════════════════════════════════
class TestStateTransitionMatrix(unittest.TestCase):
    """Exhaustive tests for the booking state machine.

    Legal transitions:
        pending  → accepted, rejected, cancelled
        accepted → completed
        completed, cancelled, rejected → (terminal, no transitions)
    """

    # ── LEGAL TRANSITIONS ──
    def test_pending_to_accepted_is_valid(self):
        self.assertTrue(is_valid_transition("pending", "accepted"))

    def test_pending_to_rejected_is_valid(self):
        self.assertTrue(is_valid_transition("pending", "rejected"))

    def test_pending_to_cancelled_is_valid(self):
        self.assertTrue(is_valid_transition("pending", "cancelled"))

    def test_accepted_to_completed_is_valid(self):
        self.assertTrue(is_valid_transition("accepted", "completed"))

    # ── ILLEGAL: FROM PENDING ──
    def test_pending_to_completed_is_illegal(self):
        self.assertFalse(is_valid_transition("pending", "completed"))

    def test_pending_to_pending_is_illegal(self):
        self.assertFalse(is_valid_transition("pending", "pending"))

    # ── ILLEGAL: FROM ACCEPTED ──
    def test_accepted_to_accepted_is_illegal(self):
        self.assertFalse(is_valid_transition("accepted", "accepted"))

    def test_accepted_to_rejected_is_illegal(self):
        self.assertFalse(is_valid_transition("accepted", "rejected"))

    def test_accepted_to_cancelled_is_illegal(self):
        self.assertFalse(is_valid_transition("accepted", "cancelled"))

    def test_accepted_to_pending_is_illegal(self):
        self.assertFalse(is_valid_transition("accepted", "pending"))

    # ── ILLEGAL: FROM COMPLETED (terminal) ──
    def test_completed_to_accepted_is_illegal(self):
        self.assertFalse(is_valid_transition("completed", "accepted"))

    def test_completed_to_rejected_is_illegal(self):
        self.assertFalse(is_valid_transition("completed", "rejected"))

    def test_completed_to_cancelled_is_illegal(self):
        self.assertFalse(is_valid_transition("completed", "cancelled"))

    def test_completed_to_pending_is_illegal(self):
        self.assertFalse(is_valid_transition("completed", "pending"))

    def test_completed_to_completed_is_illegal(self):
        self.assertFalse(is_valid_transition("completed", "completed"))

    # ── ILLEGAL: FROM CANCELLED (terminal) ──
    def test_cancelled_to_accepted_is_illegal(self):
        self.assertFalse(is_valid_transition("cancelled", "accepted"))

    def test_cancelled_to_rejected_is_illegal(self):
        self.assertFalse(is_valid_transition("cancelled", "rejected"))

    def test_cancelled_to_pending_is_illegal(self):
        self.assertFalse(is_valid_transition("cancelled", "pending"))

    def test_cancelled_to_completed_is_illegal(self):
        self.assertFalse(is_valid_transition("cancelled", "completed"))

    def test_cancelled_to_cancelled_is_illegal(self):
        self.assertFalse(is_valid_transition("cancelled", "cancelled"))

    # ── ILLEGAL: FROM REJECTED (terminal) ──
    def test_rejected_to_accepted_is_illegal(self):
        self.assertFalse(is_valid_transition("rejected", "accepted"))

    def test_rejected_to_pending_is_illegal(self):
        self.assertFalse(is_valid_transition("rejected", "pending"))

    def test_rejected_to_completed_is_illegal(self):
        self.assertFalse(is_valid_transition("rejected", "completed"))

    def test_rejected_to_cancelled_is_illegal(self):
        self.assertFalse(is_valid_transition("rejected", "cancelled"))

    def test_rejected_to_rejected_is_illegal(self):
        self.assertFalse(is_valid_transition("rejected", "rejected"))

    # ── UNKNOWN / EDGE CASES ──
    def test_unknown_current_status_returns_false(self):
        self.assertFalse(is_valid_transition("garbage", "accepted"))

    def test_none_current_status_returns_false(self):
        self.assertFalse(is_valid_transition(None, "accepted"))

    def test_empty_string_current_status_returns_false(self):
        self.assertFalse(is_valid_transition("", "accepted"))

    def test_case_sensitive_pending_uppercase_fails(self):
        """State machine is case-sensitive — 'PENDING' != 'pending'."""
        self.assertFalse(is_valid_transition("PENDING", "accepted"))

    def test_case_sensitive_new_status_uppercase_fails(self):
        self.assertFalse(is_valid_transition("pending", "ACCEPTED"))


# ══════════════════════════════════════════════════════════
#  BOOKING CREATION
# ══════════════════════════════════════════════════════════
class TestBookingCreation(unittest.TestCase):
    """Tests for create_booking with various booking types and slot scenarios."""

    def setUp(self):
        clear_test_data()
        self.customer = create_raw_test_user("BC1", "400")
        self.pro_user = create_raw_test_user("BP1", "401")
        self.pro_id = create_test_professional(self.pro_user['id'], is_approved=True)
        self.service_id = create_test_service("Test Service BC", 200.0)

    def tearDown(self):
        clear_test_data()

    def test_scheduled_booking_with_valid_slot(self):
        """Scheduled booking with a valid slot_id succeeds."""
        slot_id = add_slot(self.pro_id, "2026-10-01", "10:00", "11:00")
        bid = create_booking(
            self.customer['id'], self.pro_id, self.service_id,
            "scheduled", "cash", 200.0, slot_id=slot_id
        )
        self.assertIsNotNone(bid)
        booking = get_booking_by_id(bid)
        self.assertEqual(booking['status'], 'pending')
        self.assertEqual(booking['time_slot_id'], slot_id)

    def test_scheduled_booking_slot_gets_locked(self):
        """Creating a scheduled booking must mark the slot as booked."""
        slot_id = add_slot(self.pro_id, "2026-10-02", "10:00", "11:00")
        create_booking(
            self.customer['id'], self.pro_id, self.service_id,
            "scheduled", "upi", 200.0, slot_id=slot_id
        )
        slot = get_slot_by_id(slot_id)
        self.assertEqual(slot['is_booked'], 1)

    def test_scheduled_booking_without_slot_id(self):
        """Scheduled booking with slot_id=None proceeds without slot assignment."""
        bid = create_booking(
            self.customer['id'], self.pro_id, self.service_id,
            "scheduled", "cash", 200.0, slot_id=None
        )
        self.assertIsNotNone(bid)
        booking = get_booking_by_id(bid)
        self.assertIsNone(booking['time_slot_id'])

    def test_immediate_booking_with_available_slot(self):
        """Immediate booking auto-selects the first available slot."""
        slot_id = add_slot(self.pro_id, "2026-10-03", "09:00", "10:00")
        bid = create_booking(
            self.customer['id'], self.pro_id, self.service_id,
            "immediate", "upi", 200.0
        )
        self.assertIsNotNone(bid)
        booking = get_booking_by_id(bid)
        self.assertEqual(booking['time_slot_id'], slot_id)

    def test_immediate_booking_without_available_slot(self):
        """Immediate booking with no slots still creates booking (slot_id=None)."""
        bid = create_booking(
            self.customer['id'], self.pro_id, self.service_id,
            "immediate", "cash", 200.0
        )
        self.assertIsNotNone(bid)
        booking = get_booking_by_id(bid)
        self.assertIsNone(booking['time_slot_id'])

    def test_booking_initial_payment_status_is_pending(self):
        """All new bookings start with payment_status='pending'."""
        bid = create_booking(
            self.customer['id'], self.pro_id, self.service_id,
            "scheduled", "upi", 300.0
        )
        booking = get_booking_by_id(bid)
        self.assertEqual(booking['payment_status'], 'pending')


# ══════════════════════════════════════════════════════════
#  BOOKING LIFECYCLE (DB-backed)
# ══════════════════════════════════════════════════════════
class TestBookingLifecycle(unittest.TestCase):
    """End-to-end lifecycle: pending → accepted → completed."""

    def setUp(self):
        clear_test_data()
        self.customer = create_raw_test_user("BL1", "410")
        self.pro_user = create_raw_test_user("BL2", "411")
        self.pro_id = create_test_professional(self.pro_user['id'], is_approved=True)
        self.service_id = create_test_service("Test Service BL", 150.0)
        self.slot_id = add_slot(self.pro_id, "2026-10-10", "14:00", "15:00")
        self.booking_id = create_booking(
            self.customer['id'], self.pro_id, self.service_id,
            "scheduled", "cash", 150.0, slot_id=self.slot_id
        )

    def tearDown(self):
        clear_test_data()

    def test_full_lifecycle_pending_accepted_completed(self):
        """Happy path: pending → accepted → completed."""
        # Accept
        success, _ = accept_booking(self.booking_id, self.pro_id)
        self.assertTrue(success)
        self.assertEqual(get_booking_by_id(self.booking_id)['status'], 'accepted')

        # Complete
        success, _ = complete_booking(self.booking_id, self.pro_id)
        self.assertTrue(success)
        b = get_booking_by_id(self.booking_id)
        self.assertEqual(b['status'], 'completed')
        self.assertEqual(b['is_active'], 0)

    def test_cancel_from_pending(self):
        """Customer can cancel a pending booking."""
        success, msg = cancel_booking(self.booking_id, self.customer['id'])
        self.assertTrue(success)
        self.assertEqual(get_booking_by_id(self.booking_id)['status'], 'cancelled')

    def test_reject_from_pending(self):
        """Professional can reject a pending booking."""
        success, msg = reject_booking(self.booking_id, self.pro_id)
        self.assertTrue(success)
        self.assertEqual(get_booking_by_id(self.booking_id)['status'], 'rejected')

    def test_booking_deactivated_after_completion(self):
        """Completed booking must be set to is_active=False."""
        accept_booking(self.booking_id, self.pro_id)
        complete_booking(self.booking_id, self.pro_id)
        self.assertEqual(get_booking_by_id(self.booking_id)['is_active'], 0)

    def test_booking_deactivated_after_cancellation(self):
        """Cancelled booking must be set to is_active=False."""
        cancel_booking(self.booking_id, self.customer['id'])
        self.assertEqual(get_booking_by_id(self.booking_id)['is_active'], 0)

    def test_booking_deactivated_after_rejection(self):
        """Rejected booking must be set to is_active=False."""
        reject_booking(self.booking_id, self.pro_id)
        self.assertEqual(get_booking_by_id(self.booking_id)['is_active'], 0)


# ══════════════════════════════════════════════════════════
#  INVALID TRANSITIONS (DB-backed)
# ══════════════════════════════════════════════════════════
class TestBookingInvalidTransitions(unittest.TestCase):
    """Verify that illegal state jumps are blocked at the service layer."""

    def setUp(self):
        clear_test_data()
        self.customer = create_raw_test_user("BIT1", "420")
        self.pro_user = create_raw_test_user("BIT2", "421")
        self.pro_id = create_test_professional(self.pro_user['id'], is_approved=True)
        self.sid = create_test_service("Test Service BIT", 100.0)

    def tearDown(self):
        clear_test_data()

    def _create_booking(self):
        slot_id = add_slot(self.pro_id, "2026-11-01", "10:00", "11:00")
        return create_booking(
            self.customer['id'], self.pro_id, self.sid,
            "scheduled", "cash", 100.0, slot_id=slot_id
        )

    def test_cannot_complete_pending_booking(self):
        """pending → completed is illegal."""
        bid = self._create_booking()
        success, msg = complete_booking(bid, self.pro_id)
        self.assertFalse(success)
        self.assertIn("Cannot complete from", msg)

    def test_cannot_accept_cancelled_booking(self):
        """cancelled → accepted is illegal."""
        bid = self._create_booking()
        cancel_booking(bid, self.customer['id'])
        success, msg = accept_booking(bid, self.pro_id)
        self.assertFalse(success)

    def test_cannot_cancel_completed_booking(self):
        """completed → cancelled is illegal."""
        bid = self._create_booking()
        accept_booking(bid, self.pro_id)
        complete_booking(bid, self.pro_id)
        success, msg = cancel_booking(bid, self.customer['id'])
        self.assertFalse(success)

    def test_cannot_reject_accepted_booking(self):
        """accepted → rejected is illegal."""
        bid = self._create_booking()
        accept_booking(bid, self.pro_id)
        success, msg = reject_booking(bid, self.pro_id)
        self.assertFalse(success)

    def test_cannot_accept_completed_booking(self):
        """completed → accepted is illegal."""
        bid = self._create_booking()
        accept_booking(bid, self.pro_id)
        complete_booking(bid, self.pro_id)
        success, msg = accept_booking(bid, self.pro_id)
        self.assertFalse(success)

    def test_cannot_complete_rejected_booking(self):
        """rejected → completed is illegal."""
        bid = self._create_booking()
        reject_booking(bid, self.pro_id)
        success, msg = complete_booking(bid, self.pro_id)
        self.assertFalse(success)

    def test_cannot_cancel_rejected_booking(self):
        """rejected → cancelled is illegal."""
        bid = self._create_booking()
        reject_booking(bid, self.pro_id)
        success, msg = cancel_booking(bid, self.customer['id'])
        self.assertFalse(success)


# ══════════════════════════════════════════════════════════
#  AUTHORIZATION CHECKS
# ══════════════════════════════════════════════════════════
class TestBookingAuthorization(unittest.TestCase):
    """Verify that unauthorized users cannot manipulate bookings."""

    def setUp(self):
        clear_test_data()
        self.customer = create_raw_test_user("BA1", "430")
        self.pro_user = create_raw_test_user("BA2", "431")
        self.pro_id = create_test_professional(self.pro_user['id'], is_approved=True)
        self.other_user = create_raw_test_user("BA3", "432")
        self.other_pro_user = create_raw_test_user("BA4", "433")
        self.other_pro_id = create_test_professional(self.other_pro_user['id'], is_approved=True)
        self.sid = create_test_service("Test Service BA", 250.0)
        slot_id = add_slot(self.pro_id, "2026-10-20", "10:00", "11:00")
        self.booking_id = create_booking(
            self.customer['id'], self.pro_id, self.sid,
            "scheduled", "cash", 250.0, slot_id=slot_id
        )

    def tearDown(self):
        clear_test_data()

    def test_cancel_by_wrong_user_fails(self):
        """A user who didn't create the booking cannot cancel it."""
        success, msg = cancel_booking(self.booking_id, self.other_user['id'])
        self.assertFalse(success)
        self.assertIn("Unauthorized", msg)

    def test_accept_by_wrong_professional_fails(self):
        """A different professional cannot accept another's booking."""
        success, msg = accept_booking(self.booking_id, self.other_pro_id)
        self.assertFalse(success)

    def test_reject_by_wrong_professional_fails(self):
        """A different professional cannot reject another's booking."""
        success, msg = reject_booking(self.booking_id, self.other_pro_id)
        self.assertFalse(success)

    def test_complete_by_wrong_professional_fails(self):
        """A different professional cannot complete another's booking."""
        accept_booking(self.booking_id, self.pro_id)
        success, msg = complete_booking(self.booking_id, self.other_pro_id)
        self.assertFalse(success)

    def test_accept_nonexistent_booking_fails(self):
        """Accepting a booking that doesn't exist returns failure."""
        success, msg = accept_booking(99999, self.pro_id)
        self.assertFalse(success)

    def test_cancel_nonexistent_booking_fails(self):
        """Cancelling a booking that doesn't exist returns failure."""
        success, msg = cancel_booking(99999, self.customer['id'])
        self.assertFalse(success)
        self.assertIn("not found", msg)

    def test_complete_nonexistent_booking_fails(self):
        """Completing a booking that doesn't exist returns failure."""
        success, msg = complete_booking(99999, self.pro_id)
        self.assertFalse(success)

    def test_reject_nonexistent_booking_fails(self):
        """Rejecting a booking that doesn't exist returns failure."""
        success, msg = reject_booking(99999, self.pro_id)
        self.assertFalse(success)


# ══════════════════════════════════════════════════════════
#  SLOT LIBERATION
# ══════════════════════════════════════════════════════════
class TestSlotLiberation(unittest.TestCase):
    """Verify that slots are freed when bookings are cancelled or rejected."""

    def setUp(self):
        clear_test_data()
        self.customer = create_raw_test_user("SL1", "440")
        self.pro_user = create_raw_test_user("SL2", "441")
        self.pro_id = create_test_professional(self.pro_user['id'], is_approved=True)
        self.sid = create_test_service("Test Service SL", 300.0)

    def tearDown(self):
        clear_test_data()

    def test_slot_freed_on_cancel(self):
        """Cancelling a booking must unmark the slot as booked."""
        slot_id = add_slot(self.pro_id, "2026-12-01", "09:00", "10:00")
        bid = create_booking(
            self.customer['id'], self.pro_id, self.sid,
            "scheduled", "cash", 300.0, slot_id=slot_id
        )
        # Slot should be locked
        self.assertEqual(get_slot_by_id(slot_id)['is_booked'], 1)

        cancel_booking(bid, self.customer['id'])

        # Slot should be freed
        self.assertEqual(get_slot_by_id(slot_id)['is_booked'], 0)

    def test_slot_freed_on_reject(self):
        """Rejecting a booking must unmark the slot as booked."""
        slot_id = add_slot(self.pro_id, "2026-12-02", "09:00", "10:00")
        bid = create_booking(
            self.customer['id'], self.pro_id, self.sid,
            "scheduled", "upi", 300.0, slot_id=slot_id
        )
        self.assertEqual(get_slot_by_id(slot_id)['is_booked'], 1)

        reject_booking(bid, self.pro_id)

        self.assertEqual(get_slot_by_id(slot_id)['is_booked'], 0)

    def test_slot_not_freed_on_completion(self):
        """Completed bookings do NOT free the slot — the work was done."""
        slot_id = add_slot(self.pro_id, "2026-12-03", "09:00", "10:00")
        bid = create_booking(
            self.customer['id'], self.pro_id, self.sid,
            "scheduled", "cash", 300.0, slot_id=slot_id
        )
        accept_booking(bid, self.pro_id)
        complete_booking(bid, self.pro_id)

        # Slot stays booked (work was delivered in that time)
        self.assertEqual(get_slot_by_id(slot_id)['is_booked'], 1)

    def test_cancel_booking_without_slot_does_not_crash(self):
        """Cancelling a booking that has no slot assigned must not raise."""
        bid = create_booking(
            self.customer['id'], self.pro_id, self.sid,
            "scheduled", "cash", 300.0, slot_id=None
        )
        success, msg = cancel_booking(bid, self.customer['id'])
        self.assertTrue(success)


if __name__ == '__main__':
    unittest.main()
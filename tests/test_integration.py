"""
test_integration.py — End-to-end integration tests across all layers.

Covers:
    - Complete booking lifecycle (create → accept → complete) with dashboard sync
    - Cancel booking lifecycle with slot re-availability
    - Rejection flow with slot liberation verification
    - Immediate booking lifecycle
    - Immutability: service price change post-booking
    - Cross-dashboard data consistency (customer vs professional views)

Database-dependent (uses live MySQL via test_utils).
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from services.booking_service import (
    create_booking,
    accept_booking,
    complete_booking,
    cancel_booking,
    reject_booking,
    get_customer_bookings,
    get_customer_history,
    get_professional_bookings,
    get_professional_history,
)
from services.admin_service import approve_professional
from services.professional_service import add_slot
from services.payment_service import process_payment
from repositories.booking_repository import get_booking_by_id
from repositories.time_slot_repository import get_slot_by_id
from tests.test_utils import (
    clear_test_data,
    create_raw_test_user,
    create_test_professional,
    create_test_service,
)


class TestCompleteBookingFlow(unittest.TestCase):
    """Full lifecycle: register → approve → book → accept → complete."""

    def setUp(self):
        clear_test_data()

    def tearDown(self):
        clear_test_data()

    def test_flow_complete_booking_with_dashboard_sync(self):
        """Full happy path verifying cross-dashboard data consistency."""
        # Setup
        c = create_raw_test_user("IntC1", "2000")
        p = create_raw_test_user("IntP1", "2001")
        pid = create_test_professional(p['id'], is_approved=False)
        sid = create_test_service("INT SERVICE Complete", 100.0)

        # Admin approves
        approve_professional(pid)

        # Pro adds slot
        slot_id = add_slot(pid, "2026-10-10", "15:00", "16:00")

        # Customer books
        bid = create_booking(c['id'], pid, sid, "scheduled", "cash", 100.0, slot_id=slot_id)
        process_payment(bid, "cash", 100.0)

        # Verify both dashboards show active booking
        c_active = get_customer_bookings(c['id'])
        p_active = get_professional_bookings(pid)
        self.assertEqual(len(c_active), 1)
        self.assertEqual(len(p_active), 1)

        # Pro accepts
        accept_booking(bid, pid)
        c_active_synced = get_customer_bookings(c['id'])
        self.assertEqual(
            c_active_synced[0]['status'], 'accepted',
            "Customer active view must sync Professional's accept command"
        )

        # Pro completes
        complete_booking(bid, pid)

        # Verify removed from active on BOTH dashboards
        self.assertEqual(len(get_customer_bookings(c['id'])), 0)
        self.assertEqual(len(get_professional_bookings(pid)), 0)

        # Verify pushed to history on BOTH dashboards
        c_hist = get_customer_history(c['id'])
        p_hist = get_professional_history(pid)
        self.assertEqual(len(c_hist), 1)
        self.assertEqual(len(p_hist), 1)
        self.assertEqual(c_hist[0]['status'], 'completed')
        self.assertEqual(p_hist[0]['status'], 'completed')


class TestCancelBookingFlow(unittest.TestCase):
    """Cancel lifecycle with cross-dashboard verification."""

    def setUp(self):
        clear_test_data()

    def tearDown(self):
        clear_test_data()

    def test_flow_cancel_booking_with_dashboard_sync(self):
        """Customer cancels booking — stripped from active, moved to history."""
        c = create_raw_test_user("IntC2", "2010")
        p = create_raw_test_user("IntP2", "2011")
        pid = create_test_professional(p['id'], is_approved=True)
        sid = create_test_service("INT SERVICE Cancel", 150.0)
        slot_id = add_slot(pid, "2026-11-10", "10:00", "11:00")

        bid = create_booking(c['id'], pid, sid, "scheduled", "upi", 150.0, slot_id)
        process_payment(bid, "upi", 150.0)

        cancel_booking(bid, c['id'])

        # Stripped from active
        self.assertEqual(len(get_customer_bookings(c['id'])), 0)
        self.assertEqual(len(get_professional_bookings(pid)), 0)

        # Logged in history
        self.assertEqual(len(get_customer_history(c['id'])), 1)
        self.assertEqual(len(get_professional_history(pid)), 1)

    def test_cancel_releases_slot(self):
        """Cancelled booking must release the associated slot."""
        c = create_raw_test_user("IntC3", "2020")
        p = create_raw_test_user("IntP3", "2021")
        pid = create_test_professional(p['id'], is_approved=True)
        sid = create_test_service("INT SERVICE SlotCancel", 200.0)
        slot_id = add_slot(pid, "2026-11-15", "14:00", "15:00")

        bid = create_booking(c['id'], pid, sid, "scheduled", "cash", 200.0, slot_id)

        # Slot locked
        self.assertEqual(get_slot_by_id(slot_id)['is_booked'], 1)

        cancel_booking(bid, c['id'])

        # Slot freed
        self.assertEqual(get_slot_by_id(slot_id)['is_booked'], 0)


class TestRejectionFlow(unittest.TestCase):
    """Rejection lifecycle with slot liberation verification."""

    def setUp(self):
        clear_test_data()

    def tearDown(self):
        clear_test_data()

    def test_rejection_frees_slot_and_moves_to_history(self):
        """Rejected booking releases slot and appears in history."""
        c = create_raw_test_user("IntC4", "2030")
        p = create_raw_test_user("IntP4", "2031")
        pid = create_test_professional(p['id'], is_approved=True)
        sid = create_test_service("INT SERVICE Reject", 300.0)
        slot_id = add_slot(pid, "2026-12-01", "09:00", "10:00")

        bid = create_booking(c['id'], pid, sid, "scheduled", "cash", 300.0, slot_id)

        reject_booking(bid, pid)

        # Slot freed
        self.assertEqual(get_slot_by_id(slot_id)['is_booked'], 0)

        # In history, not active
        self.assertEqual(len(get_customer_bookings(c['id'])), 0)
        self.assertEqual(len(get_customer_history(c['id'])), 1)
        self.assertEqual(get_customer_history(c['id'])[0]['status'], 'rejected')


class TestImmediateBookingFlow(unittest.TestCase):
    """End-to-end with immediate booking type."""

    def setUp(self):
        clear_test_data()

    def tearDown(self):
        clear_test_data()

    def test_immediate_booking_auto_selects_and_completes(self):
        """Immediate booking auto-selects slot, then lifecycle completes normally."""
        c = create_raw_test_user("IntC5", "2040")
        p = create_raw_test_user("IntP5", "2041")
        pid = create_test_professional(p['id'], is_approved=True)
        sid = create_test_service("INT SERVICE Immediate", 400.0)
        slot_id = add_slot(pid, "2026-10-05", "08:00", "09:00")

        bid = create_booking(c['id'], pid, sid, "immediate", "upi", 400.0)
        self.assertIsNotNone(bid)

        # Slot should be auto-locked
        booking = get_booking_by_id(bid)
        self.assertIsNotNone(booking['time_slot_id'])
        self.assertEqual(get_slot_by_id(booking['time_slot_id'])['is_booked'], 1)

        # Normal lifecycle
        accept_booking(bid, pid)
        complete_booking(bid, pid)
        self.assertEqual(get_booking_by_id(bid)['status'], 'completed')


class TestPriceImmutabilityIntegration(unittest.TestCase):
    """Verify service price changes don't retroactively affect bookings."""

    def setUp(self):
        clear_test_data()

    def tearDown(self):
        clear_test_data()

    def test_service_price_change_does_not_affect_existing_booking(self):
        """Mutating service base_price after booking must not change total_price."""
        c = create_raw_test_user("IntC6", "2050")
        p = create_raw_test_user("IntP6", "2051")
        pid = create_test_professional(p['id'], is_approved=True)
        sid = create_test_service("INT SERVICE Immutable", 999.0)

        bid = create_booking(c['id'], pid, sid, "immediate", "cash", 999.0)
        original_price = float(get_booking_by_id(bid)['total_price'])

        # Mutate service price in DB
        from database.db import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE services SET base_price = 1.0 WHERE id = %s", (sid,))
        conn.commit()
        cursor.close()
        conn.close()

        # Booking total_price must remain at 999.0
        mutated_price = float(get_booking_by_id(bid)['total_price'])
        self.assertEqual(
            mutated_price, original_price,
            "Booking total_price must NOT change retroactively"
        )


if __name__ == '__main__':
    unittest.main()

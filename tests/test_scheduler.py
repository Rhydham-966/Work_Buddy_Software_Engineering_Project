"""
test_scheduler.py — Pure unit tests for BookingScheduler.

Covers:
    - Initial availability on fresh scheduler
    - Slot booking makes slot unavailable
    - Double-booking same slot
    - Multi-slot same professional
    - Cross-professional isolation
    - Edge values (empty string, None)

No database dependency.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from services.booking_scheduler import BookingScheduler


class TestBookingScheduler(unittest.TestCase):
    """Comprehensive tests for the in-memory BookingScheduler."""

    def setUp(self):
        self.scheduler = BookingScheduler()

    def tearDown(self):
        self.scheduler = None

    # ── AVAILABILITY ──
    def test_initial_availability_returns_true(self):
        """A fresh scheduler should show all slots as available."""
        self.assertTrue(self.scheduler.is_available(1, "10AM"))

    def test_availability_for_nonexistent_professional(self):
        """Querying a professional with no bookings returns available."""
        self.assertTrue(self.scheduler.is_available(9999, "10AM"))

    # ── BOOKING ──
    def test_booking_makes_slot_unavailable(self):
        """After booking a slot, it must be unavailable."""
        self.scheduler.book_slot(1, "10AM")
        self.assertFalse(self.scheduler.is_available(1, "10AM"))

    def test_double_booking_same_slot_stays_unavailable(self):
        """Booking the same slot twice should still show unavailable."""
        self.scheduler.book_slot(1, "10AM")
        self.scheduler.book_slot(1, "10AM")
        self.assertFalse(self.scheduler.is_available(1, "10AM"))

    def test_booking_one_slot_does_not_affect_another(self):
        """Booking 10AM should not block 11AM for the same professional."""
        self.scheduler.book_slot(1, "10AM")
        self.assertTrue(self.scheduler.is_available(1, "11AM"))

    def test_multiple_slots_same_professional(self):
        """A professional can have multiple booked slots."""
        self.scheduler.book_slot(1, "10AM")
        self.scheduler.book_slot(1, "11AM")
        self.scheduler.book_slot(1, "2PM")
        self.assertFalse(self.scheduler.is_available(1, "10AM"))
        self.assertFalse(self.scheduler.is_available(1, "11AM"))
        self.assertFalse(self.scheduler.is_available(1, "2PM"))
        self.assertTrue(self.scheduler.is_available(1, "3PM"))

    # ── CROSS-PROFESSIONAL ISOLATION ──
    def test_different_professional_slots_are_isolated(self):
        """Booking pro 1's 10AM must not affect pro 2's 10AM."""
        self.scheduler.book_slot(1, "10AM")
        self.assertTrue(self.scheduler.is_available(2, "10AM"))

    def test_multiple_professionals_independent_state(self):
        """Each professional maintains independent slot state."""
        self.scheduler.book_slot(1, "10AM")
        self.scheduler.book_slot(2, "11AM")
        self.scheduler.book_slot(3, "12PM")

        self.assertFalse(self.scheduler.is_available(1, "10AM"))
        self.assertTrue(self.scheduler.is_available(1, "11AM"))
        self.assertFalse(self.scheduler.is_available(2, "11AM"))
        self.assertTrue(self.scheduler.is_available(2, "10AM"))
        self.assertFalse(self.scheduler.is_available(3, "12PM"))
        self.assertTrue(self.scheduler.is_available(3, "10AM"))

    # ── EDGE VALUES ──
    def test_empty_string_slot(self):
        """Empty string is a valid slot key."""
        self.scheduler.book_slot(1, "")
        self.assertFalse(self.scheduler.is_available(1, ""))
        self.assertTrue(self.scheduler.is_available(1, "10AM"))

    def test_none_as_slot_value(self):
        """None is a valid slot key (no type enforcement)."""
        self.scheduler.book_slot(1, None)
        self.assertFalse(self.scheduler.is_available(1, None))

    def test_numeric_slot_value(self):
        """Numeric time values should work as keys."""
        self.scheduler.book_slot(1, 1000)
        self.assertFalse(self.scheduler.is_available(1, 1000))
        self.assertTrue(self.scheduler.is_available(1, 1100))


if __name__ == "__main__":
    unittest.main()
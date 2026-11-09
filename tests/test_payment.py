"""
test_payment.py — Comprehensive tests for the Payment Service layer.

Covers:
    - UPI payment → immediate 'paid' status
    - Cash payment → 'pending' status
    - Case-insensitive payment method handling
    - generate_invoice with valid/invalid booking
    - Immutability: service price change does not affect booking total_price

Database-dependent (uses live MySQL via test_utils).
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from services.payment_service import process_payment, generate_invoice
from repositories.booking_repository import get_booking_by_id
from services.booking_service import create_booking
from tests.test_utils import (
    clear_test_data,
    create_raw_test_user,
    create_test_professional,
    create_test_service,
)


class TestPaymentProcessing(unittest.TestCase):
    """Tests for process_payment with different methods."""

    def setUp(self):
        clear_test_data()
        self.customer = create_raw_test_user("PC1", "700")
        self.pro_user = create_raw_test_user("PP1", "701")
        self.pro_id = create_test_professional(self.pro_user['id'], True)
        self.service_id = create_test_service("Test Service Pay", 100.0)

    def tearDown(self):
        clear_test_data()

    def _create_booking(self):
        return create_booking(
            self.customer['id'], self.pro_id, self.service_id,
            "immediate", "cash", 100.0
        )

    def test_upi_payment_marks_as_paid(self):
        """UPI payment should set payment_status to 'paid'."""
        bid = self._create_booking()
        process_payment(bid, "upi", 100.0)
        b = get_booking_by_id(bid)
        self.assertEqual(b['payment_status'], 'paid')

    def test_cash_payment_stays_pending(self):
        """Cash payment should keep payment_status as 'pending'."""
        bid = self._create_booking()
        process_payment(bid, "cash", 100.0)
        b = get_booking_by_id(bid)
        self.assertEqual(b['payment_status'], 'pending')

    def test_upi_uppercase_marks_as_paid(self):
        """Payment method check is case-insensitive — 'UPI' works."""
        bid = self._create_booking()
        process_payment(bid, "UPI", 100.0)
        b = get_booking_by_id(bid)
        self.assertEqual(b['payment_status'], 'paid')

    def test_upi_mixed_case_marks_as_paid(self):
        """'Upi' (mixed case) should also be treated as UPI."""
        bid = self._create_booking()
        process_payment(bid, "Upi", 100.0)
        b = get_booking_by_id(bid)
        self.assertEqual(b['payment_status'], 'paid')

    def test_process_payment_returns_true(self):
        """process_payment should return True on success."""
        bid = self._create_booking()
        result = process_payment(bid, "cash", 100.0)
        self.assertTrue(result)


class TestGenerateInvoice(unittest.TestCase):
    """Tests for the generate_invoice print-based invoice."""

    def setUp(self):
        clear_test_data()
        self.customer = create_raw_test_user("GI1", "710")
        self.pro_user = create_raw_test_user("GI2", "711")
        self.pro_id = create_test_professional(self.pro_user['id'], True)
        self.sid = create_test_service("Test Service GI", 500.0)

    def tearDown(self):
        clear_test_data()

    def test_generate_invoice_with_valid_booking_does_not_raise(self):
        """generate_invoice on a valid booking must not raise."""
        bid = create_booking(
            self.customer['id'], self.pro_id, self.sid,
            "immediate", "upi", 500.0
        )
        try:
            generate_invoice(bid)
        except Exception as e:
            self.fail(f"generate_invoice raised {e} on valid booking")

    def test_generate_invoice_with_nonexistent_booking_does_not_raise(self):
        """generate_invoice on a non-existent booking must not crash."""
        try:
            generate_invoice(99999)
        except Exception as e:
            self.fail(f"generate_invoice raised {e} on non-existent booking")


class TestBookingPriceImmutability(unittest.TestCase):
    """Verify that changing service price does NOT retroactively affect bookings."""

    def setUp(self):
        clear_test_data()
        self.customer = create_raw_test_user("IM1", "720")
        self.pro_user = create_raw_test_user("IM2", "721")
        self.pro_id = create_test_professional(self.pro_user['id'], True)
        self.sid = create_test_service("Test Service Immutable", 999.0)

    def tearDown(self):
        clear_test_data()

    def test_service_price_change_does_not_affect_booking_total(self):
        """Once a booking is created, its total_price is frozen."""
        bid = create_booking(
            self.customer['id'], self.pro_id, self.sid,
            "immediate", "cash", 999.0
        )
        original_booking = get_booking_by_id(bid)
        original_price = float(original_booking['total_price'])

        # Mutate the service base_price in the database
        from database.db import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE services SET base_price = 1.0 WHERE id = %s",
            (self.sid,)
        )
        conn.commit()
        cursor.close()
        conn.close()

        # Booking total_price must remain unchanged
        updated_booking = get_booking_by_id(bid)
        self.assertEqual(
            float(updated_booking['total_price']),
            original_price,
            "Booking total_price must NOT change when service base_price is modified"
        )


if __name__ == '__main__':
    unittest.main()
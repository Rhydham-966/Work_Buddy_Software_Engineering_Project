"""
test_invoice.py — Comprehensive tests for the Invoice module.

Covers:
    - Invoice creation during payment processing
    - Invoice field accuracy (amount, method, status)
    - Invoice retrieval for non-existent booking
    - Invoice after booking completion (generate_invoice print)
    - Multiple invoices for same booking (latest retrieval)

Database-dependent (uses live MySQL via test_utils).
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from repositories.invoice_repository import get_invoice_by_booking, create_invoice
from services.payment_service import process_payment
from services.booking_service import create_booking, accept_booking, complete_booking
from tests.test_utils import (
    clear_test_data,
    create_raw_test_user,
    create_test_professional,
    create_test_service,
)


class TestInvoiceCreation(unittest.TestCase):
    """Tests for invoice creation via process_payment."""

    def setUp(self):
        clear_test_data()
        self.customer = create_raw_test_user("INV1", "1000")
        self.pro_user = create_raw_test_user("INV2", "1001")
        self.pro_id = create_test_professional(self.pro_user['id'], True)
        self.sid = create_test_service("Test Service INV", 500.0)

    def tearDown(self):
        clear_test_data()

    def test_invoice_created_on_payment_processing(self):
        """process_payment must create an invoice record in DB."""
        bid = create_booking(
            self.customer['id'], self.pro_id, self.sid,
            "immediate", "cash", 500.0
        )
        process_payment(bid, "cash", 500.0)
        inv = get_invoice_by_booking(bid)
        self.assertIsNotNone(inv, "Invoice must exist after process_payment")

    def test_invoice_amount_matches_booking_price(self):
        """Invoice amount must match the charged amount."""
        bid = create_booking(
            self.customer['id'], self.pro_id, self.sid,
            "immediate", "upi", 500.0
        )
        process_payment(bid, "upi", 500.0)
        inv = get_invoice_by_booking(bid)
        self.assertEqual(float(inv['amount']), 500.0)

    def test_invoice_payment_method_matches(self):
        """Invoice payment_method must match what was processed."""
        bid = create_booking(
            self.customer['id'], self.pro_id, self.sid,
            "immediate", "cash", 500.0
        )
        process_payment(bid, "cash", 500.0)
        inv = get_invoice_by_booking(bid)
        self.assertEqual(inv['payment_method'], 'cash')

    def test_invoice_upi_payment_status_is_paid(self):
        """UPI invoice should reflect 'paid' status."""
        bid = create_booking(
            self.customer['id'], self.pro_id, self.sid,
            "immediate", "upi", 500.0
        )
        process_payment(bid, "upi", 500.0)
        inv = get_invoice_by_booking(bid)
        self.assertEqual(inv['payment_status'], 'paid')

    def test_invoice_cash_payment_status_is_pending(self):
        """Cash invoice should reflect 'pending' status."""
        bid = create_booking(
            self.customer['id'], self.pro_id, self.sid,
            "immediate", "cash", 500.0
        )
        process_payment(bid, "cash", 500.0)
        inv = get_invoice_by_booking(bid)
        self.assertEqual(inv['payment_status'], 'pending')


class TestInvoiceRetrieval(unittest.TestCase):
    """Tests for invoice retrieval edge cases."""

    def setUp(self):
        clear_test_data()

    def tearDown(self):
        clear_test_data()

    def test_get_invoice_for_nonexistent_booking_returns_none(self):
        """Fetching invoice for a non-existent booking returns None."""
        inv = get_invoice_by_booking(99999)
        self.assertIsNone(inv)

    def test_get_invoice_returns_latest_if_multiple_exist(self):
        """If multiple invoices exist for a booking, the latest is returned."""
        c = create_raw_test_user("InvMulti1", "1010")
        p = create_raw_test_user("InvMulti2", "1011")
        pid = create_test_professional(p['id'], True)
        sid = create_test_service("Test Service InvMulti", 100.0)

        bid = create_booking(c['id'], pid, sid, "immediate", "cash", 100.0)
        # Create two invoices manually
        create_invoice(bid, 100.0, "cash", "pending")
        create_invoice(bid, 100.0, "cash", "paid")  # latest

        inv = get_invoice_by_booking(bid)
        self.assertEqual(inv['payment_status'], 'paid', "Must return the latest invoice")


class TestInvoiceOnCompletion(unittest.TestCase):
    """Tests for generate_invoice triggered by booking completion."""

    def setUp(self):
        clear_test_data()
        self.customer = create_raw_test_user("InvComp1", "1020")
        self.pro_user = create_raw_test_user("InvComp2", "1021")
        self.pro_id = create_test_professional(self.pro_user['id'], True)
        self.sid = create_test_service("Test Service InvComp", 750.0)

    def tearDown(self):
        clear_test_data()

    def test_complete_booking_does_not_crash_generate_invoice(self):
        """complete_booking → generate_invoice (print) must not raise."""
        bid = create_booking(
            self.customer['id'], self.pro_id, self.sid,
            "immediate", "cash", 750.0
        )
        process_payment(bid, "cash", 750.0)
        accept_booking(bid, self.pro_id)

        try:
            success, msg = complete_booking(bid, self.pro_id)
            self.assertTrue(success, "Booking completion must succeed")
        except Exception as e:
            self.fail(f"complete_booking raised {e} during invoice generation")


if __name__ == '__main__':
    unittest.main()

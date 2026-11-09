# tests/service/test_payment_service.py
# ============================================================
# Service-layer tests for services/payment_service.py
# Tests: process_payment, generate_invoice
# Uses REAL MySQL — no mocking.
# ============================================================

import sys                                          # for path manipulation
import os                                           # for path joining

# -- Ensure project root is importable --
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from services.payment_service import (              # import service functions
    process_payment,                                # processes payment and creates invoice
    generate_invoice                                # prints invoice details to console
)
from services.booking_service import (              # booking service for setup
    create_booking                                  # creates a booking for payment tests
)
from repositories.booking_repository import (       # repo access for verification
    get_booking_by_id                               # fetch booking to check payment status
)
from repositories.invoice_repository import (       # repo access for invoices
    get_invoice_by_booking                          # fetch invoice by booking ID
)
from database.db import get_connection              # direct DB access for cleanup


# ============================================================
# HELPER: clean up a booking and its invoices
# ============================================================
def _cleanup_booking(booking_id):
    """Delete a booking and related invoices from the database."""
    conn = get_connection()                         # get connection
    cursor = conn.cursor()                          # open cursor
    cursor.execute("DELETE FROM invoices WHERE booking_id = %s", (booking_id,))  # invoices first
    cursor.execute("DELETE FROM bookings WHERE id = %s", (booking_id,))         # then booking
    conn.commit()                                   # persist
    cursor.close()                                  # close cursor
    conn.close()                                    # close connection


# ============================================================
# TEST 1: process_payment — UPI sets payment_status to 'paid'
# ============================================================
def test_process_payment_upi(
    db_connection, test_user, test_professional_with_service, test_slot
):
    """UPI payment should set payment_status to 'paid' and create an invoice."""
    pro = test_professional_with_service["professional"]   # professional dict
    svc = test_professional_with_service["service"]        # service dict

    # -- Create a booking to pay for --
    booking_id = create_booking(                    # create test booking
        customer_id=test_user["id"],
        professional_id=pro["id"],
        service_id=svc["id"],
        booking_type="scheduled",
        payment_method="upi",
        total_price=750.00,
        slot_id=test_slot["id"]
    )

    # -- Process payment --
    result = process_payment(                       # call service function
        booking_id=booking_id,                      # which booking to pay
        method="upi",                               # UPI method
        amount=750.00                               # payment amount
    )

    assert result is True, "process_payment must return True"  # must succeed

    # -- Verify payment_status updated in booking --
    booking = get_booking_by_id(booking_id)         # fetch the booking
    assert booking["payment_status"] == "paid", \
        "UPI payment must set payment_status to 'paid'"  # must be 'paid'

    # -- Verify invoice was created --
    invoice = get_invoice_by_booking(booking_id)    # fetch the invoice
    assert invoice is not None, "Invoice must exist after payment"  # must exist
    assert float(invoice["amount"]) == 750.00, "Invoice amount must match"    # correct amount
    assert invoice["payment_method"] == "upi", "Invoice method must be 'upi'"  # correct method
    assert invoice["payment_status"] == "paid", "Invoice status must be 'paid'"  # correct status

    # -- CLEANUP --
    _cleanup_booking(booking_id)


# ============================================================
# TEST 2: process_payment — cash keeps payment_status as 'pending'
# ============================================================
def test_process_payment_cash(
    db_connection, test_user, test_professional_with_service, test_slot
):
    """Cash payment should keep payment_status as 'pending'."""
    pro = test_professional_with_service["professional"]
    svc = test_professional_with_service["service"]

    # -- Create a booking --
    booking_id = create_booking(
        customer_id=test_user["id"],
        professional_id=pro["id"],
        service_id=svc["id"],
        booking_type="scheduled",
        payment_method="cash",
        total_price=500.00,
        slot_id=test_slot["id"]
    )

    # -- Process payment --
    result = process_payment(                       # call service function
        booking_id=booking_id,
        method="cash",                              # cash method
        amount=500.00
    )

    assert result is True, "process_payment must return True"  # must succeed

    # -- Verify payment_status remains 'pending' --
    booking = get_booking_by_id(booking_id)         # fetch the booking
    assert booking["payment_status"] == "pending", \
        "Cash payment must keep payment_status as 'pending'"  # must be 'pending'

    # -- Verify invoice was created with 'pending' status --
    invoice = get_invoice_by_booking(booking_id)    # fetch the invoice
    assert invoice is not None, "Invoice must exist after payment"
    assert invoice["payment_status"] == "pending", \
        "Invoice status must be 'pending' for cash"

    # -- CLEANUP --
    _cleanup_booking(booking_id)


# ============================================================
# TEST 3: generate_invoice — prints invoice for valid booking
# ============================================================
def test_generate_invoice_valid(
    db_connection, test_user, test_professional_with_service, test_slot, capsys
):
    """generate_invoice should print invoice details for a valid booking."""
    pro = test_professional_with_service["professional"]
    svc = test_professional_with_service["service"]

    # -- Create a booking and process payment --
    booking_id = create_booking(
        customer_id=test_user["id"],
        professional_id=pro["id"],
        service_id=svc["id"],
        booking_type="scheduled",
        payment_method="upi",
        total_price=600.00,
        slot_id=test_slot["id"]
    )
    process_payment(booking_id, "upi", 600.00)      # process payment first

    # -- Generate invoice (prints to stdout) --
    generate_invoice(booking_id)                    # call service function

    # -- Capture console output --
    captured = capsys.readouterr()                  # capture stdout/stderr
    output = captured.out                           # get stdout content

    assert "INVOICE" in output, "Output must contain 'INVOICE'"        # header present
    assert str(booking_id) in output, "Output must contain booking ID"  # booking ID shown

    # -- CLEANUP --
    _cleanup_booking(booking_id)


# ============================================================
# TEST 4: generate_invoice — invalid booking prints error
# ============================================================
def test_generate_invoice_invalid_booking(db_connection, capsys):
    """generate_invoice should print an error for a non-existent booking."""
    generate_invoice(999999)                        # call with fake booking ID

    captured = capsys.readouterr()                  # capture stdout
    output = captured.out                           # get stdout content

    assert "error" in output.lower(), \
        "Output must contain an error message for invalid booking"  # error shown


# ============================================================
# TEST 5: process_payment — creates invoice even with invalid method
# ============================================================
def test_process_payment_unknown_method(
    db_connection, test_user, test_professional_with_service, test_slot
):
    """An unknown payment method should default to 'pending' status."""
    pro = test_professional_with_service["professional"]
    svc = test_professional_with_service["service"]

    booking_id = create_booking(
        customer_id=test_user["id"],
        professional_id=pro["id"],
        service_id=svc["id"],
        booking_type="scheduled",
        payment_method="cash",                      # use cash as DB enum
        total_price=400.00,
        slot_id=test_slot["id"]
    )

    # -- Process with an unknown method string --
    result = process_payment(                       # call service function
        booking_id=booking_id,
        method="bitcoin",                           # not 'upi', so defaults to pending
        amount=400.00
    )

    assert result is True, "process_payment must still return True"

    # -- Verify payment_status is 'pending' (since method != 'upi') --
    booking = get_booking_by_id(booking_id)         # fetch the booking
    assert booking["payment_status"] == "pending", \
        "Unknown method must set payment_status to 'pending'"

    # -- CLEANUP --
    _cleanup_booking(booking_id)

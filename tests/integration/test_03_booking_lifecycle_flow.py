# tests/integration/test_03_booking_lifecycle_flow.py
# ============================================================
# INTEGRATION TEST — Booking Lifecycle Component
#
# Simulates the actual transaction:
#   1. View Services & Professionals
#   2. Book Slot
#   3. Accept Booking
#   4. Process Payment
#   5. Complete Booking
#   6. Verify final invoice
#
# Leverages base fixtures to eliminate setup boilerplate.
# ============================================================

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from services.customer_service import view_services, get_professionals_for_service
from services.booking_service import create_booking, accept_booking, complete_booking, get_available_slots_for_professional
from services.payment_service import process_payment
from repositories.booking_repository import get_booking_by_id
from repositories.invoice_repository import get_invoice_by_booking
from database.db import get_connection

def test_booking_lifecycle_flow(db_connection, test_user, test_professional_with_service, test_slot):
    customer = test_user
    pro = test_professional_with_service["professional"]
    svc = test_professional_with_service["service"]
    slot = test_slot
    booking_id = None

    try:
        # STEP 1: Verify Browse Feeds
        assert len(view_services()) > 0
        assert len(get_professionals_for_service(svc["id"])) > 0
        assert len(get_available_slots_for_professional(pro["id"])) > 0

        # STEP 2: Book
        booking_id = create_booking(
            customer_id=customer["id"],
            professional_id=pro["id"],
            service_id=svc["id"],
            booking_type="scheduled",
            payment_method="upi",
            total_price=750.00,
            slot_id=slot["id"]
        )
        assert booking_id is not None
        assert get_booking_by_id(booking_id)["status"] == "pending"

        # STEP 3: Accept
        accept_booking(booking_id, pro["id"])
        assert get_booking_by_id(booking_id)["status"] == "accepted"

        # STEP 4: Pay
        process_payment(booking_id, "upi", 750.00)
        assert get_booking_by_id(booking_id)["payment_status"] == "paid"

        # STEP 5: Complete
        complete_booking(booking_id, pro["id"])
        assert get_booking_by_id(booking_id)["status"] == "completed"

        # STEP 6: Verify Invoice
        invoice = get_invoice_by_booking(booking_id)
        assert invoice is not None
        assert float(invoice["amount"]) == 750.00

    finally:
        # CLEANUP (Only booking/invoice since fixtures handle the core data)
        if booking_id:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM invoices WHERE booking_id = %s", (booking_id,))
            cursor.execute("DELETE FROM bookings WHERE id = %s", (booking_id,))
            conn.commit()
            cursor.close()
            conn.close()

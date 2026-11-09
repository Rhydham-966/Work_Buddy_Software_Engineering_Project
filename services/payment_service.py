# services/payment_service.py

from repositories.booking_repository import get_booking_by_id, update_payment_status
from repositories.invoice_repository import create_invoice

def process_payment(booking_id, method, amount):
    # IF payment_method == 'upi': mark payment_status = 'paid'
    # IF cash: keep pending until completion
    payment_status = 'paid' if method.lower() == 'upi' else 'pending'

    update_payment_status(booking_id, payment_status)
    
    # Store invoice in DB
    create_invoice(booking_id, amount, method, payment_status)
    return True

def generate_invoice(booking_id):
    booking = get_booking_by_id(booking_id)
    if not booking:
        print("Booking Error - could not retrieve invoice details.")
        return

    print("----- INVOICE -----")
    print(f"Booking ID: {booking['id']}")
    print(f"Customer ID: {booking['user_id']}")
    print(f"Professional ID: {booking['professional_id']}")
    print(f"Service ID: {booking['service_id']}")
    print(f"Amount: {booking['total_price']}")
    print(f"Payment Method: {str(booking['payment_method']).lower()}")
    print(f"Payment Status: {str(booking['payment_status']).lower()}")
    print("---------------")
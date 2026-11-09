# controllers/customer_controller.py

from services.customer_service import view_services, get_professionals_for_service
from services.booking_service import (
    create_booking,
    get_available_slots_for_professional,
    get_customer_bookings,
    get_customer_history
)


def customer_dashboard(user):
    while True:
        print("\n--- CUSTOMER DASHBOARD ---")
        print("1. Browse Services & Book")
        print("2. View Active Bookings")
        print("3. View Booking History")
        print("4. Logout")

        choice = input("Enter choice: ")

        if choice == "1":
            handle_booking(user)
        elif choice == "2":
            handle_view_bookings(user)
        elif choice == "3":
            handle_view_history(user)
        elif choice == "4":
            break
        else:
            print("Invalid choice!")


def handle_booking(user):
    print("\n--- Available Services ---")
    services = view_services()

    if not services:
        print("No services available at the moment.")
        return

    for s in services:
        print(f"{s['id']}. {s['name']} - ₹{s['base_price']} ({s['estimated_time']})")

    try:
        service_id = int(input("\nSelect a Service ID to view professionals: "))
    except ValueError:
        print("Invalid input!")
        return

    # Check if service exists
    if not any(s['id'] == service_id for s in services):
        print("Invalid Service ID.")
        return

    print("\n--- Professionals for this Service ---")
    professionals = get_professionals_for_service(service_id)

    if not professionals:
        print("No approved professionals available for this service right now.")
        return

    for p in professionals:
        print(f"ID: {p['id']} | Name: {p['name']} | Experience: {p['experience']} yrs | Area: {p['area']} | Radius: {p['work_radius']} km | Custom Price: ₹{p['custom_price']}")

    try:
        prof_id = int(input("\nSelect a Professional ID to view available slots: "))
    except ValueError:
        print("Invalid input!")
        return

    if not any(p['id'] == prof_id for p in professionals):
        print("Invalid Professional ID.")
        return

    print("\n--- Available Slots ---")
    slots = get_available_slots_for_professional(prof_id)

    if not slots:
        print("No available slots for this professional at the moment.")
        return

    for slot in slots:
        print(f"Slot ID: {slot['id']} | Date: {slot['slot_date']} | Time: {slot['start_time']} - {slot['end_time']}")

    try:
        slot_id = int(input("\nSelect a Slot ID to book: "))
    except ValueError:
        print("Invalid input!")
        return

    if not any(slot['id'] == slot_id for slot in slots):
        print("Invalid Slot ID.")
        return

    print("\nBooking Type:")
    print("1. Immediate")
    print("2. Scheduled")
    
    b_type_choice = input("Enter choice (1/2): ")
    booking_type = "immediate" if b_type_choice == "1" else "scheduled"

    print("\nPayment Method:")
    print("1. Cash")
    print("2. UPI")
    pay_choice = input("Enter choice (1/2): ")
    payment_method = "upi" if pay_choice == "2" else "cash"

    # Find total price dynamically from the professional offering
    custom_price = 0
    for p in professionals:
        if p['id'] == prof_id:
            custom_price = p['custom_price']
            break

    print(f"\nTotal Price for this service will be: ₹{custom_price}")
    print("Confirm Booking? (y/n)")
    confirm = input("Choice: ").lower()

    if confirm == 'y':
        # Booking now maps extended schema inputs 
        booking_id = create_booking(user['id'], prof_id, service_id, booking_type, payment_method, custom_price, slot_id=slot_id)
        
        if booking_id:
            print(f"Booking confirmed! Booking ID: {booking_id}")
            
            # Immediately trigger invoice and payment processing rules
            from services.payment_service import process_payment, generate_invoice
            process_payment(booking_id, payment_method, custom_price)
            generate_invoice(booking_id)
        else:
            print("Booking completely failed.")
    else:
        print("Booking cancelled.")


def handle_view_bookings(user):
    bookings = get_customer_bookings(user['id'])

    if not bookings:
        print("You have no active bookings.")
        return

    print("\n--- Your Active Bookings ---")
    can_cancel = False
    for b in bookings:
        print(f"Booking #{b['id']} | Service: {b['service_name']} | Professional: {b['professional_name']} | "
              f"Time: {b['scheduled_datetime']} | "
              f"Type: {b['booking_type']} | Status: {b['status']} | Payment: {b['payment_status']}")
        if b['status'] == 'pending':
            can_cancel = True

    if can_cancel:
        action = input("\nDo you want to cancel any booking? (y/n): ").lower()
        if action == 'y':
            try:
                b_id = int(input("Enter Booking ID to cancel: "))
                from services.booking_service import cancel_booking
                success, msg = cancel_booking(b_id, user['id'])
                print(msg)
            except ValueError:
                print("Invalid input!")

# ---------------- VIEW BOOKING HISTORY ----------------
def handle_view_history(user):
    history = get_customer_history(user['id'])

    if not history:
        print("No booking history found.")
        return

    print("\n--- Your Booking History ---")
    for b in history:
        print(f"Booking #{b['id']} | Service: {b['service_name']} | Professional: {b['professional_name']} | "
              f"Time: {b['scheduled_datetime']} | "
              f"Type: {b['booking_type']} | Status: {b['status']} | Payment: {b['payment_status']}")

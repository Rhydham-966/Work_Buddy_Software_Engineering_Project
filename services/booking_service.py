# services/booking_service.py

from repositories.booking_repository import (
    create_booking as repo_create_booking,
    get_bookings_by_customer,
    get_bookings_by_professional,
    mark_slot_booked,
    get_booking_by_id,
    update_booking_status,
    unmark_slot_booked,
    deactivate_booking,
    get_booking_history_by_customer,
    get_booking_history_by_professional
)
from repositories.time_slot_repository import get_available_slots, get_slot_by_id
from services.payment_service import generate_invoice

def is_valid_transition(current_status, new_status):
    rules = {
        "pending": ["accepted", "rejected", "cancelled"],
        "accepted": ["completed"],
        "completed": [],
        "cancelled": [],
        "rejected": []
    }
    return new_status in rules.get(current_status, [])


# ---------------- CREATE BOOKING ----------------
def create_booking(customer_id, professional_id, service_id, booking_type, payment_method, total_price, slot_id=None):
    scheduled_datetime = None
    
    if booking_type == "immediate":
        # Find earliest slot and mark it
        slots = get_available_slots(professional_id)
        if slots:
            slot_id = slots[0]['id']
            # We construct a primitive datetime string for the DB (using string formatting)
            scheduled_datetime = f"{slots[0]['slot_date']} {slots[0]['start_time']}"
        else:
            # No immediate slot; proceed with a pending booking without a slot
            print("[WARN] No immediate slot available; booking created without slot assignment.")
            # Keep slot_id as None and scheduled_datetime as None
    else:
        # Scheduled: The user provided a slot_id, we look it up to grab the scheduled_datetime
        if slot_id:
            slot_data = get_slot_by_id(slot_id)
            if slot_data:
                scheduled_datetime = f"{slot_data['slot_date']} {slot_data['start_time']}"

    # Lock the slot
    if slot_id:
        mark_slot_booked(slot_id)

    # Note: payment_status defaults to pending.
    payment_status = 'pending'

    booking_id = repo_create_booking(
        customer_id, professional_id, service_id, slot_id, 
        booking_type, scheduled_datetime, payment_method, payment_status, total_price
    )
    return booking_id


# ---------------- CUSTOMER BOOKINGS ----------------
def get_customer_bookings(customer_id):
    return get_bookings_by_customer(customer_id)

def get_customer_history(customer_id):
    return get_booking_history_by_customer(customer_id)

# ---------------- PROFESSIONAL BOOKINGS ----------------
def get_professional_bookings(professional_id):
    return get_bookings_by_professional(professional_id)

def get_professional_history(professional_id):
    return get_booking_history_by_professional(professional_id)

# ---------------- GET SLOTS ----------------
def get_available_slots_for_professional(professional_id):
    return get_available_slots(professional_id)


# ---------------- CANCEL/UPDATE BOOKING (PROFESSIONAL OR CUSTOMER) ----------------
def cancel_booking(booking_id, user_id):
    booking = get_booking_by_id(booking_id)
    if not booking:
        return False, "Booking not found."
    
    if booking['user_id'] != user_id:
        return False, "Unauthorized."
        
    if not is_valid_transition(booking['status'], 'cancelled'):
        return False, f"Invalid transition: Cannot cancel from '{booking['status']}' status."
        
    if booking['time_slot_id']:
        unmark_slot_booked(booking['time_slot_id'])
    
    update_booking_status(booking_id, 'cancelled')
    deactivate_booking(booking_id)
    return True, "Booking cancelled securely."

def accept_booking(booking_id, professional_id):
    booking = get_booking_by_id(booking_id)
    if not booking or booking['professional_id'] != professional_id:
        return False, "Unauthorized or not found."
        
    if not is_valid_transition(booking['status'], 'accepted'):
        return False, f"Invalid transition: Cannot accept from '{booking['status']}'."
        
    update_booking_status(booking_id, 'accepted')
    return True, "Booking ACCEPTED successfully."

def reject_booking(booking_id, professional_id):
    booking = get_booking_by_id(booking_id)
    if not booking or booking['professional_id'] != professional_id:
        return False, "Unauthorized or not found."
        
    if not is_valid_transition(booking['status'], 'rejected'):
        return False, f"Invalid transition: Cannot reject from '{booking['status']}'."
        
    if booking['time_slot_id']:
        unmark_slot_booked(booking['time_slot_id'])
        
    update_booking_status(booking_id, 'rejected')
    deactivate_booking(booking_id)
    return True, "Booking REJECTED. Slot freed."

def complete_booking(booking_id, professional_id):
    booking = get_booking_by_id(booking_id)
    if not booking or booking['professional_id'] != professional_id:
        return False, "Unauthorized or not found."
        
    if not is_valid_transition(booking['status'], 'completed'):
        return False, f"Invalid transition: Cannot complete from '{booking['status']}'."
        
    update_booking_status(booking_id, 'completed')
    deactivate_booking(booking_id)
    
    print("\n[SUCCESS] Booking successfully COMPLETED. Finalizing Invoice computations...")
    generate_invoice(booking_id)
    
    return True, "Booking COMPLETED! Great job."
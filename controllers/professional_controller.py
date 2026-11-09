# controllers/professional_controller.py

from services.professional_service import (
    create_profile,
    add_service_pricing,
    add_slot,
    get_profile,
    get_my_services,
    get_my_slots,
    get_available_services
)

from services.booking_service import get_professional_bookings, get_professional_history

# ---------------- REGISTRATION PROFILE FLOW ----------------
def handle_profile_creation(user):
    print("\n--- Setup Professional Profile ---")
    services = get_available_services()
    if not services:
        print("No structural services defined. You can't offer anything yet.")
        
    try:
        experience = int(input("Experience (years): "))
        area = input("Work Area (City): ")
        work_radius = int(input("Work Radius (km): "))
    except ValueError:
        print("Invalid input, aborting profile setup.")
        return

    # Create base professional record (no service_id anymore)
    professional_id = create_profile(user["id"], experience, area, work_radius)
    if not professional_id:
        print("Profile may already exist.")
        return

    if not services:
        print("Wait for admin to configure services. Setup complete for now!")
        return

    print("\n--- Select Your Services & Set Prices ---")
    for s in services:
        print(f"{s['id']}. {s['name']} (Platform base suggestion: Rs.{s['base_price']} | {s['estimated_time']})")
        
    # Let them add services
    while True:
        choice = input("\nEnter Service ID to offer (or 'done' to finish): ")
        if choice.lower() == 'done':
            break
        
        try:
            sid = int(choice)
            if any(s['id'] == sid for s in services):
                price = float(input(f"Enter your custom price you want to charge for Service ID {sid}: "))
                # Add to mapping
                add_service_pricing(professional_id, sid, price)
                print("Service added successfully to your profile!")
            else:
                print("Invalid Service ID. Try again.")
        except ValueError:
            print("Please enter a valid number or 'done'.")
            
    print("Profile setup complete! Please wait for Admin approval to appear in search.")


# ---------------- DASHBOARD ----------------
def professional_dashboard(user):
    while True:
        print("\n--- PROFESSIONAL DASHBOARD ---")
        print("1. View My Profile & Pricing")
        print("2. Add Time Slot")
        print("3. View My Slots")
        print("4. View Active Bookings")
        print("5. Manage Booking Status (Accept/Reject/Complete)")
        print("6. View Booking History")
        print("7. Logout")

        choice = input("Enter choice: ")

        if choice == "1":
            handle_view_profile(user)
        elif choice == "2":
            handle_add_slot(user)
        elif choice == "3":
            handle_view_slots(user)
        elif choice == "4":
            handle_view_bookings(user)
        elif choice == "5":
            handle_booking_action(user)
        elif choice == "6":
            handle_view_history(user)
        elif choice == "7":
            break
        else:
            print("Invalid choice!")


# ---------------- VIEW PROFILE ----------------
def handle_view_profile(user):
    profile = get_profile(user["id"])

    if profile:
        print("\n--- Your Profile ---")
        print(f"Professional ID: {profile['id']}")
        print(f"Experience: {profile['experience']} years")
        print(f"Area: {profile['area']}")
        print(f"Work Radius: {profile['work_radius']} km")
        print(f"Approved: {'Yes' if profile['is_approved'] else 'No (Pending)'}")
        
        print("\n--- Services Offered & Pricing ---")
        my_services = get_my_services(profile['id'])
        if my_services:
            for ms in my_services:
                print(f"  {ms['name']} - You charge: ₹{ms['custom_price']}")
        else:
            print("  No services offered yet!!")
            
    else:
        print("Profile not found. Let's create one now!")
        handle_profile_creation(user)


# ---------------- ADD TIME SLOT ----------------
def handle_add_slot(user):
    profile = get_profile(user["id"])

    if not profile:
        print("No profile active!")
        return

    if not profile["is_approved"]:
        print("Your profile is not approved yet! Wait for admin approval.")
        return

    print("\n--- Add Time Slot ---")

    try:
        slot_date = input("Date (YYYY-MM-DD): ")
        start_time = input("Start Time (HH:MM): ")
        end_time = input("End Time (HH:MM): ")
    except ValueError:
        print("Invalid input!")
        return

    slot_id = add_slot(profile["id"], slot_date, start_time, end_time)

    if slot_id:
        print(f"Time slot added successfully! (Slot ID: {slot_id})")
    else:
        print("Failed to add time slot.")


# ---------------- VIEW SLOTS ----------------
def handle_view_slots(user):
    profile = get_profile(user["id"])

    if not profile:
        print("Create your profile first!")
        return

    slots = get_my_slots(profile["id"])

    if not slots:
        print("No time slots found. Add slots first.")
        return

    print("\n--- Your Time Slots ---")
    for slot in slots:
        status = "BOOKED" if slot["is_booked"] else "AVAILABLE"
        print(f"  Slot {slot['id']}: {slot['slot_date']} | {slot['start_time']} - {slot['end_time']} | {status}")


# ---------------- VIEW BOOKINGS ----------------
def handle_view_bookings(user):
    profile = get_profile(user["id"])

    if not profile:
        print("No active profile!")
        return

    bookings = get_professional_bookings(profile["id"])

    if not bookings:
        print("No active bookings yet.")
        return

    print("\n--- Your Active Bookings ---")
    for b in bookings:
        print(f"  Booking #{b['id']}: {b['service_name']} | Customer: {b['customer_name']} | "
              f"Time: {b['scheduled_datetime']} | Status: {b['status']} | Payment: {b['payment_status']}")

# ---------------- VIEW BOOKING HISTORY ----------------
def handle_view_history(user):
    profile = get_profile(user["id"])
    if not profile:
        print("No active profile!")
        return

    history = get_professional_history(profile["id"])

    if not history:
        print("No booking history.")
        return

    print("\n--- Your Booking History ---")
    for b in history:
        print(f"  Booking #{b['id']}: {b['service_name']} | Customer: {b['customer_name']} | "
              f"Time: {b['scheduled_datetime']} | Status: {b['status']} | Payment: {b['payment_status']}")


# ---------------- MANAGE BOOKING STATUS ----------------
def handle_booking_action(user):
    profile = get_profile(user["id"])
    if not profile:
        print("No active profile!")
        return

    try:
        b_id = int(input("\nEnter Booking ID to manage: "))
    except ValueError:
        print("Invalid ID.")
        return

    print("Actions:")
    print("a - Accept")
    print("r - Reject")
    print("c - Complete")
    
    action = input("Choose action: ").lower()
    from services.booking_service import accept_booking, reject_booking, complete_booking

    if action == 'a':
        success, msg = accept_booking(b_id, profile["id"])
        print(msg)
    elif action == 'r':
        success, msg = reject_booking(b_id, profile["id"])
        print(msg)
    elif action == 'c':
        success, msg = complete_booking(b_id, profile["id"])
        print(msg)
    else:
        print("Invalid action.")

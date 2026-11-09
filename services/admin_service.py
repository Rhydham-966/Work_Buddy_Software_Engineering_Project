# services/admin_service.py

from repositories.service_repository import add_service as repo_add_service, get_all_services
from repositories.professional_repository import (
    get_pending_professionals,
    approve_professional as repo_approve_professional,
    reject_professional as repo_reject_professional,
    get_professional_by_user
)
from services.professional_service import get_my_services


# ---------------- ADD SERVICE ----------------
def add_service(name, description, base_price, estimated_time):
    # Check for duplicate service name
    services = get_all_services()
    if any(s['name'] == name for s in services):
        return False, "Service with this name already exists."
    try:
        repo_add_service(name, description, base_price, estimated_time)
        return True, "Service added successfully."
    except Exception as e:
        return False, str(e)


# Existing CLI helper (kept for interactive use)
def create_service():
    print("\n--- Add Service ---")

    name = input("Service Name: ")
    description = input("Description: ")
    base_price = float(input("Base Price: "))
    estimated_time = input("Estimated Time (e.g. 2 hours): ")

    success, message = add_service(name, description, base_price, estimated_time)
    print(message)


# ---------------- VIEW SERVICES ----------------
def view_services():
    services = get_all_services()

    print("\n--- All Services ---")
    for s in services:
        print(f"{s['id']}. {s['name']} - ₹{s['base_price']} ({s['estimated_time']})")


# ---------------- APPROVE PROFESSIONAL ----------------
def approve_professional(professional_id):
    try:
        repo_approve_professional(professional_id)
        return True, "Professional approved."
    except Exception as e:
        return False, str(e)


def manage_professionals():
    professionals = get_pending_professionals()

    if not professionals:
        print("No pending professionals!")
        return

    print("\n--- Pending Professionals ---")
    for p in professionals:
        print(f"""
ID: {p['id']}
Name: {p['name']}
Phone: {p['phone']}
Experience: {p['experience']} years
Area: {p['area']}""")
        services_offered = get_my_services(p['id'])
        if services_offered:
            print("Services Apply:")
            for s in services_offered:
                print(f"  - {s['name']} (Custom Price: ₹{s['custom_price']})")
        else:
            print("  - No services offered yet.")
        print("")

    choice = input("Enter Professional ID to approve/reject: ")

    action = input("Enter 'a' to approve or 'r' to reject: ")

    if action == 'a':
        success, message = approve_professional(choice)
        print(message)
    elif action == 'r':
        repo_reject_professional(choice)
        print("Professional rejected!")
    else:
        print("Invalid action!")
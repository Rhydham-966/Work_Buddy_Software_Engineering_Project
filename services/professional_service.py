# services/professional_service.py

from repositories.professional_repository import (
    create_professional,
    get_professional_by_user,
    add_professional_service,
    get_services_for_professional
)

from repositories.time_slot_repository import (
    add_time_slot as repo_add_time_slot,
    get_available_slots,
    get_all_slots_by_professional
)

from repositories.service_repository import get_all_services


# ---------------- CREATE PROFILE ----------------
def create_profile(user_id, experience, area, work_radius):
    existing = get_professional_by_user(user_id)

    if existing:
        return None

    professional_id = create_professional(user_id, experience, area, work_radius)
    return professional_id

def add_service_pricing(professional_id, service_id, custom_price):
    add_professional_service(professional_id, service_id, custom_price)

# ---------------- ADD TIME SLOT ----------------
def add_slot(professional_id, slot_date, start_time, end_time):
    slot_id = repo_add_time_slot(professional_id, slot_date, start_time, end_time)
    return slot_id


# ---------------- GET PROFILE ----------------
def get_profile(user_id):
    return get_professional_by_user(user_id)

def get_my_services(professional_id):
    return get_services_for_professional(professional_id)


# ---------------- GET MY SLOTS ----------------
def get_my_slots(professional_id):
    return get_all_slots_by_professional(professional_id)


# ---------------- GET AVAILABLE SERVICES ----------------
def get_available_services():
    return get_all_services()
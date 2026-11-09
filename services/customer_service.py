# services/customer_service.py

from repositories.customer_repository import (
    get_services,
    get_professionals_by_service
)


# ---------------- VIEW SERVICES ----------------
def view_services():
    return get_services()


# ---------------- GET PROFESSIONALS FOR SERVICE ----------------
def get_professionals_for_service(service_id):
    return get_professionals_by_service(service_id)

# tests/integration/test_02_professional_setup_flow.py
# ============================================================
# INTEGRATION TEST — Professional Setup Component
#
# Simulates a professional's setup journey:
#   1. Create User & Profile
#   2. Admin approves profile
#   3. Link profile to a service
#   4. Add a time slot
# ============================================================

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from repositories.professional_repository import create_professional, add_professional_service, approve_professional
from repositories.service_repository import add_service
from repositories.time_slot_repository import add_time_slot
from services.auth_service import register_user
from database.db import get_connection


def test_professional_setup_flow(db_connection, unique_id):
    pro_user_id = None
    professional_id = None
    service_id = None
    slot_id = None
    ps_id = None

    try:
        # STEP 1: Create Professional Account & Profile
        pro_user_id = register_user(
            name=f"FlowPro_{unique_id}",
            email=f"pro_{unique_id}@test.com",
            phone="88" + unique_id,
            password="propass",
            role="professional"
        )
        assert pro_user_id is not None
        
        professional_id = create_professional(
            user_id=pro_user_id, experience=5, area="TestArea", work_radius=10
        )
        assert professional_id is not None

        # STEP 2: Admin Approval
        approve_professional(professional_id)

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT is_approved FROM professionals WHERE id = %s", (professional_id,))
        assert cursor.fetchone()["is_approved"] in (1, True)
        cursor.close()
        conn.close()

        # STEP 3: Setup Service Linking
        svc_name = f"TestSvc_{unique_id}"
        add_service(name=svc_name, description="Test", base_price=500, estimated_time="1 hr")
        
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id FROM services WHERE name = %s", (svc_name,))
        service_id = cursor.fetchone()["id"]
        cursor.close()
        conn.close()

        add_professional_service(professional_id, service_id, custom_price=750)

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id FROM professional_services WHERE professional_id = %s AND service_id = %s",
            (professional_id, service_id)
        )
        ps_row = cursor.fetchone()
        ps_id = ps_row["id"] if ps_row else None
        cursor.close()
        conn.close()

        # STEP 4: Add Time Slot
        slot_id = add_time_slot(professional_id, "2026-12-31", "14:00:00", "15:00:00")
        assert slot_id is not None

    finally:
        # CLEANUP
        conn = get_connection()
        cursor = conn.cursor()
        if ps_id: cursor.execute("DELETE FROM professional_services WHERE id = %s", (ps_id,))
        if slot_id: cursor.execute("DELETE FROM time_slots WHERE id = %s", (slot_id,))
        if professional_id: cursor.execute("DELETE FROM professionals WHERE id = %s", (professional_id,))
        if service_id: cursor.execute("DELETE FROM services WHERE id = %s", (service_id,))
        if pro_user_id: 
            cursor.execute("DELETE FROM otp_verification WHERE user_id = %s", (pro_user_id,))
            cursor.execute("DELETE FROM users WHERE id = %s", (pro_user_id,))
        conn.commit()
        cursor.close()
        conn.close()

"""
test_professional.py — Comprehensive tests for Professional Service layer.

Covers:
    - Profile creation (new, duplicate)
    - Service linking and pricing
    - Slot management (add, retrieve)
    - Profile retrieval (exists, non-existent)
    - Available services listing
    - Slot retrieval for professional with no slots

Database-dependent (uses live MySQL via test_utils).
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from services.professional_service import (
    create_profile,
    add_service_pricing,
    add_slot,
    get_profile,
    get_my_services,
    get_my_slots,
    get_available_services,
)
from tests.test_utils import (
    clear_test_data,
    create_raw_test_user,
    create_test_service,
)


class TestProfessionalProfileCreation(unittest.TestCase):
    """Tests for professional profile creation."""

    def setUp(self):
        clear_test_data()

    def tearDown(self):
        clear_test_data()

    def test_create_new_profile_returns_id(self):
        """Creating a new professional profile returns a valid ID."""
        u = create_raw_test_user("ProNew", "900", "professional")
        pid = create_profile(u['id'], 5, "TestArea", 15)
        self.assertIsNotNone(pid)
        self.assertIsInstance(pid, int)

    def test_create_duplicate_profile_returns_none(self):
        """Creating a profile for a user who already has one returns None."""
        u = create_raw_test_user("ProDup", "901", "professional")
        pid1 = create_profile(u['id'], 5, "Area1", 10)
        pid2 = create_profile(u['id'], 3, "Area2", 20)
        self.assertIsNotNone(pid1)
        self.assertIsNone(pid2)

    def test_profile_fields_stored_correctly(self):
        """Profile fields must match what was passed during creation."""
        u = create_raw_test_user("ProFields", "902", "professional")
        pid = create_profile(u['id'], 8, "Downtown", 25)
        profile = get_profile(u['id'])
        self.assertEqual(profile['experience'], 8)
        self.assertEqual(profile['area'], "Downtown")
        self.assertEqual(profile['work_radius'], 25)

    def test_new_profile_is_not_approved_by_default(self):
        """A freshly created profile must have is_approved=False."""
        u = create_raw_test_user("ProUnappr", "903", "professional")
        create_profile(u['id'], 2, "Suburb", 5)
        profile = get_profile(u['id'])
        self.assertEqual(profile['is_approved'], 0)


class TestProfessionalProfileRetrieval(unittest.TestCase):
    """Tests for profile retrieval edge cases."""

    def setUp(self):
        clear_test_data()

    def tearDown(self):
        clear_test_data()

    def test_get_profile_nonexistent_user_returns_none(self):
        """Getting profile for a user with no profile returns None."""
        u = create_raw_test_user("ProNone", "910", "professional")
        profile = get_profile(u['id'])
        self.assertIsNone(profile)

    def test_get_profile_existing_user(self):
        """Getting profile for a user with a profile returns dict."""
        u = create_raw_test_user("ProExist", "911", "professional")
        create_profile(u['id'], 3, "City", 10)
        profile = get_profile(u['id'])
        self.assertIsNotNone(profile)
        self.assertIn('id', profile)


class TestServicePricing(unittest.TestCase):
    """Tests for linking services and setting custom prices."""

    def setUp(self):
        clear_test_data()
        self.user = create_raw_test_user("ProSvc", "920", "professional")
        self.pid = create_profile(self.user['id'], 5, "TestArea", 15)

    def tearDown(self):
        clear_test_data()

    def test_add_service_pricing_links_correctly(self):
        """Adding a service pricing should link the service to the professional."""
        sid = create_test_service("Test Service PS1", 200.0)
        add_service_pricing(self.pid, sid, 250.0)
        services = get_my_services(self.pid)
        self.assertEqual(len(services), 1)
        self.assertEqual(services[0]['custom_price'], 250.0)

    def test_multiple_services_linked(self):
        """A professional can be linked to multiple services."""
        sid1 = create_test_service("Test Service PS2", 100.0)
        sid2 = create_test_service("Test Service PS3", 300.0)
        add_service_pricing(self.pid, sid1, 120.0)
        add_service_pricing(self.pid, sid2, 350.0)
        services = get_my_services(self.pid)
        self.assertEqual(len(services), 2)

    def test_get_my_services_when_none_linked(self):
        """Professional with no linked services returns empty list."""
        services = get_my_services(self.pid)
        self.assertEqual(len(services), 0)


class TestSlotManagement(unittest.TestCase):
    """Tests for time slot creation and retrieval."""

    def setUp(self):
        clear_test_data()
        self.user = create_raw_test_user("ProSlot", "930", "professional")
        self.pid = create_profile(self.user['id'], 4, "Area", 10)

    def tearDown(self):
        clear_test_data()

    def test_add_slot_returns_valid_id(self):
        """Adding a valid slot should return a slot ID."""
        slot_id = add_slot(self.pid, "2026-12-05", "10:00", "12:00")
        self.assertIsNotNone(slot_id)
        self.assertIsInstance(slot_id, int)

    def test_get_my_slots_returns_added_slots(self):
        """get_my_slots must return all slots for the professional."""
        add_slot(self.pid, "2026-12-05", "10:00", "12:00")
        add_slot(self.pid, "2026-12-06", "14:00", "16:00")
        slots = get_my_slots(self.pid)
        self.assertEqual(len(slots), 2)

    def test_get_my_slots_empty_for_no_slots(self):
        """Professional with no slots returns empty list."""
        slots = get_my_slots(self.pid)
        self.assertEqual(len(slots), 0)

    def test_slot_fields_stored_correctly(self):
        """Slot fields must match what was passed."""
        slot_id = add_slot(self.pid, "2026-12-10", "09:00", "11:00")
        slots = get_my_slots(self.pid)
        self.assertEqual(len(slots), 1)
        slot = slots[0]
        self.assertEqual(slot['id'], slot_id)
        self.assertEqual(slot['is_booked'], 0)


class TestAvailableServices(unittest.TestCase):
    """Tests for retrieving available services."""

    def setUp(self):
        clear_test_data()

    def tearDown(self):
        clear_test_data()

    def test_available_services_includes_created_service(self):
        """A created service should appear in available services."""
        sid = create_test_service("Test Service Avail1", 100.0)
        services = get_available_services()
        self.assertTrue(
            any(s['id'] == sid for s in services),
            "Newly created service must appear in available services"
        )

    def test_available_services_returns_list(self):
        """get_available_services must always return a list."""
        services = get_available_services()
        self.assertIsInstance(services, list)


if __name__ == '__main__':
    unittest.main()

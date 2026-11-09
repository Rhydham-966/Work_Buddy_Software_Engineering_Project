"""
test_customer.py — Comprehensive tests for Customer Service layer.

Covers:
    - View services (populated, empty)
    - Get professionals for service (approved only, no approved, invalid ID)
    - Professional filtering (unapproved must not appear)

Database-dependent (uses live MySQL via test_utils).
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from services.customer_service import view_services, get_professionals_for_service
from services.professional_service import create_profile, add_service_pricing
from tests.test_utils import (
    clear_test_data,
    create_raw_test_user,
    create_test_service,
)


class TestViewServices(unittest.TestCase):
    """Tests for customer service browsing."""

    def setUp(self):
        clear_test_data()

    def tearDown(self):
        clear_test_data()

    def test_view_services_returns_list(self):
        """view_services must always return a list."""
        services = view_services()
        self.assertIsInstance(services, list)

    def test_view_services_includes_created_service(self):
        """A created service must appear in the customer view."""
        sid = create_test_service("Test Service CV1", 100.0)
        services = view_services()
        self.assertTrue(any(s['id'] == sid for s in services))

    def test_view_services_contains_expected_fields(self):
        """Each service dict must have id, name, and base_price."""
        create_test_service("Test Service CV2", 200.0)
        services = view_services()
        self.assertGreater(len(services), 0)
        s = services[0]
        self.assertIn('id', s)
        self.assertIn('name', s)
        self.assertIn('base_price', s)


class TestGetProfessionalsForService(unittest.TestCase):
    """Tests for customer professional discovery."""

    def setUp(self):
        clear_test_data()
        self.sid = create_test_service("Test Service CustProf", 100.0)

    def tearDown(self):
        clear_test_data()

    def _approve_professional_in_db(self, professional_id):
        """Helper: directly approve a professional via DB."""
        from database.db import get_connection
        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE professionals SET is_approved=1 WHERE id=%s", (professional_id,))
        conn.commit()
        c.close()
        conn.close()

    def test_only_approved_professionals_returned(self):
        """Only approved professionals should appear for a service."""
        p_app = create_raw_test_user("CustPApp", "950", "professional")
        p_unapp = create_raw_test_user("CustPUnapp", "951", "professional")

        pid_app = create_profile(p_app['id'], 5, "Area1", 10)
        pid_unapp = create_profile(p_unapp['id'], 2, "Area2", 5)

        self._approve_professional_in_db(pid_app)

        add_service_pricing(pid_app, self.sid, 150.0)
        add_service_pricing(pid_unapp, self.sid, 120.0)

        profs = get_professionals_for_service(self.sid)
        self.assertEqual(len(profs), 1, "Only the approved professional should be returned")
        self.assertEqual(profs[0]['id'], pid_app)

    def test_no_professionals_for_service_returns_empty(self):
        """A service with no linked professionals returns empty list."""
        profs = get_professionals_for_service(self.sid)
        self.assertEqual(len(profs), 0)

    def test_nonexistent_service_id_returns_empty(self):
        """Querying professionals for a non-existent service returns empty."""
        profs = get_professionals_for_service(99999)
        self.assertEqual(len(profs), 0)

    def test_professional_fields_in_response(self):
        """Response must include professional details with custom_price."""
        p = create_raw_test_user("CustPFields", "952", "professional")
        pid = create_profile(p['id'], 7, "CityCenter", 20)
        self._approve_professional_in_db(pid)
        add_service_pricing(pid, self.sid, 180.0)

        profs = get_professionals_for_service(self.sid)
        self.assertEqual(len(profs), 1)
        prof = profs[0]
        self.assertIn('id', prof)
        self.assertIn('name', prof)
        self.assertIn('custom_price', prof)
        self.assertEqual(prof['custom_price'], 180.0)


if __name__ == '__main__':
    unittest.main()

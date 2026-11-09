"""
test_admin.py — Comprehensive tests for the Admin Service layer.

Covers:
    - Add service (unique, duplicate)
    - Approve professional (valid, non-existent)
    - Reject professional (deletion verification)
    - Pending professionals list changes after approval

Database-dependent (uses live MySQL via test_utils).
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from services.admin_service import add_service, approve_professional
from repositories.professional_repository import (
    get_professional_by_user,
    get_pending_professionals,
    reject_professional as repo_reject_professional,
)
from tests.test_utils import (
    clear_test_data,
    create_raw_test_user,
    create_test_professional,
)


class TestAddService(unittest.TestCase):
    """Tests for admin service creation."""

    def setUp(self):
        clear_test_data()

    def tearDown(self):
        clear_test_data()

    def test_add_unique_service_succeeds(self):
        """Adding a service with a unique name should succeed."""
        success, msg = add_service("Test Service Admin1", "desc", 50.0, "1 hr")
        self.assertTrue(success)
        self.assertIn("successfully", msg.lower())

    def test_add_duplicate_service_fails(self):
        """Adding a service with a name that already exists should fail."""
        add_service("Test Service AdminDup", "desc1", 50.0, "1 hr")
        success, msg = add_service("Test Service AdminDup", "desc2", 100.0, "2 hr")
        self.assertFalse(success)
        self.assertIn("already exists", msg)

    def test_add_service_with_zero_price(self):
        """A service with base_price=0 should still be addable."""
        success, _ = add_service("Test Service FreeAdmin", "free", 0.0, "30 min")
        self.assertTrue(success)

    def test_add_service_returns_tuple(self):
        """add_service must return a (bool, str) tuple."""
        result = add_service("Test Service Tuple", "t", 10.0, "1 hr")
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)


class TestApproveProfessional(unittest.TestCase):
    """Tests for admin professional approval flow."""

    def setUp(self):
        clear_test_data()

    def tearDown(self):
        clear_test_data()

    def test_approve_pending_professional_succeeds(self):
        """Approving a pending professional should set is_approved=1."""
        u = create_raw_test_user("AdminAppr", "800")
        pid = create_test_professional(u['id'], is_approved=False)

        pro_before = get_professional_by_user(u['id'])
        self.assertEqual(pro_before['is_approved'], 0)

        success, msg = approve_professional(pid)
        self.assertTrue(success)

        pro_after = get_professional_by_user(u['id'])
        self.assertEqual(pro_after['is_approved'], 1)

    def test_approve_already_approved_professional_still_succeeds(self):
        """Approving an already-approved professional should not crash."""
        u = create_raw_test_user("AdminReAppr", "801")
        pid = create_test_professional(u['id'], is_approved=True)

        success, msg = approve_professional(pid)
        self.assertTrue(success)

    def test_pending_list_shrinks_after_approval(self):
        """After approving a professional, they should leave the pending list."""
        u = create_raw_test_user("AdminPend", "802")
        pid = create_test_professional(u['id'], is_approved=False)

        pending_before = get_pending_professionals()
        self.assertTrue(any(p['id'] == pid for p in pending_before))

        approve_professional(pid)

        pending_after = get_pending_professionals()
        self.assertFalse(any(p['id'] == pid for p in pending_after))


class TestRejectProfessional(unittest.TestCase):
    """Tests for admin professional rejection (deletion) flow."""

    def setUp(self):
        clear_test_data()

    def tearDown(self):
        clear_test_data()

    def test_reject_professional_deletes_record(self):
        """Rejecting a professional should DELETE their record."""
        u = create_raw_test_user("AdminRej", "810")
        pid = create_test_professional(u['id'], is_approved=False)

        pro_before = get_professional_by_user(u['id'])
        self.assertIsNotNone(pro_before)

        repo_reject_professional(pid)

        pro_after = get_professional_by_user(u['id'])
        self.assertIsNone(pro_after)

    def test_reject_removes_from_pending_list(self):
        """After rejection, professional must not appear in pending list."""
        u = create_raw_test_user("AdminRejPend", "811")
        pid = create_test_professional(u['id'], is_approved=False)

        repo_reject_professional(pid)

        pending = get_pending_professionals()
        self.assertFalse(any(p['id'] == pid for p in pending))


if __name__ == '__main__':
    unittest.main()

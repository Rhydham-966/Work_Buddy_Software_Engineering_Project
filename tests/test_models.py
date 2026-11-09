"""
test_models.py — Pure unit tests for all dataclass models.

Covers:
    - ABC enforcement on User
    - Inheritance hierarchy (Customer, Admin, ServiceProfessional)
    - Dataclass default values
    - Polymorphism via isinstance checks
    - Boundary value analysis (IDs, prices, ratings)
    - Immutability semantics at the object level

No database dependency.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import math
from models.user import User
from models.customer import Customer
from models.professional import ServiceProfessional
from models.admin import Admin
from models.booking import Booking
from models.service import Service


# ══════════════════════════════════════════════════════════
#  USER (Abstract Base Class)
# ══════════════════════════════════════════════════════════
class TestUserABC(unittest.TestCase):
    """Verify User's abstract base class design."""

    def test_user_inherits_from_abc(self):
        """User must be declared as a subclass of ABC."""
        from abc import ABC
        self.assertTrue(issubclass(User, ABC))

    def test_user_instantiation_without_abstractmethod(self):
        """User has no @abstractmethod, so direct instantiation is allowed.
        This test documents the current behavior — the ABC marker is a
        design signal, not an enforced constraint."""
        u = User(id=1, name="Ghost", phone="000")
        self.assertEqual(u.name, "Ghost")


# ══════════════════════════════════════════════════════════
#  CUSTOMER
# ══════════════════════════════════════════════════════════
class TestCustomerModel(unittest.TestCase):
    """Tests for the Customer dataclass."""

    def setUp(self):
        self.customer = Customer(id=1, name="Alice", phone="9876543210")

    def test_customer_inherits_from_user(self):
        self.assertTrue(issubclass(Customer, User))

    def test_customer_isinstance_of_user(self):
        self.assertIsInstance(self.customer, User)

    def test_customer_field_access(self):
        self.assertEqual(self.customer.id, 1)
        self.assertEqual(self.customer.name, "Alice")
        self.assertEqual(self.customer.phone, "9876543210")

    def test_customer_is_not_admin(self):
        self.assertNotIsInstance(self.customer, Admin)

    def test_customer_is_not_service_professional(self):
        self.assertNotIsInstance(self.customer, ServiceProfessional)

    def test_customer_with_zero_id(self):
        c = Customer(id=0, name="Zero", phone="000")
        self.assertEqual(c.id, 0)

    def test_customer_with_negative_id(self):
        c = Customer(id=-1, name="Neg", phone="111")
        self.assertEqual(c.id, -1)

    def test_customer_with_empty_name(self):
        c = Customer(id=2, name="", phone="222")
        self.assertEqual(c.name, "")

    def test_customer_equality(self):
        """Dataclass equality is field-based."""
        c1 = Customer(id=1, name="Alice", phone="999")
        c2 = Customer(id=1, name="Alice", phone="999")
        self.assertEqual(c1, c2)

    def test_customer_inequality(self):
        c1 = Customer(id=1, name="Alice", phone="999")
        c2 = Customer(id=2, name="Bob", phone="888")
        self.assertNotEqual(c1, c2)


# ══════════════════════════════════════════════════════════
#  SERVICE PROFESSIONAL
# ══════════════════════════════════════════════════════════
class TestServiceProfessionalModel(unittest.TestCase):
    """Tests for ServiceProfessional dataclass defaults and boundaries."""

    def setUp(self):
        self.pro = ServiceProfessional(id=10, name="John", phone="1234567890")

    def test_professional_inherits_from_user(self):
        self.assertTrue(issubclass(ServiceProfessional, User))

    def test_professional_isinstance_of_user(self):
        self.assertIsInstance(self.pro, User)

    def test_default_rating_is_zero(self):
        self.assertEqual(self.pro.rating, 0.0)

    def test_default_available_is_true(self):
        self.assertTrue(self.pro.available)

    def test_default_work_area_is_none(self):
        self.assertIsNone(self.pro.work_area)

    def test_custom_rating(self):
        p = ServiceProfessional(id=11, name="Jane", phone="555", rating=4.5)
        self.assertEqual(p.rating, 4.5)

    def test_rating_boundary_zero(self):
        p = ServiceProfessional(id=12, name="X", phone="0", rating=0.0)
        self.assertEqual(p.rating, 0.0)

    def test_rating_boundary_max_five(self):
        p = ServiceProfessional(id=13, name="X", phone="0", rating=5.0)
        self.assertEqual(p.rating, 5.0)

    def test_rating_negative_value_stored(self):
        """Model does not enforce constraints — negative rating is stored."""
        p = ServiceProfessional(id=14, name="X", phone="0", rating=-1.0)
        self.assertEqual(p.rating, -1.0)

    def test_rating_infinity_stored(self):
        """Model does not enforce constraints — infinity is stored."""
        p = ServiceProfessional(id=15, name="X", phone="0", rating=float('inf'))
        self.assertTrue(math.isinf(p.rating))

    def test_rating_nan_stored(self):
        """Model does not enforce constraints — NaN is stored."""
        p = ServiceProfessional(id=16, name="X", phone="0", rating=float('nan'))
        self.assertTrue(math.isnan(p.rating))

    def test_set_available_false(self):
        p = ServiceProfessional(id=17, name="X", phone="0", available=False)
        self.assertFalse(p.available)

    def test_set_work_area(self):
        p = ServiceProfessional(id=18, name="X", phone="0", work_area="Downtown")
        self.assertEqual(p.work_area, "Downtown")

    def test_professional_is_not_customer(self):
        self.assertNotIsInstance(self.pro, Customer)

    def test_professional_is_not_admin(self):
        self.assertNotIsInstance(self.pro, Admin)


# ══════════════════════════════════════════════════════════
#  ADMIN
# ══════════════════════════════════════════════════════════
class TestAdminModel(unittest.TestCase):
    """Tests for the Admin dataclass."""

    def setUp(self):
        self.admin = Admin(id=99, name="SuperAdmin", phone="0000000000")

    def test_admin_inherits_from_user(self):
        self.assertTrue(issubclass(Admin, User))

    def test_admin_isinstance_of_user(self):
        self.assertIsInstance(self.admin, User)

    def test_admin_field_access(self):
        self.assertEqual(self.admin.id, 99)
        self.assertEqual(self.admin.name, "SuperAdmin")

    def test_admin_is_not_customer(self):
        self.assertNotIsInstance(self.admin, Customer)

    def test_admin_is_not_professional(self):
        self.assertNotIsInstance(self.admin, ServiceProfessional)


# ══════════════════════════════════════════════════════════
#  POLYMORPHISM CROSS-CHECK
# ══════════════════════════════════════════════════════════
class TestUserPolymorphism(unittest.TestCase):
    """Verify polymorphic behavior across the User hierarchy."""

    def test_all_subclasses_are_users(self):
        instances = [
            Customer(id=1, name="C", phone="1"),
            ServiceProfessional(id=2, name="P", phone="2"),
            Admin(id=3, name="A", phone="3"),
        ]
        for obj in instances:
            with self.subTest(obj=type(obj).__name__):
                self.assertIsInstance(obj, User)

    def test_subclasses_are_distinct_types(self):
        c = Customer(id=1, name="C", phone="1")
        p = ServiceProfessional(id=2, name="P", phone="2")
        a = Admin(id=3, name="A", phone="3")
        self.assertNotIsInstance(c, type(p))
        self.assertNotIsInstance(c, type(a))
        self.assertNotIsInstance(p, type(a))


# ══════════════════════════════════════════════════════════
#  SERVICE
# ══════════════════════════════════════════════════════════
class TestServiceModel(unittest.TestCase):
    """Tests for the Service dataclass."""

    def test_service_creation(self):
        s = Service(id=1, name="Plumbing", base_price=500.0, category="Home")
        self.assertEqual(s.id, 1)
        self.assertEqual(s.name, "Plumbing")
        self.assertEqual(s.base_price, 500.0)
        self.assertEqual(s.category, "Home")

    def test_service_price_zero(self):
        s = Service(id=2, name="Free", base_price=0.0, category="Promo")
        self.assertEqual(s.base_price, 0.0)

    def test_service_price_negative_stored(self):
        """Model layer does not validate — negative price is stored."""
        s = Service(id=3, name="Bug", base_price=-100.0, category="Error")
        self.assertEqual(s.base_price, -100.0)

    def test_service_price_infinity_stored(self):
        s = Service(id=4, name="Inf", base_price=float('inf'), category="Test")
        self.assertTrue(math.isinf(s.base_price))

    def test_service_price_very_large(self):
        s = Service(id=5, name="Luxury", base_price=9999999.99, category="Premium")
        self.assertEqual(s.base_price, 9999999.99)

    def test_service_empty_name(self):
        s = Service(id=6, name="", base_price=100.0, category="")
        self.assertEqual(s.name, "")

    def test_service_equality(self):
        s1 = Service(id=1, name="A", base_price=100.0, category="X")
        s2 = Service(id=1, name="A", base_price=100.0, category="X")
        self.assertEqual(s1, s2)


# ══════════════════════════════════════════════════════════
#  BOOKING
# ══════════════════════════════════════════════════════════
class TestBookingModel(unittest.TestCase):
    """Tests for the Booking dataclass."""

    def test_booking_creation_with_defaults(self):
        b = Booking(id=1, customer_id=10, service_id=20, time_slot="10:00-11:00")
        self.assertEqual(b.status, "CREATED")
        self.assertIsNone(b.professional_id)

    def test_booking_with_professional_assigned(self):
        b = Booking(id=2, customer_id=10, service_id=20, time_slot="12:00-13:00", professional_id=5)
        self.assertEqual(b.professional_id, 5)

    def test_booking_custom_status(self):
        b = Booking(id=3, customer_id=10, service_id=20, time_slot="14:00", status="CONFIRMED")
        self.assertEqual(b.status, "CONFIRMED")

    def test_booking_zero_ids(self):
        b = Booking(id=0, customer_id=0, service_id=0, time_slot="")
        self.assertEqual(b.id, 0)

    def test_booking_negative_ids(self):
        b = Booking(id=-1, customer_id=-1, service_id=-1, time_slot="x")
        self.assertEqual(b.id, -1)

    def test_booking_equality(self):
        b1 = Booking(id=1, customer_id=10, service_id=20, time_slot="10:00")
        b2 = Booking(id=1, customer_id=10, service_id=20, time_slot="10:00")
        self.assertEqual(b1, b2)

    def test_booking_status_mutation(self):
        """Dataclass fields are mutable by default — verify mutation works."""
        b = Booking(id=1, customer_id=10, service_id=20, time_slot="10:00")
        b.status = "COMPLETED"
        self.assertEqual(b.status, "COMPLETED")


if __name__ == '__main__':
    unittest.main()

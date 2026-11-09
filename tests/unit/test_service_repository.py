# tests/unit/test_service_repository.py
# ============================================================
# Unit tests for repositories/service_repository.py
# Tests: add_service, get_all_services
# Uses REAL MySQL — no mocking.
# ============================================================

import sys                                          # for path manipulation
import os                                           # for path joining

# -- Ensure project root is importable --
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from repositories.service_repository import (       # import functions under test
    add_service,                                    # inserts a new service row
    get_all_services                                # fetches all service rows
)
from database.db import get_connection              # direct DB access for cleanup


# ============================================================
# HELPER: unique values
# ============================================================


# ============================================================
# TEST 1: add_service — successful insertion
# ============================================================
def test_add_service_inserts_row(db_connection, unique_id):
    """add_service should create a new row in the services table."""
    service_name = f"Svc_{unique_id}"               # unique service name
    description = "Test service description"        # description text
    base_price = 250.00                             # sample base price
    estimated_time = "45 minutes"                   # sample time estimate

    add_service(                                    # call repository function
        name=service_name,                          # service name
        description=description,                    # description
        base_price=base_price,                      # price
        estimated_time=estimated_time               # time
    )

    # -- Verify the service exists in the DB --
    conn = get_connection()                         # get fresh connection
    cursor = conn.cursor(dictionary=True)           # dictionary cursor
    cursor.execute(                                 # query by exact name
        "SELECT * FROM services WHERE name = %s",
        (service_name,)
    )
    row = cursor.fetchone()                         # should be exactly one match

    assert row is not None, "Service must exist after add_service"  # row was inserted
    assert row["name"] == service_name, "Name must match"           # correct name
    assert float(row["base_price"]) == base_price, "Price must match"  # correct price
    assert row["estimated_time"] == estimated_time, "Time must match"  # correct time

    # -- CLEANUP: remove the test service --
    cursor.execute("DELETE FROM services WHERE id = %s", (row["id"],))  # delete by ID
    conn.commit()                                   # persist deletion
    cursor.close()                                  # close cursor
    conn.close()                                    # close connection


# ============================================================
# TEST 2: get_all_services — returns a list
# ============================================================
def test_get_all_services_returns_list(db_connection, unique_id):
    """get_all_services should return a list (possibly empty)."""
    services = get_all_services()                   # call repository function

    assert isinstance(services, list), "Must return a list"  # type check
    # Note: list may be empty if no services exist, which is valid


# ============================================================
# TEST 3: get_all_services — includes newly added service
# ============================================================
def test_get_all_services_includes_new(db_connection, unique_id):
    """A newly added service should appear in get_all_services results."""
    service_name = f"SvcAll_{unique_id}"            # unique name
    service_id = None                               # track for cleanup

    try:
        # -- Insert a service --
        add_service(                                # add via repository
            name=service_name,                      # unique name
            description="For get_all test",         # description
            base_price=100.00,                      # price
            estimated_time="30 minutes"             # time
        )

        # -- Fetch the ID for cleanup --
        conn = get_connection()                     # fresh connection
        cursor = conn.cursor(dictionary=True)       # dictionary cursor
        cursor.execute(                             # find the row
            "SELECT id FROM services WHERE name = %s", (service_name,)
        )
        row = cursor.fetchone()                     # get the inserted row
        service_id = row["id"] if row else None     # store ID for cleanup
        cursor.close()                              # close cursor
        conn.close()                                # close connection

        # -- Verify it appears in get_all_services --
        all_services = get_all_services()           # fetch all services
        names = [s["name"] for s in all_services]   # extract all names

        assert service_name in names, \
            "Newly added service must appear in get_all_services"  # must be present
    finally:
        # -- CLEANUP --
        if service_id:                              # if we know the ID
            conn = get_connection()                 # get connection
            cursor = conn.cursor()                  # open cursor
            cursor.execute(                         # delete the row
                "DELETE FROM services WHERE id = %s", (service_id,)
            )
            conn.commit()                           # persist
            cursor.close()                          # close cursor
            conn.close()                            # close connection


# ============================================================
# TEST 4: get_all_services — each row has required keys
# ============================================================
def test_get_all_services_row_keys(db_connection, test_service):
    """Each service dict should have id, name, description, base_price, estimated_time."""
    all_services = get_all_services()               # fetch all services

    assert len(all_services) > 0, \
        "At least one service should exist (from test_service fixture)"  # at least the fixture

    # -- Check keys on the first service --
    sample = all_services[0]                        # grab one row
    required_keys = ["id", "name", "description", "base_price", "estimated_time"]
    for key in required_keys:                       # iterate required keys
        assert key in sample, f"Service dict must contain key '{key}'"  # must be present

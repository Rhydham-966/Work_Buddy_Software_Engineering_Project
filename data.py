import mysql.connector

from database.db import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

# Using variables from database/db.py to align with the database model
db_config = {
    'host': DB_HOST,
    'user': DB_USER,
    'password': DB_PASSWORD,
    'database': DB_NAME
}

def seed_data():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    print("--- STARTING SEED DATA GENERATION ---")

    # Clear old data for a fresh state (Safely ignoring Foreign Keys temporarily)
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    cursor.execute("TRUNCATE TABLE bookings;")
    cursor.execute("TRUNCATE TABLE time_slots;")
    cursor.execute("TRUNCATE TABLE professional_services;")
    cursor.execute("TRUNCATE TABLE professionals;")
    cursor.execute("TRUNCATE TABLE services;")
    cursor.execute("TRUNCATE TABLE otp_verification;")
    cursor.execute("TRUNCATE TABLE users;")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
    conn.commit()

    # 1. Insert Users: 1 Admin, 3 Professionals, 5 Customers
    users_data = [
        ("Admin Master", "admin@wb.com", "admin1", "pass", "admin", True),
        # Professionals
        ("Pro John (Plumber)", "p1@wb.com", "pro1", "pass", "professional", True),
        ("Pro Mike (Electrician)", "p2@wb.com", "pro2", "pass", "professional", True),
        ("Pro Sarah (Cleaner)", "p3@wb.com", "pro3", "pass", "professional", True),
        # Customers
        ("Cust Alice", "c1@wb.com", "cust1", "pass", "customer", True),
        ("Cust Bob", "c2@wb.com", "cust2", "pass", "customer", True),
        ("Cust Charlie", "c3@wb.com", "cust3", "pass", "customer", True),
        ("Cust Diana", "c4@wb.com", "cust4", "pass", "customer", True),
        ("Cust Eve", "c5@wb.com", "cust5", "pass", "customer", True),
    ]

    for u in users_data:
        cursor.execute("INSERT INTO users (name, email, phone, password, role, is_verified) VALUES (%s, %s, %s, %s, %s, %s)", u)
    conn.commit()

    # Get created user IDs
    cursor.execute("SELECT id, role, phone FROM users")
    all_users = cursor.fetchall()

    pro_users = [u[0] for u in all_users if u[1] == 'professional']
    cust_users = [u[0] for u in all_users if u[1] == 'customer']

    # 2. Insert Services (3 Services)
    services_data = [
        ("Plumbing Repair", "Fix leaks and pipes", 500.00, "2 hours"),
        ("Electrical Fix", "Wiring and appliances", 800.00, "3 hours"),
        ("Deep Cleaning", "Full house wash", 1200.00, "5 hours")
    ]
    for s in services_data:
        cursor.execute("INSERT INTO services (name, description, base_price, estimated_time) VALUES (%s, %s, %s, %s)", s)
    conn.commit()

    cursor.execute("SELECT id FROM services ORDER BY id")
    service_ids = [s[0] for s in cursor.fetchall()]

    # 3. Create Professional Profiles (3 Professionals) and Map via `professional_services`
    for i, p_uid in enumerate(pro_users):
        # Insert profile
        cursor.execute("INSERT INTO professionals (user_id, experience, area, work_radius, is_approved) VALUES (%s, %s, %s, %s, TRUE)",
                       (p_uid, 5 + i, "Downtown", 10 + (2*i)))
        pro_id = cursor.lastrowid
        
        # Link to 1 specific service logic
        s_id = service_ids[i % len(service_ids)]
        custom_price = 500.00 + (100 * i)
        cursor.execute("INSERT INTO professional_services (professional_id, service_id, custom_price) VALUES (%s, %s, %s)",
                       (pro_id, s_id, custom_price))
    conn.commit()

    cursor.execute("SELECT id, user_id FROM professionals")
    pro_profiles = cursor.fetchall()

    # 4. Insert Time Slots (5 slots dynamically distributed)
    slot_ids = []
    for i in range(5):
        prof_id = pro_profiles[i % len(pro_profiles)][0]
        date_str = f"2026-12-0{i+1}"
        start_t = f"10:00:0{i}"
        end_t = f"12:00:0{i}"
        
        cursor.execute("INSERT INTO time_slots (professional_id, slot_date, start_time, end_time, is_booked) VALUES (%s, %s, %s, %s, FALSE)",
                       (prof_id, date_str, start_t, end_t))
        slot_ids.append(cursor.lastrowid)
    conn.commit()

    # 5. Insert Bookings (3 bookings) + Invoices
    for i in range(3):
        # Random distribution
        c_id = cust_users[i]
        p_id = pro_profiles[i][0]
        s_id = service_ids[i]
        sl_id = slot_ids[i]

        # Grab exact price
        cursor.execute("SELECT custom_price FROM professional_services WHERE professional_id=%s AND service_id=%s", (p_id, s_id))
        res = cursor.fetchone()
        price = res[0] if res else 500.00

        cursor.execute("""
            INSERT INTO bookings (user_id, professional_id, service_id, time_slot_id, booking_type, status)
            VALUES (%s, %s, %s, %s, 'scheduled', 'accepted')
        """, (c_id, p_id, s_id, sl_id))
        b_id = cursor.lastrowid
        
        # Mark slot as booked
        cursor.execute("UPDATE time_slots SET is_booked = TRUE WHERE id = %s", (sl_id,))

    conn.commit()
    cursor.close()
    conn.close()

    print("SEED DATA CREATED SUCCESSFULLY!")
    print("\nUse the following test logins (Role / Phone / password):")
    print("Admin: 'admin1' / pass")
    print("Professionals: 'pro1', 'pro2', 'pro3' / pass")
    print("Customers: 'cust1', 'cust2', 'cust3' / pass")

if __name__ == "__main__":
    seed_data()

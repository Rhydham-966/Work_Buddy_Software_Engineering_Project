# repositories/booking_repository.py

from database.db import get_connection

def create_booking(customer_id, professional_id, service_id, slot_id, booking_type, scheduled_datetime, payment_method, payment_status, total_price):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO bookings (user_id, professional_id, service_id, time_slot_id, booking_type, scheduled_datetime, status, payment_method, payment_status, total_price)
    VALUES (%s, %s, %s, %s, %s, %s, 'pending', %s, %s, %s)
    """

    cursor.execute(query, (customer_id, professional_id, service_id, slot_id, booking_type, scheduled_datetime, payment_method, payment_status, total_price))
    conn.commit()

    booking_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return booking_id

def get_bookings_by_customer(customer_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT b.id, b.user_id, b.professional_id, b.service_id, b.time_slot_id,
           b.booking_type, b.scheduled_datetime, b.status, b.payment_method, b.payment_status, b.total_price, b.created_at,
           s.name AS service_name, u.name AS professional_name,
           ts.slot_date, ts.start_time, ts.end_time
    FROM bookings b
    JOIN services s ON b.service_id = s.id
    JOIN professionals p ON b.professional_id = p.id
    JOIN users u ON p.user_id = u.id
    LEFT JOIN time_slots ts ON b.time_slot_id = ts.id
    WHERE b.user_id = %s AND b.is_active = TRUE
    ORDER BY b.created_at DESC
    """

    cursor.execute(query, (customer_id,))
    bookings = cursor.fetchall()
    cursor.close()
    conn.close()
    return bookings

def get_bookings_by_professional(professional_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT b.id, b.user_id, b.professional_id, b.service_id, b.time_slot_id,
           b.booking_type, b.scheduled_datetime, b.status, b.payment_method, b.payment_status, b.total_price, b.created_at,
           s.name AS service_name, u.name AS customer_name,
           ts.slot_date, ts.start_time, ts.end_time
    FROM bookings b
    JOIN services s ON b.service_id = s.id
    JOIN users u ON b.user_id = u.id
    LEFT JOIN time_slots ts ON b.time_slot_id = ts.id
    WHERE b.professional_id = %s AND b.is_active = TRUE
    ORDER BY b.created_at DESC
    """

    cursor.execute(query, (professional_id,))
    bookings = cursor.fetchall()
    cursor.close()
    conn.close()
    return bookings

def mark_slot_booked(slot_id):
    conn = get_connection()
    cursor = conn.cursor()
    query = "UPDATE time_slots SET is_booked = TRUE WHERE id = %s"
    cursor.execute(query, (slot_id,))
    conn.commit()
    cursor.close()
    conn.close()

def get_booking_by_id(booking_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM bookings WHERE id = %s", (booking_id,))
    booking = cursor.fetchone()
    cursor.close()
    conn.close()
    return booking

def update_booking_status(booking_id, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE bookings SET status = %s WHERE id = %s", (status, booking_id))
    conn.commit()
    cursor.close()
    conn.close()

def update_payment_status(booking_id, payment_status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE bookings SET payment_status = %s WHERE id = %s", (payment_status, booking_id))
    conn.commit()
    cursor.close()
    conn.close()

def unmark_slot_booked(slot_id):
    if not slot_id:
        return
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE time_slots SET is_booked = FALSE WHERE id = %s", (slot_id,))
    conn.commit()
    cursor.close()
    conn.close()

def deactivate_booking(booking_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE bookings SET is_active = FALSE WHERE id = %s", (booking_id,))
    conn.commit()
    cursor.close()
    conn.close()

def get_booking_history_by_customer(customer_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT b.id, b.user_id, b.professional_id, b.service_id, b.time_slot_id,
           b.booking_type, b.scheduled_datetime, b.status, b.payment_method, b.payment_status, b.total_price, b.created_at,
           s.name AS service_name, u.name AS professional_name,
           ts.slot_date, ts.start_time, ts.end_time
    FROM bookings b
    JOIN services s ON b.service_id = s.id
    JOIN professionals p ON b.professional_id = p.id
    JOIN users u ON p.user_id = u.id
    LEFT JOIN time_slots ts ON b.time_slot_id = ts.id
    WHERE b.user_id = %s AND b.is_active = FALSE
    ORDER BY b.created_at DESC
    """

    cursor.execute(query, (customer_id,))
    bookings = cursor.fetchall()
    cursor.close()
    conn.close()
    return bookings

def get_booking_history_by_professional(professional_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT b.id, b.user_id, b.professional_id, b.service_id, b.time_slot_id,
           b.booking_type, b.scheduled_datetime, b.status, b.payment_method, b.payment_status, b.total_price, b.created_at,
           s.name AS service_name, u.name AS customer_name,
           ts.slot_date, ts.start_time, ts.end_time
    FROM bookings b
    JOIN services s ON b.service_id = s.id
    JOIN users u ON b.user_id = u.id
    LEFT JOIN time_slots ts ON b.time_slot_id = ts.id
    WHERE b.professional_id = %s AND b.is_active = FALSE
    ORDER BY b.created_at DESC
    """

    cursor.execute(query, (professional_id,))
    bookings = cursor.fetchall()
    cursor.close()
    conn.close()
    return bookings
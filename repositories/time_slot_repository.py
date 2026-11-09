# repositories/time_slot_repository.py

from database.db import get_connection


def add_time_slot(professional_id, slot_date, start_time, end_time):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO time_slots (professional_id, slot_date, start_time, end_time, is_booked)
    VALUES (%s, %s, %s, %s, FALSE)
    """

    cursor.execute(query, (professional_id, slot_date, start_time, end_time))
    conn.commit()

    slot_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return slot_id


def get_available_slots(professional_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT * FROM time_slots
    WHERE professional_id = %s AND is_booked = FALSE
    ORDER BY slot_date, start_time
    """

    cursor.execute(query, (professional_id,))
    slots = cursor.fetchall()

    cursor.close()
    conn.close()

    return slots


def get_all_slots_by_professional(professional_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT * FROM time_slots
    WHERE professional_id = %s
    ORDER BY slot_date, start_time
    """

    cursor.execute(query, (professional_id,))
    slots = cursor.fetchall()

    cursor.close()
    conn.close()

    return slots


def get_nearest_available_slot(professional_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT * FROM time_slots
    WHERE professional_id = %s AND is_booked = FALSE
    ORDER BY slot_date, start_time
    LIMIT 1
    """

    cursor.execute(query, (professional_id,))
    slot = cursor.fetchone()

    cursor.close()
    conn.close()

    return slot


def mark_slot_booked(slot_id):
    conn = get_connection()
    cursor = conn.cursor()

    query = "UPDATE time_slots SET is_booked = TRUE WHERE id = %s"
    cursor.execute(query, (slot_id,))
    conn.commit()

    cursor.close()
    conn.close()

def get_slot_by_id(slot_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM time_slots WHERE id = %s", (slot_id,))
    slot = cursor.fetchone()
    cursor.close()
    conn.close()
    return slot

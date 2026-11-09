# repositories/invoice_repository.py

from database.db import get_connection

def create_invoice(booking_id, amount, payment_method, payment_status):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO invoices (booking_id, amount, payment_method, payment_status)
    VALUES (%s, %s, %s, %s)
    """

    cursor.execute(query, (booking_id, amount, payment_method, payment_status))
    conn.commit()

    invoice_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return invoice_id

def get_invoice_by_booking(booking_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Grabbing the latest invoice if multiple exist (due to duplicate completions etc)
    query = "SELECT * FROM invoices WHERE booking_id = %s ORDER BY id DESC LIMIT 1"
    cursor.execute(query, (booking_id,))
    
    invoice = cursor.fetchone()

    cursor.close()
    conn.close()

    return invoice

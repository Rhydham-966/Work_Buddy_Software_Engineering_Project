# repositories/otp_repository.py

from database.db import get_connection
from datetime import datetime, timedelta


def create_otp(user_id, otp_code):
    conn = get_connection()
    cursor = conn.cursor()

    expiry_time = datetime.now() + timedelta(minutes=5)

    query = """
    INSERT INTO otp_verification (user_id, otp_code, expiry_time, is_used)
    VALUES (%s, %s, %s, FALSE)
    """

    cursor.execute(query, (user_id, otp_code, expiry_time))
    conn.commit()

    cursor.close()
    conn.close()


def get_valid_otp(user_id, otp_code):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT * FROM otp_verification
    WHERE user_id = %s AND otp_code = %s AND is_used = FALSE
    ORDER BY id DESC LIMIT 1
    """

    cursor.execute(query, (user_id, otp_code))
    otp = cursor.fetchone()

    cursor.close()
    conn.close()

    return otp


def mark_otp_used(otp_id):
    conn = get_connection()
    cursor = conn.cursor()

    query = "UPDATE otp_verification SET is_used = TRUE WHERE id = %s"
    cursor.execute(query, (otp_id,))
    conn.commit()

    cursor.close()
    conn.close()



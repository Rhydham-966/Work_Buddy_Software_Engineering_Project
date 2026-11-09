# repositories/user_repository.py

from database.db import get_connection


def create_user(name, email, phone, password, role):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO users (name, email, phone, password, role, is_verified)
    VALUES (%s, %s, %s, %s, %s, FALSE)
    """

    cursor.execute(query, (name, email, phone, password, role))
    conn.commit()

    user_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return user_id


def get_user_by_phone(phone):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM users WHERE phone = %s"
    cursor.execute(query, (phone,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return user


def verify_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    query = "UPDATE users SET is_verified = TRUE WHERE id = %s"
    cursor.execute(query, (user_id,))
    conn.commit()

    cursor.close()
    conn.close()

def get_user_by_id(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM users WHERE id = %s"
    cursor.execute(query, (user_id,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return user
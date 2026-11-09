# repositories/professional_repository.py

from database.db import get_connection


def create_professional(user_id, experience, area, work_radius):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO professionals (user_id, experience, area, work_radius, is_approved)
    VALUES (%s, %s, %s, %s, FALSE)
    """

    cursor.execute(query, (user_id, experience, area, work_radius))
    conn.commit()

    professional_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return professional_id


def add_professional_service(professional_id, service_id, custom_price):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO professional_services (professional_id, service_id, custom_price)
    VALUES (%s, %s, %s)
    """

    # Ignore ON DUPLICATE constraint silently for prototype simplicity
    try:
        cursor.execute(query, (professional_id, service_id, custom_price))
        conn.commit()
    except Exception as e:
        print("Notice:", e)

    cursor.close()
    conn.close()


def get_professional_by_user(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM professionals WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    professional = cursor.fetchone()

    cursor.close()
    conn.close()

    return professional

def get_services_for_professional(professional_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT ps.custom_price, s.name, s.id as service_id
    FROM professional_services ps
    JOIN services s ON ps.service_id = s.id
    WHERE ps.professional_id = %s
    """
    cursor.execute(query, (professional_id,))
    services = cursor.fetchall()

    cursor.close()
    conn.close()
    return services

def get_approved_professionals_by_service(service_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Note the join changed to professional_services mapping
    query = """
    SELECT p.id, p.user_id, u.name, u.phone, p.experience, p.area, p.work_radius, ps.custom_price
    FROM professionals p
    JOIN users u ON p.user_id = u.id
    JOIN professional_services ps ON p.id = ps.professional_id
    WHERE ps.service_id = %s AND p.is_approved = TRUE
    """

    cursor.execute(query, (service_id,))
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return data


def get_pending_professionals():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Admin approves the WHOLE professional
    query = """
    SELECT p.id, u.name, u.phone, p.experience, p.area
    FROM professionals p
    JOIN users u ON p.user_id = u.id
    WHERE p.is_approved = FALSE
    """

    cursor.execute(query)
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return data


def approve_professional(professional_id):
    conn = get_connection()
    cursor = conn.cursor()

    query = "UPDATE professionals SET is_approved = TRUE WHERE id = %s"
    cursor.execute(query, (professional_id,))
    conn.commit()

    cursor.close()
    conn.close()


def reject_professional(professional_id):
    conn = get_connection()
    cursor = conn.cursor()

    query = "DELETE FROM professionals WHERE id = %s"
    cursor.execute(query, (professional_id,))
    conn.commit()

    cursor.close()
    conn.close()
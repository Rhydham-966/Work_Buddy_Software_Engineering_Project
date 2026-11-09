# repositories/customer_repository.py

from database.db import get_connection


def get_services():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM services"
    cursor.execute(query)

    services = cursor.fetchall()

    cursor.close()
    conn.close()

    return services


def get_professionals_by_service(service_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT p.id, p.user_id, u.name, u.phone, p.experience, p.area, p.work_radius, ps.custom_price
    FROM professionals p
    JOIN users u ON p.user_id = u.id
    JOIN professional_services ps ON p.id = ps.professional_id
    WHERE ps.service_id = %s AND p.is_approved = TRUE
    """

    cursor.execute(query, (service_id,))
    professionals = cursor.fetchall()

    cursor.close()
    conn.close()

    return professionals

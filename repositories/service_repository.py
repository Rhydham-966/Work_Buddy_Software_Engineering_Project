# repositories/service_repository.py

from database.db import get_connection


def add_service(name, description, base_price, estimated_time):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO services (name, description, base_price, estimated_time)
    VALUES (%s, %s, %s, %s)
    """

    cursor.execute(query, (name, description, base_price, estimated_time))
    conn.commit()

    cursor.close()
    conn.close()


def get_all_services():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM services"
    cursor.execute(query)

    services = cursor.fetchall()

    cursor.close()
    conn.close()

    return services
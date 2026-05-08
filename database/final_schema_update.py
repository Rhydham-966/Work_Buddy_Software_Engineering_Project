import mysql.connector

import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database.db import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

def run_update():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        
        print("Starting Final Schema Update...")

        queries = [
            "DROP TABLE IF EXISTS invoices;",
            "DROP TABLE IF EXISTS bookings;",
            
            """
            CREATE TABLE bookings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                professional_id INT NOT NULL,
                service_id INT NOT NULL,
                time_slot_id INT,
                booking_type ENUM('immediate', 'scheduled') NOT NULL,
                scheduled_datetime DATETIME NULL,
                status ENUM('pending', 'accepted', 'rejected', 'completed', 'cancelled') DEFAULT 'pending',
                payment_method ENUM('cash', 'upi') NULL,
                payment_status ENUM('pending', 'paid') DEFAULT 'pending',
                total_price DECIMAL(10,2),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (professional_id) REFERENCES professionals(id) ON DELETE CASCADE,
                FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE,
                FOREIGN KEY (time_slot_id) REFERENCES time_slots(id) ON DELETE SET NULL
            );
            """,
            
            """
            CREATE TABLE invoices (
                id INT AUTO_INCREMENT PRIMARY KEY,
                booking_id INT,
                amount DECIMAL(10,2),
                payment_method VARCHAR(20),
                payment_status VARCHAR(20) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE
            );
            """
        ]

        for q in queries:
            try:
                cursor.execute(q)
            except Exception as e:
                print(f"Error executing: {q[:50]}... \n{e}")

        conn.commit()
        cursor.close()
        conn.close()
        print("\n✅ Final schema updated successfully! Bookings and Invoices ready.")
        
    except Exception as e:
        print(f"Failed to connect or update DB: {e}")

if __name__ == "__main__":
    run_update()

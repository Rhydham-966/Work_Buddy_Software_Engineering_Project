import mysql.connector
import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database.db import DB_HOST, DB_USER, DB_PASSWORD

print("Setting up the WorkBuddy Database...")

# Connect without specifying database to create it if needed
conn = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD
)

cursor = conn.cursor()

# Read the SQL file
sql_file_path = os.path.join("database", "setup_db.sql")
with open(sql_file_path, 'r', encoding='utf-8') as f:
    sql_commands = f.read()

# Execute SQL script by splitting commands
for command in sql_commands.split(';'):
    if command.strip():
        try:
            cursor.execute(command)
        except Exception as e:
            print(f"Error executing command: {command[:50]}... \n{e}")

conn.commit()
cursor.close()
conn.close()

print("Schema imported successfully from setup_db.sql!")

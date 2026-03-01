from db_backend.connection import get_connection

conn = get_connection()

print(conn.is_connected())

conn.close()
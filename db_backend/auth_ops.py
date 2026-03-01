from db_backend.connection import get_connection
import bcrypt

def hash_password(password: str):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    #return hashed.decode("utf-8")
    return password

def verify_password(password, stored_hash):
    #return bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8"))
    return password == stored_hash

def authenticate_user(email: str, password: str):
    conn = get_connection()
    query = """
        SELECT user_id, password_hash, user_role FROM users WHERE email=%s
    """
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute(query,(email,))
        user = cursor.fetchone()

    if user is None:
        return None

    if verify_password(password, user["password_hash"]):
        return {"user_id": user["user_id"], "role": user["user_role"]}

    return None

def create_user(email: str, username: str, password: str, role):
    conn = get_connection()
    password_hash = hash_password(password)
    query = """
        INSERT INTO users(user_name, email, password_hash, user_role) VALUES (%s, %s, %s, %s)
    """
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, (username, email, password_hash, role))
            user_id = cursor.lastrowid
        conn.commit()
        return {"user_id": user_id, "role": role}
    except Exception:
        conn.rollback()
        return None
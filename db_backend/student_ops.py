#Students should be allowed to perform the following actions -
#Create a user profile
#Fetch student profile
#Enroll in a course
#View enrolled courses
#View their grades and assignments

from db_backend.connection import get_connection
from db_backend.auth_ops import hash_password

def fetch_student_profile(student_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """ 
        SELECT student_id, user_name, student_year, major, email FROM users U JOIN students S ON U.user_id = S.student_id WHERE student_id = %s
    """
    cursor.execute(query, (student_id,))
    student = cursor.fetchone()
    cursor.close()
    return student

def create_student_profile(user_name, email, password, student_year: int, major):
    conn = get_connection()
    cursor = conn.cursor()
    password_hash = hash_password(password)
    query1 = """
        INSERT INTO users (user_name, email, password_hash, user_role) VALUES (%s, %s, %s, 'student')
    """
    cursor.execute(query1, (user_name, email, password_hash,))
    user_id = cursor.lastrowid
    query2 = """
        INSERT INTO students (student_id, student_year, major) VALUES (%s, %s, %s)
    """
    cursor.execute(query2, (user_id, student_year, major,))
    try:
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    cursor.close()
    return user_id

def enroll_in_course(student_id: int, course_code, semester, enrollment_year: int):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO enrollments(student_id, course_id, semester, enrollment_year) VALUES (%s, (SELECT course_id FROM courses WHERE course_code = %s), %s, %s)
    """
    cursor.execute(query, (student_id, course_code, semester, enrollment_year,))
    enrollment_id = cursor.lastrowid
    try:
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    cursor.close()
    return enrollment_id

def view_course_grades(student_id: int, course_code):
    conn = get_connection()
    course_id_lookup_query = """
        SELECT course_id FROM courses WHERE course_code = %s
    """
    query = """
        SELECT
            CG.course_id,
            A.title,
            G.marks_obtained,
            CG.grade
        FROM course_grades CG
        JOIN grades G
            ON CG.student_id = G.student_id
        JOIN assignments A
            ON G.assignment_id = A.assignment_id
        WHERE
            CG.course_id = %s
            AND CG.student_id = %s
            AND A.course_id = CG.course_id;

    """
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute(course_id_lookup_query, (course_code,))
        row = cursor.fetchone()
        if row is None:
            raise ValueError("Course not found")
        course_id = row["course_id"]
        cursor.execute(query, (course_id, student_id))
        result = cursor.fetchall()
        return result
    
def get_total_marks(student_id: int, course_code: str):
    conn = get_connection()
    query = """
        SELECT
            SUM(G.marks_obtained) AS total_marks
        FROM grades G
        JOIN assignments A
            ON G.assignment_id = A.assignment_id
        JOIN courses C
            ON A.course_id = C.course_id
        WHERE
            G.student_id = %s
            AND C.course_code = %s
    """
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute(
            query,
            (student_id, course_code)
        )
        result = cursor.fetchone()
    # Handle no assignments yet
    return result["total_marks"] if result else 0

def get_enrolled_courses(student_id: int):
    conn = get_connection()
    query = """
        SELECT
            C.course_code,
            C.title,
            C.credits,
            E.semester,
            E.enrollment_year
        FROM enrollments E
        JOIN courses C
            ON E.course_id = C.course_id
        WHERE E.student_id = %s
    """
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute(query, (student_id,))
        return cursor.fetchall()

def get_course_assignments(student_id: int, course_code: str): #This is for pending assignments only
    conn = get_connection()
    query = """
        SELECT
            A.title,
            A.due_date,
            A.max_marks
        FROM assignments A
        JOIN courses C
            ON A.course_id = C.course_id
        JOIN enrollments E
            ON E.course_id = C.course_id
        WHERE
            C.course_code = %s
            AND E.student_id = %s
            AND A.due_date > NOW()
        AND A.assignment_id NOT IN (
            SELECT assignment_id
            FROM grades
            WHERE student_id = %s
        )
    """
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute(query, (course_code, student_id, student_id))
        return cursor.fetchall()

def get_all_grades(student_id: int):
    conn = get_connection()
    query = """
        SELECT
            C.course_code,
            A.title,
            G.marks_obtained
        FROM grades G
        JOIN assignments A
            ON G.assignment_id = A.assignment_id
        JOIN courses C
            ON A.course_id = C.course_id
        WHERE G.student_id = %s
    """
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute(query, (student_id,))
        return cursor.fetchall()
    
def get_course_submitted_assignments(student_id: int, course_code: str):
    conn = get_connection()
    query = """
        SELECT G.assignment_id, A.title, G.marks_obtained FROM grades G JOIN assignments A ON G.assignment_id = A.assignment_id JOIN courses C ON A.course_id = C.course_id WHERE G.student_id = %s AND C.course_code = %s
    """
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute(query, (student_id, course_code))
        return cursor.fetchall()
    
def view_all_courses():
    conn = get_connection()
    query = """
        SELECT course_code, title FROM courses
    """
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute(query)
        return cursor.fetchall()
    
def create_student_record(user_id, year, major):
    conn = get_connection()
    query = """
    INSERT INTO students(student_id,student_year,major)
    VALUES(%s,%s,%s)
    """
    with conn.cursor() as cursor:
        cursor.execute(query,(user_id,year,major))

    conn.commit()

def get_all_final_grades(student_id: int):
    conn = get_connection()
    query = """
        SELECT C.course_code, CG.grade FROM course_grades CG JOIN courses C ON CG.course_id = C.course_id WHERE CG.student_id = %s
    """
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute(query, (student_id,))
        return cursor.fetchall()
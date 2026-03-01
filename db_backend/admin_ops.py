#What should the admin be able to do?
#Create a profile
#Upload grades and assignments
#Create a course
#Create assignments

from db_backend.connection import get_connection
from db_backend.auth_ops import hash_password

def create_assignment(course_code, title:str, due_date:str, max_marks:int):
    conn = get_connection()
    lookup_query = """
        SELECT course_id FROM courses WHERE course_code = %s
    """
    query = """
        INSERT INTO assignments(course_id, title, due_date, max_marks) VALUES (%s, %s, %s, %s)
    """
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(lookup_query, (course_code,))
            row = cursor.fetchone()
            if row is None:
                raise ValueError("Course not found")
            course_id = row["course_id"]
            cursor.execute(query, (course_id, title, due_date, max_marks))
            assignment_id = cursor.lastrowid
        conn.commit()
        return assignment_id
    except Exception:
        conn.rollback()
        raise

def upload_grade(student_id: int, assignment_id: int, marks_obtained: int):
    conn = get_connection()
    validation_query = """
        SELECT A.assignment_id FROM assignments A JOIN enrollments E ON A.course_id = E.course_id WHERE A.assignment_id = %s AND E.student_id = %s
    """
    insert_query = """
        INSERT INTO grades(assignment_id, student_id, marks_obtained) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE marks_obtained=VALUES(marks_obtained)
    """
    try:
        with conn.cursor() as cursor:
            # Step 1: Validate enrollment
            cursor.execute(
                validation_query,
                (assignment_id, student_id)
            )
            row = cursor.fetchone()
            if row is None:
                raise ValueError(
                    "Student not enrolled in assignment course"
                )

            # Step 2: Insert grade
            cursor.execute(
                insert_query,
                (assignment_id,
                 student_id,
                 marks_obtained)
            )
            grade_id = cursor.lastrowid
        conn.commit()
        return grade_id

    except Exception:
        conn.rollback()
        raise

def create_admin_profile(user_name, email, password):
    conn = get_connection()
    query = "INSERT INTO users(user_name, email, password_hash, user_role) VALUES(%s,%s,%s,'admin')"
    password_hash = hash_password(password)
    try:
        with conn.cursor() as cursor:
            cursor.execute(query,(user_name,email,password_hash))
            admin_id = cursor.lastrowid
        conn.commit()
        return admin_id
    except Exception:
        conn.rollback()
        raise

def create_course(instructor_name, course_code, title, credits):
    conn = get_connection()
    query = "INSERT INTO courses(instructor_name, course_code, title, credits) VALUES(%s,%s,%s,%s)"
    try:
        with conn.cursor() as cursor:
            cursor.execute(query,(instructor_name,course_code,title,credits))
            course_id = cursor.lastrowid
        conn.commit()
        return course_id
    except Exception:
        conn.rollback()
        raise

def assign_course_grade(student_id:int, course_code:str, grade:str):
    conn = get_connection()
    lookup_query = "SELECT course_id FROM courses WHERE course_code=%s"
    insert_query = "INSERT INTO course_grades(grade,course_id,student_id) VALUES(%s,%s,%s) ON DUPLICATE KEY UPDATE grade=VALUES(grade)"
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(lookup_query,(course_code,))
            row = cursor.fetchone()
            if row is None:
                raise ValueError("Course not found")
            course_id = row["course_id"]
            cursor.execute(insert_query,(grade,course_id,student_id))
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def view_course_roster(course_code:str):
    conn = get_connection()
    query = "SELECT S.student_id, U.user_name,U.email,S.student_year,S.major FROM enrollments E JOIN students S ON E.student_id=S.student_id JOIN users U ON U.user_id=S.student_id JOIN courses C ON C.course_id=E.course_id WHERE C.course_code=%s"
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute(query,(course_code,))
        return cursor.fetchall()


def get_course_details(course_code: str):
    conn = get_connection()
    query = """
        SELECT
            C.course_code, C.title, C.credits, C.instructor_name, COUNT(DISTINCT A.assignment_id) AS assignment_count, COUNT(DISTINCT E.student_id) AS enrollment_count, AVG(CASE WHEN CG.grade IS NOT NULL THEN 1 ELSE NULL END) AS has_grades_ratio
        FROM courses C
        LEFT JOIN assignments A
            ON C.course_id = A.course_id
        LEFT JOIN enrollments E
            ON C.course_id = E.course_id
        LEFT JOIN course_grades CG
            ON C.course_id = CG.course_id
        WHERE C.course_code = %s
        GROUP BY
            C.course_code,
            C.title,
            C.credits,
            C.instructor_name
    """
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute(query, (course_code,))
        row = cursor.fetchone()
        if row is None:
            raise ValueError("Course not found")
        return row


def update_assignment(assignment_id:int, title:str, due_date:str, max_marks:int):
    conn = get_connection()
    query = "UPDATE assignments SET title=%s,due_date=%s,max_marks=%s WHERE assignment_id=%s"
    try:
        with conn.cursor() as cursor:
            cursor.execute(query,(title,due_date,max_marks,assignment_id))
        conn.commit()
    except Exception:
        conn.rollback()
        raise

def delete_assignment(assignment_id:int):
    conn = get_connection()
    query = "DELETE FROM assignments WHERE assignment_id=%s"
    try:
        with conn.cursor() as cursor:
            cursor.execute(query,(assignment_id,))
        conn.commit()
    except Exception:
        conn.rollback()
        raise

def view_all_students():
    conn = get_connection()
    query = """
        SELECT S.student_id, U.user_name FROM students S JOIN users U ON S.student_id = U.user_id
    """
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute(query)
        return cursor.fetchall()
    
def view_all_assignments():
    conn = get_connection()
    query = """
        SELECT assignment_id FROM assignments
    """
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute(query)
        return cursor.fetchall()
    
def view_course_assignments(course_code):
    conn = get_connection()
    query = """
        SELECT A.assignment_id, A.title, A.due_date, A.max_marks FROM assignments A JOIN courses C ON A.course_id = C.course_id WHERE C.course_code = %s
    """
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute(query, (course_code,))
        return cursor.fetchall()
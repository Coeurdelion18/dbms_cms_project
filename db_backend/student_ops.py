# Students should be allowed to perform the following actions -
# Create a user profile
# Fetch student profile
# Enroll in a course
# View enrolled courses
# View their grades and assignments

from db_backend.connection import get_connection
from db_backend.auth_ops import hash_password


def fetch_student_profile(student_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT
            student_id,
            user_name,
            student_year,
            major,
            email
        FROM users U
        JOIN students S
            ON U.user_id = S.student_id
        WHERE student_id = %s
    """

    cursor.execute(query, (student_id,))
    student = cursor.fetchone()
    cursor.close()
    return student


def enroll_in_course(student_id: int, offering_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO enrollments(student_id, offering_id)
        VALUES (%s, %s)
    """

    cursor.execute(query, (student_id, offering_id))
    enrollment_id = cursor.lastrowid

    try:
        conn.commit()
    except Exception:
        conn.rollback()
        raise

    cursor.close()
    return enrollment_id


def view_course_grades(student_id: int, offering_id: int):
    conn = get_connection()

    query = """
        SELECT
            A.title,
            G.marks_obtained,
            CG.grade
        FROM course_grades CG
        JOIN grades G
            ON CG.student_id = G.student_id
        JOIN assignments A
            ON G.assignment_id = A.assignment_id
        WHERE
            CG.offering_id = %s
            AND CG.student_id = %s
            AND A.offering_id = CG.offering_id
    """

    with conn.cursor(dictionary=True) as cursor:
        cursor.execute(query, (offering_id, student_id))
        return cursor.fetchall()


def get_total_marks(student_id: int, course_code: str):
    conn = get_connection()

    query = """
        SELECT
            SUM(G.marks_obtained) AS total_marks
        FROM grades G
        JOIN assignments A
            ON G.assignment_id = A.assignment_id
        JOIN course_offerings CO
            ON A.offering_id = CO.offering_id
        JOIN courses C
            ON CO.course_id = C.course_id
        WHERE
            G.student_id = %s
            AND C.course_code = %s
    """

    with conn.cursor(dictionary=True) as cursor:
        cursor.execute(query, (student_id, course_code))
        result = cursor.fetchone()

    return result["total_marks"] if result and result["total_marks"] is not None else 0


def get_enrolled_courses(student_id: int):
    conn = get_connection()

    query = """
        SELECT
            C.course_code,
            C.title,
            C.credits,
            CO.semester,
            CO.offering_year
        FROM enrollments E
        JOIN course_offerings CO
            ON E.offering_id = CO.offering_id
        JOIN courses C
            ON CO.course_id = C.course_id
        WHERE E.student_id = %s
    """

    with conn.cursor(dictionary=True) as cursor:
        cursor.execute(query, (student_id,))
        return cursor.fetchall()


def get_course_assignments(student_id: int, course_code: str):
    # Pending assignments only

    conn = get_connection()

    query = """
        SELECT
            A.title,
            A.due_date,
            A.max_marks
        FROM assignments A
        JOIN course_offerings CO
            ON A.offering_id = CO.offering_id
        JOIN courses C
            ON CO.course_id = C.course_id
        JOIN enrollments E
            ON E.offering_id = CO.offering_id
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
        JOIN course_offerings CO
            ON A.offering_id = CO.offering_id
        JOIN courses C
            ON CO.course_id = C.course_id
        WHERE G.student_id = %s
    """

    with conn.cursor(dictionary=True) as cursor:
        cursor.execute(query, (student_id,))
        return cursor.fetchall()


def get_course_submitted_assignments(student_id: int, course_code: str):
    conn = get_connection()

    query = """
        SELECT
            G.assignment_id,
            A.title,
            G.marks_obtained
        FROM grades G
        JOIN assignments A
            ON G.assignment_id = A.assignment_id
        JOIN course_offerings CO
            ON A.offering_id = CO.offering_id
        JOIN courses C
            ON CO.course_id = C.course_id
        WHERE
            G.student_id = %s
            AND C.course_code = %s
    """

    with conn.cursor(dictionary=True) as cursor:
        cursor.execute(query, (student_id, course_code))
        return cursor.fetchall()


def view_all_courses():
    conn = get_connection()

    query = """
        SELECT
            CO.offering_id,
            C.course_code,
            C.title,
            C.credits,
            CO.offering_year,
            CO.semester
        FROM course_offerings CO
        JOIN courses C
            ON CO.course_id = C.course_id
        ORDER BY
            CO.offering_year DESC,
            CO.semester,
            C.course_code
    """

    with conn.cursor(dictionary=True) as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def get_all_final_grades(student_id: int):
    conn = get_connection()

    query = """
        SELECT
            C.course_code,
            CG.grade
        FROM course_grades CG
        JOIN course_offerings CO
            ON CG.offering_id = CO.offering_id
        JOIN courses C
            ON CO.course_id = C.course_id
        WHERE CG.student_id = %s
    """

    with conn.cursor(dictionary=True) as cursor:
        cursor.execute(query, (student_id,))
        return cursor.fetchall()
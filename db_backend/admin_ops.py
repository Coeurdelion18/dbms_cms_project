#What should the admin be able to do?
#Create a profile
#Upload grades and assignments
#Create a course
#Create assignments

from db_backend.connection import get_connection
from db_backend.auth_ops import hash_password


def create_admin_profile(user_name, email, password):
    conn = get_connection()

    query = """
        INSERT INTO users(user_name, email, password_hash, user_role)
        VALUES(%s, %s, %s, 'admin')
    """

    password_hash = hash_password(password)

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                query,
                (
                    user_name,
                    email,
                    password_hash
                )
            )

            admin_id = cursor.lastrowid

        conn.commit()
        return admin_id

    except Exception:
        conn.rollback()
        raise


def create_student_account(
    name,
    user_name,
    student_id,
    email,
    password,
    student_year,
    major
):
    conn = get_connection()

    user_query = """
        INSERT INTO users(user_name, email, password_hash, user_role)
        VALUES(%s, %s, %s, 'student')
    """

    student_query = """
        INSERT INTO students
        (
            student_id,
            student_name,
            student_year,
            major
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s
        )
    """

    password_hash = hash_password(password)

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                user_query,
                (
                    user_name,
                    email,
                    password_hash
                )
            )

            #student_id = cursor.lastrowid

            cursor.execute(
                student_query,
                (
                    student_id,
                    name,
                    student_year,
                    major
                )
            )

        conn.commit()
        return student_id

    except Exception:
        conn.rollback()
        raise


def create_instructor_account(
    user_name,
    email,
    password,
    instructor_name=None
):
    conn = get_connection()

    user_query = """
        INSERT INTO users(user_name, email, password_hash, user_role)
        VALUES(%s, %s, %s, 'instructor')
    """

    instructor_query = """
        INSERT INTO instructors
        (
            instructor_id,
            instructor_name
        )
        VALUES
        (
            %s,
            %s
        )
    """

    password_hash = hash_password(password)

    if instructor_name is None:
        instructor_name = user_name

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                user_query,
                (
                    user_name,
                    email,
                    password_hash
                )
            )

            instructor_id = cursor.lastrowid

            cursor.execute(
                instructor_query,
                (
                    instructor_id,
                    instructor_name
                )
            )

        conn.commit()
        return instructor_id

    except Exception:
        conn.rollback()
        raise


def create_course(
    course_code,
    title,
    credits
):
    conn = get_connection()

    query = """
        INSERT INTO courses
        (
            course_code,
            title,
            credits
        )
        VALUES
        (
            %s,
            %s,
            %s
        )
    """

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                query,
                (
                    course_code,
                    title,
                    credits
                )
            )

            course_id = cursor.lastrowid

        conn.commit()
        return course_id

    except Exception:
        conn.rollback()
        raise


def create_course_offering(
    instructor_id,
    course_id,
    offering_year,
    semester,
    max_seats
):
    conn = get_connection()

    query = """
        INSERT INTO course_offerings
        (
            instructor_id,
            course_id,
            offering_year,
            semester,
            max_seats
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s
        )
    """

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                query,
                (
                    instructor_id,
                    course_id,
                    offering_year,
                    semester,
                    max_seats
                )
            )

            offering_id = cursor.lastrowid

        conn.commit()
        return offering_id

    except Exception:
        conn.rollback()
        raise


def view_course_roster(offering_id):
    conn = get_connection()

    query = """
        SELECT
            S.student_id,
            U.user_name,
            U.email,
            S.student_year,
            S.major
        FROM enrollments E
        JOIN students S
            ON E.student_id = S.student_id
        JOIN users U
            ON U.user_id = S.student_id
        WHERE E.offering_id = %s
    """

    with conn.cursor(dictionary=True) as cursor:
        cursor.execute(
            query,
            (offering_id,)
        )

        return cursor.fetchall()


def get_course_details(offering_id):
    conn = get_connection()

    query = """
        SELECT
            C.course_code,
            C.title,
            C.credits,
            I.instructor_name,
            CO.offering_year,
            CO.semester,
            COUNT(DISTINCT A.assignment_id) AS assignment_count,
            COUNT(DISTINCT E.student_id) AS enrollment_count
        FROM course_offerings CO
        JOIN courses C
            ON CO.course_id = C.course_id
        JOIN instructors I
            ON CO.instructor_id = I.instructor_id
        LEFT JOIN assignments A
            ON CO.offering_id = A.offering_id
        LEFT JOIN enrollments E
            ON CO.offering_id = E.offering_id
        WHERE CO.offering_id = %s
        GROUP BY
            CO.offering_id,
            C.course_code,
            C.title,
            C.credits,
            I.instructor_name,
            CO.offering_year,
            CO.semester
    """

    with conn.cursor(dictionary=True) as cursor:
        cursor.execute(
            query,
            (offering_id,)
        )

        row = cursor.fetchone()

        if row is None:
            raise ValueError("Offering not found")

        return row


def view_all_students():
    conn = get_connection()

    query = """
        SELECT
            S.student_id,
            U.user_name
        FROM students S
        JOIN users U
            ON S.student_id = U.user_id
    """

    with conn.cursor(dictionary=True) as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def view_all_instructors():
    conn = get_connection()

    query = """
        SELECT
            I.instructor_id,
            I.instructor_name
        FROM instructors I
    """

    with conn.cursor(dictionary=True) as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def view_all_courses():
    conn = get_connection()

    query = """
        SELECT
            course_id,
            course_code,
            title,
            credits
        FROM courses
    """

    with conn.cursor(dictionary=True) as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def view_all_course_offerings():
    conn = get_connection()

    query = """
        SELECT
            CO.offering_id,
            C.course_code,
            C.title,
            I.instructor_name,
            CO.offering_year,
            CO.semester,
            CO.max_seats
        FROM course_offerings CO
        JOIN courses C
            ON CO.course_id = C.course_id
        JOIN instructors I
            ON CO.instructor_id = I.instructor_id
    """

    with conn.cursor(dictionary=True) as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def view_all_assignments():
    conn = get_connection()

    query = """
        SELECT
            assignment_id,
            title
        FROM assignments
    """

    with conn.cursor(dictionary=True) as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def view_course_assignments(offering_id):
    conn = get_connection()

    query = """
        SELECT
            assignment_id,
            title,
            due_date,
            max_marks
        FROM assignments
        WHERE offering_id = %s
    """

    with conn.cursor(dictionary=True) as cursor:
        cursor.execute(
            query,
            (offering_id,)
        )

        return cursor.fetchall()
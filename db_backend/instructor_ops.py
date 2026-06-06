from db_backend.connection import get_connection


def view_courses(instructor_id):
    conn = get_connection()

    query = """
        SELECT
            CO.offering_id,
            C.course_code,
            C.title,
            CO.offering_year,
            CO.semester
        FROM courses C
        JOIN course_offerings CO
            ON CO.course_id = C.course_id
        WHERE CO.instructor_id = %s
    """

    with conn.cursor(dictionary=True) as cursor:
        cursor.execute(query, (instructor_id,))
        return cursor.fetchall()


def create_assignment(
    offering_id: int,
    title: str,
    due_date: str,
    max_marks: int
):
    conn = get_connection()

    query = """
        INSERT INTO assignments
        (
            offering_id,
            title,
            due_date,
            max_marks
        )
        VALUES
        (
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
                    offering_id,
                    title,
                    due_date,
                    max_marks
                )
            )

            assignment_id = cursor.lastrowid

        conn.commit()
        return assignment_id

    except Exception:
        conn.rollback()
        raise


def upload_grade(
    student_id: int,
    assignment_id: int,
    marks_obtained: int
):
    conn = get_connection()

    validation_query = """
        SELECT A.assignment_id
        FROM assignments A
        JOIN enrollments E
            ON A.offering_id = E.offering_id
        WHERE
            A.assignment_id = %s
            AND E.student_id = %s
    """

    insert_query = """
        INSERT INTO grades
        (
            assignment_id,
            student_id,
            marks_obtained
        )
        VALUES
        (
            %s,
            %s,
            %s
        )
        ON DUPLICATE KEY UPDATE
            marks_obtained = VALUES(marks_obtained)
    """

    try:
        with conn.cursor() as cursor:

            cursor.execute(
                validation_query,
                (
                    assignment_id,
                    student_id
                )
            )

            row = cursor.fetchone()

            if row is None:
                raise ValueError(
                    "Student not enrolled in assignment offering"
                )

            cursor.execute(
                insert_query,
                (
                    assignment_id,
                    student_id,
                    marks_obtained
                )
            )

            grade_id = cursor.lastrowid

        conn.commit()
        return grade_id

    except Exception:
        conn.rollback()
        raise


def assign_course_grade(
    student_id: int,
    offering_id: int,
    grade: str
):
    conn = get_connection()

    query = """
        INSERT INTO course_grades
        (
            grade,
            offering_id,
            student_id
        )
        VALUES
        (
            %s,
            %s,
            %s
        )
        ON DUPLICATE KEY UPDATE
            grade = VALUES(grade)
    """

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                query,
                (
                    grade,
                    offering_id,
                    student_id
                )
            )

        conn.commit()

    except Exception:
        conn.rollback()
        raise


def view_course_roster(offering_id: int):
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


def update_assignment(
    assignment_id: int,
    title: str,
    due_date: str,
    max_marks: int
):
    conn = get_connection()

    query = """
        UPDATE assignments
        SET
            title = %s,
            due_date = %s,
            max_marks = %s
        WHERE assignment_id = %s
    """

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                query,
                (
                    title,
                    due_date,
                    max_marks,
                    assignment_id
                )
            )

        conn.commit()

    except Exception:
        conn.rollback()
        raise


def delete_assignment(
    assignment_id: int
):
    conn = get_connection()

    query = """
        DELETE FROM assignments
        WHERE assignment_id = %s
    """

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                query,
                (assignment_id,)
            )

        conn.commit()

    except Exception:
        conn.rollback()
        raise


def view_course_assignments(
    offering_id: int
):
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
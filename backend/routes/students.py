# backend/routes/students.py

from fastapi import APIRouter, HTTPException

from db_backend.student_ops import (
    fetch_student_profile,
    enroll_in_course,
    view_course_grades,
    get_total_marks,
    get_enrolled_courses,
    get_course_assignments,
    get_all_grades,
    get_course_submitted_assignments,
    view_all_courses,
    get_all_final_grades,
    upload_assignment_submission,
    create_student_record,
)
from db_backend.auth_ops import create_user

router = APIRouter()

from backend.schemas.student import (
    SubmissionRequest,
    EnrollmentRequest,
    StudentSignupRequest,
)


@router.post("/signup")
def signup_student(req: StudentSignupRequest):
    result = create_user(req.email, req.username, req.password, role="student")
    if not result:
        raise HTTPException(status_code=400, detail="Email may already exist")

    create_student_record(result["user_id"], req.username, req.year, req.major)
    return result


@router.get("/courses/all")
def get_all_courses():
    return view_all_courses()


@router.get("/{student_id}")
def get_student_profile(student_id: int):
    student = fetch_student_profile(student_id)

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    return student


@router.get("/{student_id}/courses")
def get_student_courses(student_id: int):
    return get_enrolled_courses(student_id)


@router.get("/{student_id}/grades")
def get_student_grades(student_id: int):
    return get_all_grades(student_id)


@router.get("/{student_id}/final-grades")
def get_student_final_grades(student_id: int):
    return get_all_final_grades(student_id)


@router.get("/{student_id}/course-grades/{offering_id}")
def get_course_grades(
    student_id: int,
    offering_id: int
):
    return view_course_grades(
        student_id,
        offering_id
    )


@router.get("/{student_id}/total-marks/{course_code}")
def get_marks(
    student_id: int,
    course_code: str
):
    return {
        "student_id": student_id,
        "course_code": course_code,
        "total_marks": get_total_marks(
            student_id,
            course_code
        )
    }


@router.get("/{student_id}/assignments/{offering_id}")
def get_pending_assignments(
    student_id: int,
    offering_id: int
):
    return get_course_assignments(
        student_id,
        offering_id
    )


@router.get(
    "/{student_id}/submitted-assignments/{offering_id}"
)
def get_submitted_assignments(
    student_id: int,
    offering_id: int
):
    return get_course_submitted_assignments(
        student_id,
        offering_id
    )


@router.post("/enroll")
def enroll_student(
    req: EnrollmentRequest
):
    enrollment_id = enroll_in_course(
        req.student_id,
        req.offering_id
    )

    return {
        "message": "Enrollment successful",
        "enrollment_id": enrollment_id
    }


@router.post("/submit-assignment")
def submit_assignment(
    req: SubmissionRequest
):
    upload_assignment_submission(
        req.student_id,
        req.assignment_id,
        req.filepath
    )

    return {
        "message": "Submission uploaded"
    }

# backend/routes/admin.py

from fastapi import APIRouter, HTTPException

from db_backend.admin_ops import (
    create_admin_profile,
    create_student_account,
    create_instructor_account,
    create_course,
    create_course_offering,
    view_course_roster,
    get_course_details,
    view_all_students,
    view_all_instructors,
    view_all_courses,
    view_all_course_offerings,
    view_all_assignments,
    view_course_assignments,
)
from backend.schemas.admin import (
    AdminCreateRequest,
    StudentCreateRequest,
    InstructorCreateRequest,
    CourseCreateRequest,
    OfferingCreateRequest,
)

router = APIRouter()


@router.post("/admins")
def create_admin(req: AdminCreateRequest):
    admin_id = create_admin_profile(
        req.user_name,
        req.email,
        req.password,
    )

    return {
        "message": "Admin created",
        "admin_id": admin_id,
    }


@router.post("/students")
def create_student(req: StudentCreateRequest):
    student_id = create_student_account(
        req.name,
        req.user_name,
        req.student_id,
        req.email,
        req.password,
        req.student_year,
        req.major,
    )

    return {
        "message": "Student created",
        "student_id": student_id,
    }


@router.post("/instructors")
def create_instructor(req: InstructorCreateRequest):
    instructor_id = create_instructor_account(
        req.user_name,
        req.email,
        req.password,
        req.instructor_name,
    )

    return {
        "message": "Instructor created",
        "instructor_id": instructor_id,
    }


@router.post("/courses")
def add_course(req: CourseCreateRequest):
    course_id = create_course(
        req.course_code,
        req.title,
        req.credits,
    )

    return {
        "message": "Course created",
        "course_id": course_id,
    }


@router.post("/offerings")
def add_offering(req: OfferingCreateRequest):
    offering_id = create_course_offering(
        req.instructor_id,
        req.course_id,
        req.offering_year,
        req.semester,
        req.max_seats,
    )

    return {
        "message": "Course offering created",
        "offering_id": offering_id,
    }


@router.get("/students")
def get_students():
    return view_all_students()


@router.get("/instructors")
def get_instructors():
    return view_all_instructors()


@router.get("/courses")
def get_courses():
    return view_all_courses()


@router.get("/offerings")
def get_offerings():
    return view_all_course_offerings()


@router.get("/assignments")
def get_assignments():
    return view_all_assignments()


@router.get("/offerings/{offering_id}")
def get_offering_details(offering_id: int):
    try:
        return get_course_details(offering_id)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/offerings/{offering_id}/roster")
def get_roster(offering_id: int):
    return view_course_roster(offering_id)


@router.get("/offerings/{offering_id}/assignments")
def get_assignments_for_course(offering_id: int):
    return view_course_assignments(offering_id)

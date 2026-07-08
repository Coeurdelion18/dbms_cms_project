# backend/routes/admin.py

from fastapi import APIRouter, Depends, HTTPException

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
from backend.security import require_role

router = APIRouter()
admin_only = [Depends(require_role("admin"))]


@router.post("/admins", dependencies=admin_only)
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


@router.post("/students", dependencies=admin_only)
def create_student(req: StudentCreateRequest):
    student_id = create_student_account(
        req.name,
        req.user_name,
        req.email,
        req.password,
        req.student_year,
        req.major,
    )

    return {
        "message": "Student created",
        "student_id": student_id,
    }


@router.post("/instructors", dependencies=admin_only)
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


@router.post("/courses", dependencies=admin_only)
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


@router.post("/offerings", dependencies=admin_only)
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


@router.get("/students", dependencies=admin_only)
def get_students():
    return view_all_students()


@router.get("/instructors", dependencies=admin_only)
def get_instructors():
    return view_all_instructors()


@router.get("/courses", dependencies=admin_only)
def get_courses():
    return view_all_courses()


@router.get("/offerings", dependencies=admin_only)
def get_offerings():
    return view_all_course_offerings()


@router.get("/assignments", dependencies=admin_only)
def get_assignments():
    return view_all_assignments()


@router.get("/offerings/{offering_id}", dependencies=admin_only)
def get_offering_details(offering_id: int):
    try:
        return get_course_details(offering_id)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/offerings/{offering_id}/roster", dependencies=admin_only)
def get_roster(offering_id: int):
    return view_course_roster(offering_id)


@router.get("/offerings/{offering_id}/assignments", dependencies=admin_only)
def get_assignments_for_course(offering_id: int):
    return view_course_assignments(offering_id)

# backend/routes/instructors.py

from fastapi import APIRouter, HTTPException

from db_backend.instructor_ops import (
    view_courses,
    create_assignment,
    upload_grade,
    assign_course_grade,
    view_course_roster,
    update_assignment,
    delete_assignment,
    view_course_assignments
)

router = APIRouter()

from backend.schemas.instructor import (
    AssignmentCreateRequest,
    AssignmentUpdateRequest,
    GradeUploadRequest,
    CourseGradeRequest
)

@router.get("/{instructor_id}/courses")
def get_instructor_courses(instructor_id: int):
    return view_courses(instructor_id)


@router.post("/assignments")
def create_new_assignment(req: AssignmentCreateRequest):
    assignment_id = create_assignment(
        req.offering_id,
        req.title,
        req.due_date,
        req.max_marks,
    )

    return {
        "message": "Assignment created",
        "assignment_id": assignment_id,
    }


@router.put("/assignments")
def modify_assignment(req: AssignmentUpdateRequest):
    update_assignment(
        req.assignment_id,
        req.title,
        req.due_date,
        req.max_marks,
    )

    return {"message": "Assignment updated"}


@router.delete("/assignments/{assignment_id}")
def remove_assignment(assignment_id: int):
    delete_assignment(assignment_id)
    return {"message": "Assignment deleted"}


@router.get("/offerings/{offering_id}/assignments")
def get_assignments(offering_id: int):
    return view_course_assignments(offering_id)


@router.post("/grades")
def upload_student_grade(req: GradeUploadRequest):
    try:
        grade_id, student_id = upload_grade(
            req.student_id,
            req.assignment_id,
            req.marks_obtained,
        )

        return {
            "message": "Grade uploaded",
            "grade_id": grade_id,
            "student_id": student_id,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/course-grades")
def upload_course_grade(req: CourseGradeRequest):
    try:
        assign_course_grade(
            req.student_id,
            req.offering_id,
            req.grade,
        )

        return {"message": "Course grade assigned"}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/offerings/{offering_id}/roster")
def get_course_roster(offering_id: int):
    return view_course_roster(offering_id)

from pydantic import BaseModel

class AssignmentCreateRequest(BaseModel):
    offering_id: int
    title: str
    due_date: str
    max_marks: int


class AssignmentUpdateRequest(BaseModel):
    assignment_id: int
    title: str
    due_date: str
    max_marks: int


class GradeUploadRequest(BaseModel):
    student_id: int
    assignment_id: int
    marks_obtained: int


class CourseGradeRequest(BaseModel):
    student_id: int
    offering_id: int
    grade: str
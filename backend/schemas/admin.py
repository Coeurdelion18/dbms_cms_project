from pydantic import BaseModel

class AdminCreateRequest(BaseModel):
    user_name: str
    email: str
    password: str


class StudentCreateRequest(BaseModel):
    name: str
    user_name: str
    email: str
    password: str
    student_year: int
    major: str


class InstructorCreateRequest(BaseModel):
    user_name: str
    email: str
    password: str
    instructor_name: str | None = None


class CourseCreateRequest(BaseModel):
    course_code: str
    title: str
    credits: int


class OfferingCreateRequest(BaseModel):
    instructor_id: int
    course_id: int
    offering_year: int
    semester: str
    max_seats: int

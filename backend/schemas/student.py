from pydantic import BaseModel

class EnrollmentRequest(BaseModel):
    student_id: int
    offering_id: int


class SubmissionRequest(BaseModel):
    student_id: int
    assignment_id: int
    filepath: str


class StudentSignupRequest(BaseModel):
    email: str
    username: str
    password: str
    year: int
    major: str

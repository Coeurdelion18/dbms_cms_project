from db_backend.admin_ops import create_course
from db_backend.student_ops import create_student_profile

student_id = create_student_profile(
    "Siddharth",
    "sid@email.com",
    "hashedpw",
    3,
    "Physics"
)

print(student_id)
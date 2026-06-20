from fastapi import FastAPI

from backend.routes.students import router as student_router
from backend.routes.instructors import router as instructor_router
from backend.routes.admins import router as admin_router
app = FastAPI()

app.include_router(student_router, prefix="/students", tags=["Students"])
app.include_router(instructor_router, prefix="/instructors", tags=["Instructors"])
app.include_router(admin_router, prefix="/admin", tags=["Admin"])


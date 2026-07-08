from fastapi import APIRouter, HTTPException
from db_backend.auth_ops import authenticate_user

router = APIRouter()

from backend.schemas.auth import LoginRequest
from backend.security import create_access_token

@router.post("/login")
def login(req: LoginRequest):

    user = authenticate_user(
        req.email,
        req.password
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    token = create_access_token(
        user["user_id"],
        user["role"]
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user["user_id"],
        "role": user["role"],
    }

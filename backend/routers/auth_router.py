"""
Auth router: Register and Login endpoints.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from auth import hash_password, verify_password, create_access_token
from storage import get_user_by_username, add_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ------------------------------------------------------------------
# Request / Response schemas
# ------------------------------------------------------------------
class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str


# ------------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------------
@router.post("/register", response_model=TokenResponse)
def register(body: RegisterRequest):
    """Create a new user account and return a JWT token."""
    # Check if username already taken
    if get_user_by_username(body.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    # Create user
    hashed = hash_password(body.password)
    user = add_user(body.username, hashed)

    # Generate token
    token = create_access_token(data={"sub": user["username"], "user_id": user["id"]})

    return TokenResponse(
        access_token=token,
        user_id=user["id"],
        username=user["username"],
    )


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest):
    """Authenticate a user and return a JWT token."""
    user = get_user_by_username(body.username)
    if not user or not verify_password(body.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    token = create_access_token(data={"sub": user["username"], "user_id": user["id"]})

    return TokenResponse(
        access_token=token,
        user_id=user["id"],
        username=user["username"],
    )

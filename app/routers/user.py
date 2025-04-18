from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from app.database import get_db
from app.auth import get_current_user
from typing import Any, Optional
from psycopg2.errors import UniqueViolation

# Define the router
router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None

from fastapi import HTTPException
from psycopg2 import Error as Psycopg2Error 

# Register User
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Any = Depends(get_db)):
    try:
        # Check if email or username already exists
        db.execute("SELECT * FROM users WHERE email = %s OR username = %s", (user.email, user.username))
        existing_user = db.fetchone()
        if existing_user:
            if existing_user["email"] == user.email:
                raise HTTPException(
                    status_code=400,
                    detail="Email already registered"
                )
            if existing_user["username"] == user.username:
                raise HTTPException(
                    status_code=400,
                    detail="Username already taken"
                )

        # Hash the password
        hashed_password = pwd_context.hash(user.password)

        # Insert the new user
        db.execute(
            """INSERT INTO users (username, email, password) VALUES (%s, %s, %s) RETURNING username, email""",
            (user.username, user.email, hashed_password)
        )
        new_user = db.fetchone()
        db.connection.commit()

        if new_user is None:
            raise HTTPException(status_code=500, detail="User creation failed")

        return {"username": new_user["username"], "email": new_user["email"]}

    except HTTPException:
        raise  # Let FastAPI return this as-is

    except Exception as e:
        db.connection.rollback()
        raise HTTPException(status_code=500, detail="Unexpected server error")


# Get user by username
@router.get("/{username}", status_code=status.HTTP_200_OK)
def get_user(username: str, db: Any = Depends(get_db)):
    try:
        db.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = db.fetchone()

        if not user:
            raise HTTPException(status_code=404, detail=f"User '{username}' not found")

        return {"user": dict(user)}  # Convert to dict if using psycopg2

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# Update user's password
@router.put("/update", status_code=status.HTTP_200_OK)
def update_user_password(
    user_update: UserUpdate,
    db: Any = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_email = current_user.get("sub")  # Extract email from token

    try:
        db.execute("SELECT * FROM users WHERE email = %s", (user_email,))
        user_record = db.fetchone()

        if not user_record:
            raise HTTPException(status_code=404, detail="User not found")

        if not user_update.password:
            raise HTTPException(status_code=400, detail="Password is required")

        hashed_password = pwd_context.hash(user_update.password)

        db.execute(
            "UPDATE users SET password = %s WHERE email = %s",
            (hashed_password, user_email)
        )
        db.connection.commit()

        return {"message": "Password updated successfully"}

    except Exception as e:
        db.connection.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

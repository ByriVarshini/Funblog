from fastapi import APIRouter, Depends
from app.auth import get_current_user  # Import the auth function

router = APIRouter(prefix="/protected", tags=["Protected"])

@router.get("/")
def protected_route(current_user=Depends(get_current_user)):  
    return {"message": "You are authorized", "user": current_user}

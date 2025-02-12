import os
from fastapi import APIRouter, Depends
from schemas.user import UserOut
from models import User

from main import get_current_user

router = APIRouter(
    tags=["User"], 
)


@router.get("/me/", response_model=UserOut)
async def read_current_user(current_user: User = Depends(get_current_user)):
    """
    Retrieves the current user's information
    """
    return current_user

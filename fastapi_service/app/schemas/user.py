from pydantic import BaseModel, EmailStr
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str
    first_name: str
    last_name:str


class UserOut(UserBase):
    id: int
    email: str
    is_active: Optional[bool] = False
    is_admin: Optional[bool] = False
    is_subscribed: Optional[bool] = False
    first_name : Optional[str] = None
    last_name: Optional[str] = None
    picture: Optional[str] = None  
    is_guest: Optional[bool] = None


    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[EmailStr] = None

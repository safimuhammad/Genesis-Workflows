from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from pydantic import ValidationError
from schemas.user import TokenData
import os  
from dotenv import load_dotenv


load_dotenv() #remove after globally loading once

SECRET_KEY = os.getenv("SECRET_KEY", "your-very-secret-key")
ALGORITHM = "HS256"  # Hashing algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)) 
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7)) 
def create_access_token(data: dict , expires_delta: timedelta = None) -> str:
    """
    Creates JWT access token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire })
    encoded_jwt = jwt.encode(to_encode , SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Creates a JWT refresh token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



def verify_access_token(token: str, credential_exception) -> TokenData:
    """
    Verifies the access token and returns the token data
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        email : str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
        return token_data
    except (JWTError, ValidationError):
        raise credential_exception
    
def verify_refresh_token(token: str, credential_exception) -> TokenData:
    """
    Verifies the refresh token and returns the token data.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credential_exception
        token_data = TokenData(email=email)
        return token_data
    except (JWTError, ValidationError):
        raise credential_exception
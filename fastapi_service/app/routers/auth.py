import os
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from schemas.user import UserCreate, UserOut, Token
from auth.utils import hash_password, verify_password
from auth.jwt import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
)
from auth.utils import get_geo_location
from authlib.integrations.starlette_client import OAuth, OAuthError
from starlette.config import Config
from starlette.requests import Request
import uuid
import json
from deps import get_db, limiter
from models import User

# from models.user import User

router = APIRouter(
    tags=["Auth"],
)
# Initialize OAuth
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID") or None
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET") or None
if GOOGLE_CLIENT_ID is None or GOOGLE_CLIENT_SECRET is None:
    raise BaseException("Missing env variables")
config_data = {
    "GOOGLE_CLIENT_ID": GOOGLE_CLIENT_ID,
    "GOOGLE_CLIENT_SECRET": GOOGLE_CLIENT_SECRET,
}
starlette_config = Config(environ=config_data)
oauth = OAuth(starlette_config)

oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


@router.post("/register", response_model=UserOut)
async def register(data: UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new User
    """
    user = db.query(User).filter(User.email == data.email).first()
    if user is not None:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pw = hash_password(data.password)
    new_user = User(
        email=data.email,
        first_name=data.first_name,
        last_name=data.last_name,
        hashed_password=hashed_pw,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Authenticates user and returns the token
    """
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token_expires = timedelta(
        minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    )
    refresh_token_expires = timedelta(
        days=int(os.getenv("FRESH_TOKEN_EXPIRE_MINUTES", 7))
    )
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": user.email}, expires_delta=refresh_token_expires
    )
    user.refresh_token = refresh_token
    db.commit()

    response_data = {
        "access_token": access_token,
        "token_type": "bearer",
    }
    response = JSONResponse(content=response_data)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7)) * 24 * 60 * 60,
    )
    return response


@router.get("/login/google")
async def login_google(request: Request):
    """
    Initiates Google OAuth2 login by redirecting the user to Google's consent screen.
    """
    redirect_uri = request.url_for("auth_google")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google")
async def auth_google(request: Request, db: Session = Depends(get_db)):
    """
    Callback route for handling Google's OAuth2 response.
    Exchanges authorization code for tokens, then
    logs in/registers the user, and issues tokens.
    """
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as error:
        raise HTTPException(status_code=400, detail=f"OAuthError: {error.error}")

    user_info = token.get("userinfo", {})
    email = user_info.get("email")
    first_name = user_info.get("given_name")
    last_name = user_info.get("family_name")
    picture = user_info.get("picture")

    if not email:
        raise HTTPException(status_code=400, detail="Email not provided by Google")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        # Create a new user if doesn't exist
        user = User(
            email=email,
            first_name=first_name or "",
            last_name=last_name or "",
            picture=picture or None,
            is_active=True,
            is_admin=False,
            is_subscribed=False,
            hashed_password=hash_password(os.urandom(16).hex()),  # random password
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Generate tokens
    access_token_expires = timedelta(
        minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    )
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    refresh_token_expires = timedelta(
        days=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))
    )
    refresh_token = create_refresh_token(
        data={"sub": user.email}, expires_delta=refresh_token_expires
    )

    # Update refresh token in database
    user.refresh_token = refresh_token
    db.commit()

    # Send tokens to client; set refresh token in HTTP-only cookie
    response = Response(
        content=json.dumps({"access_token": access_token, "token_type": "bearer"}),
        media_type="application/json",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,  # set to True in production
        samesite="strict",
        max_age=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7)) * 24 * 60 * 60,
    )
    return response


@router.post("/logout")
@limiter.limit("5/minute")  # Rate limiting: 5 requests per minute per IP
async def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    """
    Logs out the user by invalidating the refresh token stored in cookies.
    """
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_refresh_token(refresh_token, credential_exception)
    user = db.query(User).filter(User.email == token_data.email).first()

    if user is None or user.refresh_token != refresh_token:
        raise credential_exception

    # Invalidate the refresh token
    user.refresh_token = None
    db.commit()
    response.delete_cookie(key="refresh_token")

    return {"message": "Successfully logged out."}


@router.post("/login/guest", response_model=UserOut)
async def login_guest(request: Request, db: Session = Depends(get_db)):
    client_ip = request.client.host
    geo_data = get_geo_location(client_ip)
    guest_email = f"user+{uuid.uuid4()}@guest.com"
    guest_password = hash_password(os.urandom(16).hex())
    guest_user = User(
        email=guest_email,
        hashed_password=guest_password,
        first_name="guest",
        last_name="",
        location=geo_data,
        is_guest=True,
    )
    db.add(guest_user)
    db.commit()
    db.refresh(guest_user)

    access_token_expires = timedelta(
        minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    )
    refresh_token_expires = timedelta(
        days=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))
    )

    access_token = create_access_token(
        data={"sub": guest_email}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": guest_email}, expires_delta=refresh_token_expires
    )
    guest_user.refresh_token = refresh_token
    db.commit()
    response_data = {"access_token": access_token, "token_type": "bearer"}
    response = JSONResponse(content=response_data)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7)) * 24 * 60 * 60,
    )
    return response


@router.post("/refresh-token", response_model=Token)
@limiter.limit("5/minute")  # Rate limiting: 5 requests per minute per IP
async def refresh_token_endpoint(
    request: Request, response: Response, db: Session = Depends(get_db)
):
    """
    Refreshes the access token using a valid refresh token from cookies.
    """
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_refresh_token(refresh_token, credential_exception)
    user = db.query(User).filter(User.email == token_data.email).first()

    if user is None or user.refresh_token != refresh_token:
        raise credential_exception

    # Invalidate the old refresh token (refresh token rotation)
    user.refresh_token = None
    db.commit()

    # Generate new tokens
    access_token_expires = timedelta(
        minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    )
    new_access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    new_refresh_token = create_refresh_token(
        data={"sub": user.email},
        expires_delta=timedelta(days=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))),
    )

    # Store the new refresh token
    user.refresh_token = new_refresh_token
    db.commit()

    # Set the new refresh token in the HTTP-only cookie
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=True,  # Set to True in production
        samesite="strict",
        max_age=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))
        * 24
        * 60
        * 60,  # in seconds
    )

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
    }

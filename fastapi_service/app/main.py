import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from auth.jwt import verify_access_token
from database import engine, Base
from models import User
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
from deps import limiter, get_db

load_dotenv()
Base.metadata.create_all(bind=engine)
app = FastAPI()
origins = [
    "http://localhost",
    "http://localhost:3000",
    # Add other frontend domains here
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows specific origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)
app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get("SECRET_KEY", "a-very-secret-key"),
    https_only=True,
)
# Rate limiter
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)
oauth2_schema = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(
    token: str = Depends(oauth2_schema), db: Session = Depends(get_db)
):
    """
    Retrieves the current user based on token
    """
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_access_token(token, credential_exception)
    user = db.query(User).filter(User.email == token_data.email).first()
    if user is None:
        raise credential_exception
    return user


from routers.auth import router as auth_router
from routers.users import router as users_router
from routers.chains import router as messages_router
from routers.components import router as components_router
from routers.background import router as background_router

app.include_router(auth_router, prefix="/auth")
app.include_router(users_router, prefix="/users")
app.include_router(messages_router, prefix="/messages")
app.include_router(components_router, prefix="/components")
app.include_router(background_router, prefix="/background")


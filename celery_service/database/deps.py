from .database import SessionLocal
from slowapi import Limiter
from slowapi.util import get_remote_address

def get_db_session():
    db = SessionLocal()
    return db
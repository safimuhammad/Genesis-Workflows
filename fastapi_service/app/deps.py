from database import SessionLocal
from slowapi import Limiter
from slowapi.util import get_remote_address

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

limiter = Limiter(key_func=get_remote_address)
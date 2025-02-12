# database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL: Replace with your actual database URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres")

# SQLAlchemy Engine
engine = create_engine(
    DATABASE_URL
)

# SessionLocal: SQLAlchemy session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base: Base class for models
Base = declarative_base()
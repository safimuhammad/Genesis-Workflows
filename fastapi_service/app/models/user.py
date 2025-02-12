from sqlalchemy import Column, Integer, String, Boolean, JSON
from database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    is_subscribed = Column(Boolean, default=False, nullable=False)
    refresh_token = Column(String, nullable=True)
    picture = Column(String, nullable=True, default=None)
    location = Column(JSON, nullable=True)
    is_guest = Column(Boolean, nullable=False, default=False)
    messages = relationship("Message", back_populates="user")




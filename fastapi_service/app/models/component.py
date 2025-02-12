from sqlalchemy import Column, Integer, String, Boolean, JSON
from database import Base

class Abilities(Base):
    __tablename__ = "abilities"
    id = Column(Integer, primary_key=True, index=True)
    tool_name = Column(String, nullable=False, unique=True, index=True)
    description = Column(String, nullable=True)
    args = Column(JSON, nullable=True)
    output = Column(JSON, nullable=True)
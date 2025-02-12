from sqlalchemy import Column, Integer, String, Boolean, JSON
from database import Base

class Chain(Base):
    __tablename__ = "bg_chain"
    id = Column(Integer, primary_key=True, index=True)
    chain_id = Column(String, nullable=False)
    chain = Column(JSON,nullable=False)
    is_active = Column(Boolean, default=True)
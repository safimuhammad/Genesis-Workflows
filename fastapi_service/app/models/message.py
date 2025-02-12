from sqlalchemy import Column, JSON, String, ForeignKey, Integer
from sqlalchemy.orm import relationship
from database import Base


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, nullable=False, primary_key=True, index=True)
    chain_id = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    from_agent = Column(String, nullable=False)
    to_agent = Column(String, nullable=False)
    message = Column(String, nullable=False)
    args = Column(JSON, nullable=False)
    user = relationship("User", back_populates="messages")

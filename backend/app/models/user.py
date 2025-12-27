from sqlalchemy import Column, Integer, String, Boolean
from app.core.database import Base
from sqlalchemy.orm import relationship



class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="attendee")
    is_active = Column(Boolean, default=True)
    refresh_tokens = relationship(
    "RefreshToken",
    back_populates="user",
    cascade="all, delete-orphan"
)

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime



class Invite(Base):
    __tablename__ = "invites"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, unique=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    token_hash = Column(String(255), nullable=False,unique=True)
    expires_at = Column(DateTime, nullable=False)

    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    event = relationship("Event", backref="invites")
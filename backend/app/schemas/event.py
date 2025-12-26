from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class EventBase(BaseModel):
    name: str
    description: str | None = None
    start_time: datetime
    end_time: datetime
    location: str | None = None
    max_attendees: int | None = None

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    max_attendees: Optional[int] = None

class EventResponse(EventBase):
    id: int
    created_by: int

    class Config:
        from_attributes = True

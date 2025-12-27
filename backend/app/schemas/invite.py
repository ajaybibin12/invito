from pydantic import BaseModel, EmailStr
from datetime import datetime


class InviteCreate(BaseModel):
    email: EmailStr


class InviteResponse(BaseModel):
    id: int
    email: EmailStr
    event_id: int
    expires_at: datetime
    used: bool

    class Config:
        from_attributes = True

class InviteResponseDev(InviteResponse):
    dev_token: str


class InviteVerifyResponse(BaseModel):
    valid: bool
    event_id: int | None = None
    email: EmailStr | None = None

class InviteAcceptRequest(BaseModel):
    token: str
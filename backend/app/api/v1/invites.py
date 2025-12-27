from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    BackgroundTasks
)
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_admin
from app.core.tokens import generate_invite_token, hash_token

from app.models.invite import Invite
from app.models.event import Event
from app.models.user import User

from app.schemas.invite import (
    InviteCreate,
    InviteResponse,
    InviteVerifyResponse,
    InviteResponseDev,
    InviteAcceptRequest
)

from app.core.config import settings
from app.services.email import send_invite_email
from app.core.security import get_password_hash, create_access_token
import secrets



router = APIRouter(prefix="/events", tags=["Invites"])



@router.post(
    "/{event_id}/invite",
    response_model=InviteResponseDev if settings.ENV == "development" else InviteResponse,
    status_code=status.HTTP_201_CREATED
)
def invite_user(
    event_id: int,
    payload: InviteCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    # Validate event
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    # Prevent duplicate active invites
    existing = db.query(Invite).filter(
        Invite.event_id == event_id,
        Invite.email == payload.email,
        Invite.used == False,
        Invite.expires_at > datetime.utcnow()
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Active invite already exists for this email"
        )

    # Generate secure token
    raw_token, token_hash = generate_invite_token()

    invite = Invite(
        email=payload.email,
        event_id=event_id,
        token_hash=token_hash,
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )

    # Persist
    db.add(invite)
    db.commit()
    db.refresh(invite)

    # Send email asynchronously
    background_tasks.add_task(
        send_invite_email,
        payload.email,
        raw_token,
        event.name
    )

    # return invite
    response = InviteResponse.from_orm(invite)

    if settings.ENV == "development":
        return {
            **response.model_dump(),
            "dev_token": raw_token
        }

    return response


@router.get(
    "/invites/verify",
    response_model=InviteVerifyResponse
)
def verify_invite(
    token: str,
    db: Session = Depends(get_db)
):
    token_hash = hash_token(token)

    invite = db.query(Invite).filter(
        Invite.token_hash == token_hash,
        Invite.used == False,
        Invite.expires_at > datetime.utcnow()
    ).first()

    if not invite:
        return InviteVerifyResponse(valid=False)

    return InviteVerifyResponse(
        valid=True,
        event_id=invite.event_id,
        email=invite.email
    )



@router.post("/invites/accept")
def accept_invite(
    payload: InviteAcceptRequest,
    db: Session = Depends(get_db),
    ):
    token_hash = hash_token(payload.token)
    invite = db.query(Invite).filter(
        Invite.token_hash == token_hash,
        Invite.used == False,
        Invite.expires_at > datetime.utcnow()
    ).first()

    if not invite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired invite token"
        )

    user = db.query(User).filter(User.email == invite.email).first()
    if not user:
        random_password = secrets.token_urlsafe(16)
        user = User(
            email=invite.email,
            hashed_password=get_password_hash(random_password),
            role="attendee"
        )
        db.add(user)
        db.flush()

    invite.used = True
    db.commit()

    # 🎟 auto login
    token = create_access_token(
        {"sub": user.email, "role": user.role}
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }
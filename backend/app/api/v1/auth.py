from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, create_access_token
from app.core.security import hash_refresh_token
from app.core.security import refresh_token_expiry, create_refresh_token
from datetime import datetime
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.schemas.auth import LoginRequest, TokenResponse,RefreshTokenRequest

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Create access token
    access_token = create_access_token(
        {"sub": user.email, "role": user.role}
    )

    # Create refresh token
    raw_refresh_token = create_refresh_token()
    db_refresh_token = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(raw_refresh_token),
        expires_at=refresh_token_expiry()
    )

    db.add(db_refresh_token)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": raw_refresh_token
    }

@router.post("/refresh")
def refresh_token(
    data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    token_hash = hash_refresh_token(data.refresh_token)

    db_token = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked == False,
            RefreshToken.expires_at > datetime.utcnow()
        )
        .first()
    )

    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    user = db_token.user

    # Rotate old token
    db_token.revoked = True

    new_refresh = create_refresh_token()
    new_db_token = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(new_refresh),
        expires_at=refresh_token_expiry()
    )

    db.add(new_db_token)
    db.commit()

    new_access = create_access_token(
        {"sub": user.email, "role": user.role}
    )

    return {
        "access_token": new_access,
        "refresh_token": new_refresh
    }


# ===================== LOGOUT =====================
@router.post("/logout")
def logout(
    data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    token_hash = hash_refresh_token(data.refresh_token)

    db_token = db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash
    ).first()

    if db_token:
        db_token.revoked = True
        db.commit()

    return {"detail": "Logged out successfully"}
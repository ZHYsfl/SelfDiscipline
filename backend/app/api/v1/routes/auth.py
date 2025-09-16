from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas
from app.crud import (
    create_refresh_token as db_create_refresh_token,
    create_user,
    get_user_by_email,
    get_valid_refresh_token,
    revoke_refresh_token,
)
from app.database import get_db
from app.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.config import settings


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.UserRead)
def register(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = create_user(db, payload.email, payload.password, payload.display_name)
    return user


@router.post("/login", response_model=schemas.TokenPair)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, payload.email)
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)

    decoded = decode_token(refresh)
    exp_ts = int(decoded["exp"])  # seconds since epoch
    expires_at = datetime.fromtimestamp(exp_ts, tz=timezone.utc)
    db_create_refresh_token(db, user.id, refresh, expires_at)

    return schemas.TokenPair(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=schemas.AccessTokenResponse)
def refresh_token(payload: schemas.TokenRefreshRequest, db: Session = Depends(get_db)):
    stored = get_valid_refresh_token(db, payload.refresh_token)
    if not stored:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    try:
        decoded = decode_token(payload.refresh_token)
        if decoded.get("typ") != "refresh":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong token type")
    except ValueError:
        revoke_refresh_token(db, stored)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Expired or invalid refresh token")

    access = create_access_token(decoded["sub"])  # sub is user_id as str
    return schemas.AccessTokenResponse(access_token=access)


@router.post("/logout")
def logout(payload: schemas.TokenRefreshRequest, db: Session = Depends(get_db)):
    stored = get_valid_refresh_token(db, payload.refresh_token)
    if stored:
        revoke_refresh_token(db, stored)
    return {"ok": True}

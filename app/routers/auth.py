from fastapi import APIRouter, Depends, HTTPException, status
from datetime import timedelta, datetime

from app.schemas import LoginRequest, TokenRefreshRequest
from app.utils.security import decode_access_token, create_access_token, create_refresh_token
from app.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app import crud, schemas

router = APIRouter()


@router.post("/register", response_model=schemas.UserOut)
async def register(user_in: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await crud.get_user(db, user_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = await crud.create_user(db, user_in)
    return user


@router.post("/login", response_model=schemas.TokenPair)
async def login(login_in: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await crud.authenticate_user(db, login_in.email, login_in.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_refresh_token(
        data={"sub": user.email},
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    await crud.create_refresh_token(db, user.email, refresh_token, expires_at)

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh", response_model=schemas.TokenResponse)
async def refresh_token(data: TokenRefreshRequest, db: AsyncSession = Depends(get_db)):
    db_token = await crud.get_refresh_token(db, data.refresh_token)
    if not db_token or db_token.revoked or db_token.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    email = decode_access_token(data.refresh_token)
    if email is None:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    access_token = create_access_token(
        data={"sub": email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(data: TokenRefreshRequest, db: AsyncSession = Depends(get_db)):
    revoked = await crud.revoke_refresh_token(db, data.refresh_token)
    if not revoked:
        raise HTTPException(status_code=400, detail="Refresh token invalid")
    return {"detail": "Logged out successfully"}

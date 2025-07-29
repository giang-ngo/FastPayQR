from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app import schemas, models
from backend.app.utils.security import get_password_hash, verify_password
from datetime import datetime
import uuid


async def get_user(db: AsyncSession, user_id: int):
    return await db.get(models.User, user_id)


async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(models.User).where(models.User.email == email))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user: schemas.UserCreate):
    db_user = models.User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=get_password_hash(user.password),
        is_active=True,
        is_admin=False,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def authenticate_user(db: AsyncSession, email: str, password: str):
    result = await db.execute(select(models.User).where(models.User.email == email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


async def create_order(db: AsyncSession, user_id: int, order: schemas.OrderCreate):
    user = await get_user(db, user_id)
    if not user:
        return None

    db_order = models.Order(
        id=str(uuid.uuid4()),
        user_id=user_id,
        items=[item.dict() for item in order.items],
        total_amount=order.total_amount,
        status="pending"
    )
    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)
    return db_order


async def get_order(db: AsyncSession, order_id: str):
    result = await db.execute(select(models.Order).where(models.Order.id == order_id))
    return result.scalar_one_or_none()


async def create_refresh_token(db: AsyncSession, user_id: int, token: str, expires_at: datetime):
    user = await db.get(models.User, user_id)
    if not user:
        raise Exception("User not found")

    db_token = models.RefreshToken(
        user_id=user.id,
        token=token,
        expires_at=expires_at,
        revoked=False,
    )
    db.add(db_token)
    await db.commit()
    await db.refresh(db_token)
    return db_token



async def get_refresh_token(db: AsyncSession, token: str):
    result = await db.execute(select(models.RefreshToken).where(models.RefreshToken.token == token))
    return result.scalar_one_or_none()



async def revoke_refresh_token(db: AsyncSession, token: str):
    db_token = await get_refresh_token(db, token)
    if db_token:
        db_token.revoked = True
        await db.commit()
        return True
    return False

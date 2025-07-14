from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas, crud
from app.database import get_db
from app.deps import get_current_user

router = APIRouter()


@router.post("/orders", response_model=schemas.OrderOut)
async def create_order(order_in: schemas.OrderCreate, db: AsyncSession = Depends(get_db),
                       current_user=Depends(get_current_user)):
    return await crud.create_order(db, user_email=current_user.email, order=order_in)

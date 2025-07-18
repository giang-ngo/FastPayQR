from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app import crud
from backend.app.database import get_db
from backend.app.schemas import OrderOut

router = APIRouter()


@router.get("/pay/{order_id}", response_model=OrderOut)
async def pay_view(order_id: str, db: AsyncSession = Depends(get_db)):
    order = await crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

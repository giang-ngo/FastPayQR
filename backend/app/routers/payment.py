import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app import crud
from backend.app.database import get_db
from backend.app.schemas import OrderOut
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from backend.app.models import Order
from backend.app.deps import get_current_user
from backend.app.tasks.tasks import send_invoice_email_task
from backend.app.websocket_manager import manager

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get("/pay/{order_id}", response_model=OrderOut)
async def pay_view(
        order_id: str,
        db: AsyncSession = Depends(get_db),
        current_user=Depends(get_current_user),
):
    order = await crud.get_order(db, order_id)

    if not order or order.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Order not found")
    order_dict = {
        "id": order.id,
        "items": order.items,
        "total_amount": order.total_amount,
        "user_email": order.user.email,
        "status": order.status, }

    return order_dict


@router.post("/pay/internal/{order_id}")
async def pay_internal(
        order_id: str,
        db: AsyncSession = Depends(get_db),
        current_user=Depends(get_current_user),
):
    result = await db.execute(
        select(Order).options(selectinload(Order.user)).where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()
    if not order or order.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.status == "paid":
        raise HTTPException(status_code=400, detail="Order already paid")

    user = order.user
    if user.wallet_balance < order.total_amount:
        raise HTTPException(status_code=400, detail="Insufficient wallet balance")

    user.wallet_balance -= order.total_amount
    order.status = "paid"
    await db.commit()
    await manager.send_update(order_id, "paid")

    send_invoice_email_task.delay(
        order_id=order.id,
        user_email=user.email,
        user_name=user.full_name,
        amount=order.total_amount
    )

    return {"message": "Payment successful"}


@router.post("/webhook/ipn")
async def handle_ipn(request: Request, db: AsyncSession = Depends(get_db)):
    data = await request.json()
    order_id = data.get("order_id")
    status = data.get("status")

    if not order_id or not status:
        raise HTTPException(status_code=400, detail="Invalid webhook payload")

    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if status == "paid" and order.status != "paid":
        order.status = "paid"
        await db.commit()

    return {"message": "IPN received"}

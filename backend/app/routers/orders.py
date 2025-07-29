from backend.app import schemas, crud
from backend.app.deps import get_current_user
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
import qrcode
import os
import socket

from backend.app.database import get_db
from backend.app.models import Order

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
QR_FOLDER = os.path.join(BASE_DIR, "static", "qr")
os.makedirs(QR_FOLDER, exist_ok=True)


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()


@router.post("/", response_model=schemas.OrderOut)
async def create_order(
        order_in: schemas.OrderCreate,
        db: AsyncSession = Depends(get_db),
        current_user=Depends(get_current_user)
):
    order = await crud.create_order(db, user_id=current_user.id, order=order_in)
    await db.refresh(order, attribute_names=["user"])
    return {
        **order.__dict__,
        "user_email": order.user.email
    }


@router.get("/{order_id}/qr")
async def generate_qr(order_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Order).options(selectinload(Order.user)).where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    ip = get_local_ip()
    qr_data = f"http://{ip}:8000/payment/pay/{order_id}"

    img_filename = f"{order_id}.png"
    img_path = os.path.join(QR_FOLDER, img_filename)

    try:
        os.remove(img_path)
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"Lỗi khi xóa ảnh cũ: {e}")

    img = qrcode.make(qr_data)
    img.save(img_path)

    return {
        "order_id": order.id,
        "customer_name": order.user.full_name,
        "amount": order.total_amount,
        "status": order.status,
        "items": order.items,
        "image_url": f"http://{ip}:8000/static/qr/{img_filename}",
        "qr_url": qr_data,
    }

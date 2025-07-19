from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.deps import get_current_user
from backend.app.database import get_db
from backend.app.models import WalletTopUp, User
from backend.app.schemas import WalletTopUpCreate, WalletTopUpOut

router = APIRouter()


@router.post("/topup", response_model=WalletTopUpOut, status_code=201)
async def create_topup(
        topup_in: WalletTopUpCreate,
        db: AsyncSession = Depends(get_db),
        current_user=Depends(get_current_user)
):
    topup = WalletTopUp(
        user_id=current_user.id,
        amount=topup_in.amount,
        status="pending"
    )
    db.add(topup)
    await db.commit()
    await db.refresh(topup)
    return topup


@router.post("/topup/confirm/{topup_id}", response_model=WalletTopUpOut)
async def confirm_topup(
        topup_id: int,
        db: AsyncSession = Depends(get_db)
):
    topup = await db.get(WalletTopUp, topup_id)

    if not topup:
        raise HTTPException(status_code=404, detail="Topup not found")

    if topup.status == "completed":
        raise HTTPException(status_code=400, detail="Topup already completed")

    user = await db.get(User, topup.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Cập nhật số dư
    user.wallet_balance += topup.amount
    topup.status = "completed"

    await db.commit()
    await db.refresh(topup)
    return topup

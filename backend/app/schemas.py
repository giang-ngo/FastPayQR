from pydantic import BaseModel, EmailStr, condecimal
from typing import List, Optional
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    wallet_balance: float
    is_active: bool
    is_admin: bool

    class Config:
        from_attributes = True


class WalletTopUpBase(BaseModel):
    amount: condecimal(gt=0)


class WalletTopUpCreate(WalletTopUpBase):
    pass


class WalletTopUpOut(WalletTopUpBase):
    id: int
    status: str
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class Item(BaseModel):
    name: str
    quantity: int
    price: int


class OrderCreate(BaseModel):
    items: List[Item]
    total_amount: int


class OrderOut(OrderCreate):
    id: str
    user_email: EmailStr
    status: str

    class Config:
        from_attributes = True

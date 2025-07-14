from pydantic import BaseModel, EmailStr
from typing import List


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str


class UserOut(BaseModel):
    email: EmailStr
    full_name: str
    is_active: bool

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


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
        orm_mode = True


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

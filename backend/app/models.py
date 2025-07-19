from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.database import Base
from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, JSON
import uuid


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)  # thêm id kiểu Integer auto increment
    email = Column(String, unique=True, index=True, nullable=False)  # giữ unique chứ không phải primary key nữa
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    wallet_balance = Column(Float, default=0.0)

    # Quan hệ
    topups = relationship("WalletTopUp", back_populates="user")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")


class WalletTopUp(Base):
    __tablename__ = "wallet_topups"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float, nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="topups")


class Order(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    items = Column(JSON, nullable=False)
    total_amount = Column(Integer, nullable=False)
    status = Column(String, default="pending")

    user = relationship("User", back_populates="orders")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, nullable=False, index=True)
    issued_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False)

    user = relationship("User", back_populates="refresh_tokens")

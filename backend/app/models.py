from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, JSON
import uuid
from datetime import datetime
from backend.app.database import Base


class User(Base):
    __tablename__ = "users"

    email = Column(String, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")


class Order(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_email = Column(String, ForeignKey("users.email"), nullable=False)
    items = Column(JSON, nullable=False)
    total_amount = Column(Integer, nullable=False)
    status = Column(String, default="pending")

    user = relationship("User", back_populates="orders")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_email = Column(String, ForeignKey("users.email"), nullable=False)
    token = Column(String, unique=True, nullable=False, index=True)
    issued_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False)

    user = relationship("User", back_populates="refresh_tokens")

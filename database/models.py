from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class UserRole(enum.Enum):
    USER = "user"
    ADMIN = "admin"


class PaymentGateway(enum.Enum):
    ZARINPAL = "zarinpal"
    ZIBAL = "zibal"
    CRYPTO = "crypto"


class PaymentType(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class TransactionType(enum.Enum):
    PAYMENT = "payment"
    USAGE = "usage"
    REFUND = "refund"
    INVITE_BONUS = "invite_bonus"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    username = Column(String)
    balance = Column(Float, default=0)
    role = Column(Enum(UserRole), default=UserRole.USER)
    invited_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    servers = relationship("Server", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")


class Server(Base):
    __tablename__ = "servers"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    hetzner_id = Column(String)
    name = Column(String)
    country = Column(String)
    hardware_type = Column(String)
    os = Column(String)
    hourly_cost = Column(Float)
    status = Column(String)
    created_at = Column(DateTime)
    user = relationship("User", back_populates="servers")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float)
    type = Column(Enum(TransactionType))  # "payment", "usage", "refund", "invite_bonus"
    timestamp = Column(DateTime)
    user = relationship("User", back_populates="transactions")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float)
    gateway = Column(Enum(PaymentGateway))
    status = Column(Enum(PaymentType))  # "pending", "completed", "failed"
    created_at = Column(DateTime)
    completed_at = Column(DateTime, nullable=True)

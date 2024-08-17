from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    username = Column(String(100))
    balance = Column(Float, default=0.0)
    servers = relationship('Server', back_populates='owner')
    transactions = relationship('Transaction', back_populates='user')


class Server(Base):
    __tablename__ = 'servers'

    id = Column(Integer, primary_key=True)
    hetzner_id = Column(String(100), unique=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    server_type = Column(String(50))
    country = Column(String(50))
    os = Column(String)
    cost_per_hour = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    owner = relationship('User', back_populates='servers')


class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    amount = Column(Float)
    type = Column(String(50))  # deposit or withdrawal
    timestamp = Column(DateTime, default=datetime.utcnow)
    user = relationship('User', back_populates='transactions')

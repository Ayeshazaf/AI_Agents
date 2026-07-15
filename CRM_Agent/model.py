from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy import DateTime
from sqlalchemy.orm import relationship
from shared.database import Base
from enum import Enum
from sqlalchemy import Enum as SqlEnum
from datetime import datetime


class ComplaintStatus(str, Enum):
    open = "open"
    in_review = "in_review"
    resolved = "resolved"
    closed = "closed"
    escalated = "escalated"

class ComplaintPriority(int, Enum):
    low = 1
    medium = 2
    high = 3

class Customer(Base):
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    phone_number = Column(String)
    address = Column(String)
    account_id = Column(Integer, unique=True, nullable=False)

    complaints = relationship("Complaint", back_populates="customer")
    sessions = relationship("ChatHistory", back_populates="customer")
class Complaint(Base):
    __tablename__ = 'complaints'

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    description = Column(String)
    status = Column(SqlEnum(ComplaintStatus))
    priority = Column(SqlEnum(ComplaintPriority))

    created_at = Column(DateTime)
    customer = relationship("Customer", back_populates="complaints")

    
class ChatHistory(Base):
    __tablename__ = 'chat_history'

    id = Column(Integer, primary_key=True)
    session_id = Column(String)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    role = Column(String, default="user")  # role can be 'user' or 'assistant'
    message = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="sessions")

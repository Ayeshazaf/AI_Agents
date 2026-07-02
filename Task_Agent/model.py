from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from enum import Enum
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import DateTime
from datetime import datetime

Base = declarative_base()

class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"

class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(SqlEnum(TaskStatus), nullable=False)
    priority = Column(SqlEnum(TaskPriority), nullable=False)
    due_date = Column(String, nullable=True)
    updated_at = Column(DateTime)

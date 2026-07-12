from shared.database import Base, engine

from Task_Agent.model import Task
from RAG_Agent.db_model import document, chunks
from CRM_Agent.model import Customer, Complaint, ChatHistory

Base.metadata.create_all(bind=engine)
print("Created tables...")
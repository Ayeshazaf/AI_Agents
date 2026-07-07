from shared.database import Base, engine

from Task_Agent.model import Task
from RAG_Agent.db_model import document, chunks

Base.metadata.create_all(bind=engine)
print("Creating tables...")
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import DateTime
from datetime import datetime
from shared.database import Base
# what is page number field? It is a field that indicates the page number of the chunk in the original document. This can be useful for referencing specific parts of a document, especially when dealing with large documents that are split into multiple chunks.
#how page number firld is implemented? The page number field is implemented as an Integer column in the chunks table. It is optional, meaning it can be null if the page number is not applicable or not provided. This allows for flexibility in cases where the chunk does not correspond to a specific page in the original document.


class document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    category = Column(String, nullable=False)  
    page_count = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class chunks(Base):
    __tablename__ = "chunks"
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(String, nullable=False)
    source_document = relationship("document", backref="chunks")
    doc_category = Column(String, nullable=True)  # Optional category field
    page_number = Column(Integer, nullable=True)  # Optional page number field
    
    
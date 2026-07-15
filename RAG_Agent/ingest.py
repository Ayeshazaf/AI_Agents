from fastapi import UploadFile, File, APIRouter, Depends
import fitz  # PyMuPDF
from shared.database import get_db
from sqlalchemy.orm import Session
from .db_model import document, chunks
from .chunker import chunk_text
from .embedder import embedder
from shared.logging_config import logger
import re
from shared.init_db import Base

router = APIRouter()


@router.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...), category: str = None, db: Session = Depends(get_db)):
    # Open the PDF file 
    logger.info(f"Uploading PDF file: {file.filename} with category: {category}")
    pdf_bytes = await file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    all_pages_text = ""
    count = 0
    # Create the document row first so chunk rows can reference its ID.
    new_document = document(title=file.filename, content="", page_count=0, category=category)
    db.add(new_document)
    db.flush()

    for page in doc.pages():
        text = page.get_text()  # Extract text from the page
        # Process the extracted text as needed
        
        text = clean_text(text)  # Clean the text using the clean_text function
        page_number = page.number + 1  # Page numbers are zero-based in PyMuPDF, so add 1

        chunks_list = chunk_text(text, page_number, file.filename)  # Chunk the text using the chunk_text function


        for index, chunk in enumerate(chunks_list):
            db.add(
                chunks(
                   document_id=new_document.id,
                   chunk_index=index,
                   chunk_text=chunk,
                   source_document=new_document,
                   doc_category=category,  # Set the category for each chunk
                   page_number=page_number  # Set the page number for each chunk
            )
        )
        all_pages_text += text
        # print(f"Page {count + 1} text: {text}")  # Print the extracted text for each page
        count += 1
    new_document.content = all_pages_text
    new_document.page_count = count
    db.commit()
    db.refresh(new_document)

    # Generate embeddings for all chunks
    embedder()
    
    logger.info(f"PDF file uploaded and processed: {file.filename} with {count} pages and category: {category}")
    return {
    "filename": file.filename,
    "page_count": count,
    "text": all_pages_text
}



def clean_text(text):
    # Remove page numbers
    text = re.sub(r'Page\s+\d+(\s+of\s+\d+)?', '', text)

    # Remove standalone numbers (optional)
    text = re.sub(r'\b\d+\b', '', text)

    # Fix hyphenated words
    text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)

    # Merge wrapped lines
    text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)

    # Remove extra blank lines
    text = re.sub(r'\n{2,}', '\n\n', text)

    # Collapse spaces
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

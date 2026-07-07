from fastapi import UploadFile, File, APIRouter
import fitz  # PyMuPDF
from shared.database import SessionLocal, engine, Base
from .db_model import document, chunks
from .chunker import chunk_text
from .embedder import embedder
from .retriever import retrieve
import shared.init_db 
import re
router = APIRouter()
db = SessionLocal()


@router.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    # Open the PDF file 
    pdf_bytes = await file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    all_pages_text = ""
    count = 0
    for page in doc.pages():
        text = page.get_text()  # Extract text from the page
        # Process the extracted text as needed
        all_pages_text += text
        # print(f"Page {count + 1} text: {text}")  # Print the extracted text for each page
        count += 1
    # Clean the text using the clean_text function
    all_pages_text = clean_text(all_pages_text)
    # print(all_pages_text)  # Print the cleaned text for all pages

    new_document = document(title=file.filename, content=all_pages_text, page_count=count)
    db.add(new_document)
    db.commit()
    db.refresh(new_document)
    chunks_list = chunk_text(all_pages_text)  # Call the chunk_text function with the cleaned text and document ID

    for index, chunk in enumerate(chunks_list):

        db.add(
            chunks(
                document_id=new_document.id,
                chunk_index=index,
                chunk_text=chunk
            )
        )
    
    db.commit()

    # Generate embeddings for all chunks
    embedder()


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

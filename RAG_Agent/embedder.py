# Generate embeddings for all chunks
# Load all chunks from DB. Use all-MiniLM-L6-v2 to generate embeddings. Print the shape (num_chunks, 384) to verify.
# Create a FAISS FlatL2 index. Normalise vectors. Add all embeddings. Save with faiss.write_index() to disk.
#Save a list of {chunk_id, doc_id, content} as metadata.json alongside the FAISS index file for lookup after search.

from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json
from faiss import IndexFlatL2
from shared.database import SessionLocal
from .db_model import chunks

from fastapi import FastAPI
app = FastAPI()
db = SessionLocal()

all_chunks = db.query(chunks).all()
all_chunk_texts = [chunk.chunk_text for chunk in all_chunks]
model = SentenceTransformer('all-MiniLM-L6-v2')

def embedder():

    embeddings = model.encode(all_chunk_texts)
    print(f"Generated embeddings with shape: {embeddings.shape}")
    #faiss requires float32, so convert the embeddings to float32
    embeddings = embeddings.astype(np.float32)
    # Normalise vectors.
    faiss.normalize_L2(embeddings)
    # Create a FAISS FlatL2 index.
    index = IndexFlatL2(embeddings.shape[1])
    
    # Add all embeddings.
    index.add(embeddings)
    # Save with faiss.write_index() to disk.
    faiss.write_index(index, "faiss_index.bin")

    # Save a list of {chunk_id, doc_id, content} as metadata.json alongside the FAISS index file for lookup after search.
    metadata = []

    for chunk in all_chunks:
        metadata.append(
      {
            "chunk_id": chunk.id,
            "doc_id": chunk.document_id,
            "content": chunk.chunk_text
        }
        )    
    with open("metadata.json", "w") as f:
        json.dump(metadata, f)
    return embeddings.shape

#write command to intsall faiss and sentence-transformers if not already installed
#pip install faiss-cpu sentence-transformers
import os

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


model = SentenceTransformer('all-MiniLM-L6-v2')

def embedder():
    
    all_chunks = db.query(chunks).all()
    all_chunk_texts = [chunk.chunk_text for chunk in all_chunks]

    embeddings = model.encode(all_chunk_texts) # what is model.encode? It is a method from the SentenceTransformer class that generates embeddings for a list of texts. It takes a list of strings as input and returns a numpy array of embeddings, where each embedding corresponds to the input text at the same index. The embeddings are typically high-dimensional vectors that capture semantic information about the input texts.
    print(f"Generated embeddings with shape: {embeddings.shape}")
    # Normalise vectors.
    faiss.normalize_L2(embeddings)
    # Create a FAISS FlatL2 index.
    index = IndexFlatL2(embeddings.shape[1]) #what is embeddings.shape[1]? It is the number of dimensions of the embeddings. Each embedding is a vector in a high-dimensional space, and embeddings.shape[1] gives the size of that vector, which corresponds to the number of features or dimensions in the embedding space.
    
    # Add all embeddings.
    index.add(embeddings)
    
    if os.path.exists("faiss_index.bin"):
        os.remove("faiss_index.bin")
    # Save with faiss.write_index() to disk.
    faiss.write_index(index, "faiss_index.bin")

    # # Save a list of {chunk_id, doc_id, content} as metadata.json alongside the FAISS index file for lookup after search.
    # metadata = []

    # for chunk in all_chunks:
    #     metadata.append(
    #   {
    #         "chunk_id": chunk.id,
    #         "doc_id": chunk.document_id,
    #         "content": chunk.chunk_text
    #     }
    #     )    
    # with open("metadata.json", "w") as f:
    #     json.dump(metadata, f)
    return embeddings.shape

#write command to intsall faiss and sentence-transformers if not already installed
#pip install faiss-cpu sentence-transformers
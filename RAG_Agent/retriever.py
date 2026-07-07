from fastapi import APIRouter
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json

model = SentenceTransformer('all-MiniLM-L6-v2')
router = APIRouter()

@router.post("rag/search")
def retrieve_endpoint(query: str, top_k: int = 5):
    return retrieve(query, top_k)

def retrieve(query, top_k=5):
    # Load the FAISS index and metadata
    index = faiss.read_index("faiss_index.bin")
    with open("metadata.json", "r") as f:
        metadata = json.load(f)

    # Generate embedding for the query
    query_embedding = model.encode([query])
    query_embedding = query_embedding.astype(np.float32)
    faiss.normalize_L2(query_embedding)

    # Search the FAISS index
    distances, indices = index.search(query_embedding, top_k)

    # Retrieve the corresponding chunks from metadata
    results = []
    for idx in indices[0]:
        if idx < len(metadata):
            results.append(metadata[idx])

    return results
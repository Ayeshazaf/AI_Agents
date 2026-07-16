import os
from .db_model import chunks, document
from fastapi import APIRouter, Depends
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from shared.database import get_db
from sqlalchemy.orm import Session
from shared.logging_config import logger
from shared.init_db import Base

from CRM_Agent.model import  ChatHistory
model = SentenceTransformer('all-MiniLM-L6-v2')
router = APIRouter()


@router.post("/rag/search")
def retrieve_endpoint(query: str, top_k: int = 5, category_filter: str = None, db: Session = Depends(get_db)):
    logger.info(f"Received RAG search request with query: '{query}', top_k: {top_k}, category_filter: {category_filter}")
    if not os.path.exists("faiss_index.bin"):
        logger.error("FAISS index not found. Please upload documents and generate embeddings first.")
        return {"error": "FAISS index not found. Please upload documents and generate embeddings first."}

    # Load the FAISS index and metadata
    index = faiss.read_index("faiss_index.bin")
    #extract and store history from chat history 
    history = db.query(ChatHistory).order_by(ChatHistory.timestamp).all()
    logger.info(f"Retrieved chat history with {len(history)} messages.")
    # Generate embedding for the query
    query_embedding = model.encode([query])
    faiss.normalize_L2(query_embedding)

    # Search the FAISS index
    distances, indices = index.search(query_embedding, top_k)

    filtered = []

    for idx, score in zip(indices[0], distances[0]):

        if category_filter and chunks[idx].category != category_filter:
            continue

    filtered.append((chunks[idx], score))

    # Retrieve the corresponding chunks from metadata
    results = []
    for idx in indices:
        if idx < len(chunks):
            results.append(chunks[idx])
            
    logger.info(f"Retrieved {len(results)} chunks from FAISS index for query: '{query}'")
    
    llm_prompt = build_prompt(query, results, history)
    logger.info(f"Constructed LLM prompt: {llm_prompt}")
    llm_model = "Qwen2.5-3B-Instruct"
    llm_response = llm_model.generate(llm_prompt)
    
    return {
        "answer_chunks": [result["content"] for result in results],
        "sources": [
            {
                "doc_name": result["doc_name"],
                "page_number": result["page_number"],
                "score": float(distances[0][i]) if i < len(distances[0]) else 0.0
            }
            for i, result in enumerate(results)
        ],
        "total_tokens_estimated": len(build_prompt(query, results, history)) // 4,
        "llm_response": llm_response
    }



# Write a build_prompt(question, chunks, history=[]) function that returns a structured prompt string with system instruction, context block, conversation history, and question. Print the prompt for a test query to verify the format.
def build_prompt(query, retrieved_chunks, history):
    
    # System instruction
    system_instruction = "You are a helpful assistant. Use the provided context to answer the question."

    # Context block
    context_block = "\n".join([f"Chunk {i+1}: {chunk['content']}" for i, chunk in enumerate(retrieved_chunks)])

    # Conversation history
    history_block = "\n".join([f"User: {h.user_message}\nAssistant: {h.assistant_response}" for h in history])

    # Final prompt
    prompt = f"{system_instruction}\n\nContext:\n{context_block}\n\nHistory:\n{history_block}\n\nQuestion: {query}"

    return prompt
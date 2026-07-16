from fastapi import FastAPI

import shared.init_db
from CRM_Agent.routes import router as crm_router
from RAG_Agent.ingest import router as ingest_app
from RAG_Agent.retriever import router as rag_router
from Task_Agent.routes import router as task_router

app = FastAPI()

app.include_router(task_router)
app.include_router(ingest_app)
app.include_router(rag_router)
app.include_router(crm_router)
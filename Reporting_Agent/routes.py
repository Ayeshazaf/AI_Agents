from fastapi import FastAPI, Depends, APIRouter
import shared.init_db
from Task_Agent.routes import router as task_router
from RAG_Agent.ingest import router as ingest_app
from RAG_Agent.retriever import router as rag_router
from CRM_Agent.routes import router as crm_router
from CRM_Agent.intent import classify_intent, generate_response
from shared.database import get_db
from sqlalchemy.orm import Session
from shared.logging_config import logger
from CRM_Agent.model import Complaint, Customer
from Task_Agent.model import Task
from RAG_Agent.db_model import document, chunks

router = APIRouter()

@router.include_router(task_router, prefix="/tasks", tags=["tasks"])
@router.include_router(ingest_app, prefix="/ingest", tags=["ingest"])
@router.include_router(rag_router, prefix="/rag", tags=["rag"])
@router.include_router(crm_router, prefix="/crm", tags=["crm"])


@router.get("/weekly_report")
def generate_weekly_report(db: Session = Depends(get_db)):
    logger.info("Generating weekly report")
    
    # Fetch data for the report
    total_customers = db.query(Customer).count()
    total_complaints = db.query(Complaint).count()
    open_complaints = db.query(Complaint).filter(Complaint.status == "open").count()
    closed_complaints = db.query(Complaint).filter(Complaint.status == "closed").count()
    total_tasks = db.query(Task).count()

    report = {
        "total_customers": total_customers,
        "total_complaints": total_complaints,
        "open_complaints": open_complaints,
        "closed_complaints": closed_complaints,
        "total_tasks": total_tasks
    }

    logger.info(f"Weekly report generated: {report}")
    return report
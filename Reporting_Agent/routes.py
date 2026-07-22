from fastapi import FastAPI, Depends, APIRouter
import shared.init_db
from shared.database import get_db
from sqlalchemy.orm import Session
from shared.logging_config import logger
from CRM_Agent.model import Complaint, Customer
from Task_Agent.model import Task

router = APIRouter()


@router.get("/weekly_report")
def generate_weekly_report(db: Session = Depends(get_db)):
    logger.info("Generating weekly report")
    
    # Fetch data for the report
    try: 
        total_customers = db.query(Customer).count()
        total_complaints = db.query(Complaint).count()
        open_complaints = db.query(Complaint).filter(Complaint.status == "open").count()
        closed_complaints = db.query(Complaint).filter(Complaint.status == "closed").count()
        total_tasks = db.query(Task).count()
    except Exception as exc:
        logger.error("Error occurred while generating weekly report: %s", exc)
        raise

    report = {
        "total_customers": total_customers,
        "total_complaints": total_complaints,
        "open_complaints": open_complaints,
        "closed_complaints": closed_complaints,
        "total_tasks": total_tasks
    }

    logger.info(f"Weekly report generated: {report}")
    return report
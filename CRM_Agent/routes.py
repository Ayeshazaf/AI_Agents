from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from .model import Customer
from .model import Complaint , ComplaintStatus, ComplaintPriority
from .model import  ChatHistory
from datetime import datetime
from shared.database import get_db
from sqlalchemy.orm import Session
from .intent import classify_intent, generate_response
from .services import enforce_status_transition
from shared.logging_config import logger
import uuid
from shared.init_db import Base

router = APIRouter()
class CustomerCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., unique=True)
    phone_number: str = Field(..., max_length=20)
    address: str = Field(..., max_length=200)
    account_id: int = Field(..., unique=True)

class CustomerResponse(BaseModel):
    id: int
    name: str
    email: str
    phone_number: str
    address: str
    account_id: int


class ComplaintCreate(BaseModel):
    customer_id: int
    description: str
    status: ComplaintStatus
    priority: ComplaintPriority
    created_at: datetime

class ComplaintResponse(BaseModel):
    id: int
    customer_id: int
    description: str
    status: ComplaintStatus
    priority: ComplaintPriority

class IntentResult(BaseModel):
    intent: str


class ChatResponse(BaseModel):
    session_id: str
    last_messages: list[str]
    assistant_response: str
    intent_result: IntentResult

@router.get("/customers")
async def read_customers( db: Session = Depends(get_db)):
    logger.info("Fetching all customers")
    customers = db.query(Customer).all()
    logger.info(f"Retrieved {len(customers)} customers from the database")
    return [CustomerResponse(**customer.__dict__) for customer in customers]


@router.post("/customers", response_model=CustomerResponse)
async def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    logger.info(f"Creating a new customer with name: {customer.name}")
    try:
        db_customer = Customer(**customer.model_dump())
        db.add(db_customer)
        db.commit()
        db.refresh(db_customer)
        logger.info(f"Customer created with ID: {db_customer.id}")
        return CustomerResponse(**db_customer.__dict__)
    except Exception as e:
        logger.error(f"Error occurred while creating customer: {e}")
        raise

@router.get("/customers/{customer_id}")
async def read_customer(customer_id: int , db: Session = Depends(get_db)):
    logger.info(f"Fetching customer with ID: {customer_id}")
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if customer:
        logger.info(f"Customer found with ID: {customer_id}")
        return CustomerResponse(**customer.__dict__)
    logger.warning(f"Customer not found with ID: {customer_id}")
    return {"message": f"Customer {customer_id} not found"}

@router.delete("/customers/{customer_id}")
async def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    logger.info(f"Fetching customer with ID: {customer_id}")
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if customer:
        logger.info(f"Deleting customer with ID: {customer_id}")
        db.delete(customer)
        db.commit()
        return {"message": f"Customer {customer_id} deleted"}
    logger.warning(f"Customer not found with ID: {customer_id}")
    return {"message": f"Customer {customer_id} not found"}

@router.put("/customers/{customer_id}")
async def update_customer(customer_id: int, customer: CustomerCreate, db: Session = Depends(get_db)):
    existing_customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if existing_customer:
        logger.info(f"Updating customer with ID: {customer_id}")
        for key, value in customer.model_dump().items():
            setattr(existing_customer, key, value)  
        db.commit()
        logger.info(f"Customer updated with ID: {customer_id}")
        return {"message": f"Customer {customer_id} updated", "customer": customer}
    logger.warning(f"Customer not found with ID: {customer_id}")
    return {"message": f"Customer {customer_id} not found"}

# Build endpoints: POST /complaints, GET /complaints?customer_id=X, PUT /complaints/{id}/status, POST /complaints/{id}/escalate, POST /complaints/{id}/close.
@router.post("/complaints", response_model=ComplaintResponse)
async def create_complaint(complaint: ComplaintCreate, db: Session = Depends(get_db)):
    logger.info(f"Creating a new complaint for customer ID: {complaint.customer_id}")
    try:
        db_complaint = Complaint(**complaint.model_dump())
        db.add(db_complaint)
        db.commit()
        db.refresh(db_complaint)
        logger.info(f"Complaint created with ID: {db_complaint.id}")
    except Exception as e:
        logger.error(f"Error occurred while creating complaint: {e}")
        raise
    return {"message": "Complaint created", "complaint": complaint}
# GET /complaints should accept ?status=open and return results sorted by priority desc, then created_at asc. Verify the order is correct with Postman using 3 complaints of different priorities.
@router.get("/complaints")
async def read_complaints(customer_id: int = None, status: str = None, priority: ComplaintPriority = None, db: Session = Depends(get_db)):
    logger.info(f"Fetching complaints with filters - customer_id: {customer_id}, status: {status}, priority: {priority}")
    query = db.query(Complaint)
    if customer_id:
        query = query.filter(Complaint.customer_id == customer_id)
    if status:
        query = query.filter(Complaint.status == status)
    if priority:
        query = query.filter(Complaint.priority == priority)
    complaints = query.order_by(Complaint.priority.desc(), Complaint.created_at.asc()).all()
    logger.info(f"Retrieved {len(complaints)} complaints from the database")
    return complaints

@router.put("/complaints/{complaint_id}/status")
async def update_complaint_status(complaint_id: int, status: str, complaint:ComplaintCreate, db: Session = Depends(get_db)):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if complaint:
        logger.info(f"Updating complaint status for ID: {complaint_id}")
        enforce_status_transition(complaint.status, status)
        complaint.status = status
        db.commit()
        logger.info(f"Complaint {complaint_id} status updated to {status}")
        return {"message": f"Complaint {complaint_id} status updated to {status}"}
    logger.warning(f"Complaint not found with ID: {complaint_id}")
    return {"message": f"Complaint {complaint_id} not found"}

@router.post("/complaints/{complaint_id}/escalate")
async def escalate_complaint(complaint_id: int, complaint:ComplaintCreate, db: Session = Depends(get_db)):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if complaint:
        complaint.status = "escalated"
        db.commit()
        logger.info(f"Complaint {complaint_id} escalated")
        return {"message": f"Complaint {complaint_id} escalated"}
    logger.warning(f"Complaint not found with ID: {complaint_id}")
    return {"message": f"Complaint {complaint_id} not found"}

@router.post("/complaints/{complaint_id}/close")
async def close_complaint(complaint_id: int, complaint:ComplaintCreate, db: Session = Depends(get_db)):
    logger.info(f"Closing complaint with ID: {complaint_id}")
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if complaint:
        complaint.status = "closed"
        db.commit()
        logger.info(f"Complaint {complaint_id} closed")
        return {"message": f"Complaint {complaint_id} closed"}
    logger.warning(f"Complaint not found with ID: {complaint_id}")
    return {"message": f"Complaint {complaint_id} not found"}



@router.post("/crm/chat/", response_model=ChatResponse)
async def chat(session_id: str, customer_id: int, user_message: str, db: Session = Depends(get_db)):
    logger.info(f"Received chat message from customer ID: {customer_id} in session: {session_id}")
    if session_id is None:
        session_id = str(uuid.uuid4())
    # Add the new user message
    new_user_message = ChatHistory(
        session_id=session_id,
        customer_id=customer_id,
        role="user",
        message=user_message,
        created_at=datetime.now(),
    )
    db.add(new_user_message)
    db.commit()

    # Fetch the last 3 messages
    last_messages = db.query(ChatHistory).filter(ChatHistory.session_id == session_id).order_by(ChatHistory.created_at.desc()).limit(3).all()

    # Classify intent and generate response
    intent_result = classify_intent(user_message)
    assistant_response = generate_response(intent_result["intent"], customer_id=customer_id, db=db)

    # Add the assistant response
    new_assistant_message = ChatHistory(
        session_id=session_id,
        customer_id=customer_id,
        role="assistant",
        message=assistant_response,
        created_at=datetime.now(),
    )
    db.add(new_assistant_message)
    db.commit()
    logger.info(f"Assistant response added to session: {session_id}")
    return { "session_id": session_id, "last_messages": [msg.message for msg in last_messages], "assistant_response": assistant_response, "intent_result": intent_result}

#why are we using logger.info etc when we are returning the response to the user? The logger is used for internal logging purposes, allowing developers and system administrators to track the flow of operations, debug issues, and monitor the application's behavior. It provides a record of events that occur during the execution of the application, which can be invaluable for troubleshooting and understanding how the application is performing.
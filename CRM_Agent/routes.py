from fastapi import APIRouter
from pydantic import BaseModel, Field
from .model import Customer
from .model import Complaint , ComplaintStatus, ComplaintPriority
from .model import  ChatHistory
from datetime import datetime
from shared.database import SessionLocal
from .intent import classify_intent, generate_response
import uuid
db = SessionLocal()

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

 
@router.get("/customers")
async def read_customers():
    customers = db.query(Customer).all()
    return [CustomerResponse(**customer.__dict__) for customer in customers]

@router.post("/customers", response_model=CustomerResponse)
async def create_customer(customer: CustomerCreate):
    db_customer = Customer(**customer.dict())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return CustomerResponse(**db_customer.__dict__)

@router.get("/customers/{customer_id}")
async def read_customer(customer_id: int):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if customer:
        return CustomerResponse(**customer.__dict__)
    return {"message": f"Customer {customer_id} not found"}

@router.delete("/customers/{customer_id}")
async def delete_customer(customer_id: int):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if customer:
        db.delete(customer)
        db.commit()
        return {"message": f"Customer {customer_id} deleted"}
    return {"message": f"Customer {customer_id} not found"}

@router.put("/customers/{customer_id}")
async def update_customer(customer_id: int, customer: CustomerCreate):
    existing_customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if existing_customer:
        for key, value in customer.dict().items():
            setattr(existing_customer, key, value)
        db.commit()
        return {"message": f"Customer {customer_id} updated", "customer": customer}
    return {"message": f"Customer {customer_id} not found"}

# Build endpoints: POST /complaints, GET /complaints?customer_id=X, PUT /complaints/{id}/status, POST /complaints/{id}/escalate, POST /complaints/{id}/close.
@router.post("/complaints", response_model=ComplaintResponse)
async def create_complaint(complaint: ComplaintCreate):
    db_complaint = Complaint(**complaint.dict())
    db.add(db_complaint)
    db.commit()
    db.refresh(db_complaint)
    return {"message": "Complaint created", "complaint": complaint}
# GET /complaints should accept ?status=open and return results sorted by priority desc, then created_at asc. Verify the order is correct with Postman using 3 complaints of different priorities.
@router.get("/complaints")
async def read_complaints(customer_id: int = None, status: str = None, priority: ComplaintPriority = None):
    query = db.query(Complaint)
    if customer_id:
        query = query.filter(Complaint.customer_id == customer_id)
    if status:
        query = query.filter(Complaint.status == status)
    if priority:
        query = query.filter(Complaint.priority == priority)
    complaints = query.order_by(Complaint.priority.desc(), Complaint.created_at.asc()).all()
    return complaints

@router.put("/complaints/{complaint_id}/status")
async def update_complaint_status(complaint_id: int, status: str, complaint:ComplaintCreate ):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if complaint:
        complaint.status = status
        db.commit()
        return {"message": f"Complaint {complaint_id} status updated to {status}"}
    return {"message": f"Complaint {complaint_id} not found"}

@router.post("/complaints/{complaint_id}/escalate")
async def escalate_complaint(complaint_id: int, complaint:ComplaintCreate):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if complaint:
        complaint.status = "escalated"
        db.commit()
        return {"message": f"Complaint {complaint_id} escalated"}
    return {"message": f"Complaint {complaint_id} not found"}

@router.post("/complaints/{complaint_id}/close")
async def close_complaint(complaint_id: int, complaint:ComplaintCreate):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if complaint:
        complaint.status = "closed"
        db.commit()
        return {"message": f"Complaint {complaint_id} closed"}
    return {"message": f"Complaint {complaint_id} not found"}


# Load the session by session_id.
# Fetch the last 3 messages from chat_messages ordered by created_at.
# Add the new user message.
# Add the assistant response.
# Return the last 3 messages.
@router.post("/crm/chat/")
async def chat(session_id: str,customer_id: int , user_message: str):
    if session_id is None:
        session_id = str(uuid.uuid4())


    # Add the new user message
    new_user_message = new_user_message = ChatHistory(
    session_id=session_id,
    customer_id=customer_id,
    role="user",
    message=user_message,
    created_at=datetime.utcnow(),
)
    db.add(new_user_message)
    db.commit()

    # Fetch the last 3 messages
    last_messages = db.query(ChatHistory).filter(ChatHistory.session_id == session_id).order_by(ChatHistory.created_at.desc()).limit(3).all()

    # Classify intent and generate response
    intent_result = classify_intent(user_message)
    assistant_response = generate_response(intent_result["intent"])

    # Add the assistant response
    new_assistant_message = new_user_message = ChatHistory(
    session_id=session_id,
    customer_id=customer_id,
    role="assistant",
    message=assistant_response,
    created_at=datetime.utcnow(),
)
    db.add(new_assistant_message)
    db.commit()
    return { "session_id": session_id, "last_messages": [msg.message for msg in last_messages], "assistant_response": assistant_response, "intent_result": intent_result}
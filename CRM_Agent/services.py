from django.db import router

from .model import ComplaintStatus, Complaint
from fastapi import HTTPException

# Valid transitions
# Open → In-review, Escalated
# In-review → Resolved, Escalated
# Resolved → Closed, Open (if customer rejects resolution)
# Escalated → In-review, Closed
# Closed → nothing (terminal)

VALID_STATUSES = {
    "open" : ["in_review", "escalated"],
    "in_review" : ["resolved", "escalated"],
    "resolved" : ["closed", "open"],
    "escalated" : ["in_review", "closed"],
    "closed" : []
}

def enforce_status_transition(current_status: ComplaintStatus, new_status: ComplaintStatus):
    if current_status == new_status:
        return  # No transition needed

    if current_status not in VALID_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid current status: {current_status}"
        )
    if new_status not in VALID_STATUSES[current_status]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot transition from {current_status} to {new_status}"
        )

def create_complaint(db, complaint_data):
    new_complaint = Complaint(**complaint_data)
    db.add(new_complaint)
    db.commit()
    db.refresh(new_complaint)
    return new_complaint

def update_complaint_priority(db, customer_id, new_priority):
    complaint = db.query(Complaint).filter(Complaint.customer_id == customer_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail=f"Complaint for customer {customer_id} not found")
    
    complaint.priority = new_priority
    db.commit()
    db.refresh(complaint)
    
    return complaint

def close_complaint(db, customer_id):
    complaint = db.query(Complaint).filter(Complaint.customer_id == customer_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail=f"Complaint for customer {customer_id} not found")
    
    enforce_status_transition(complaint.status, "closed")
    
    complaint.status = "closed"
    db.commit()
    db.refresh(complaint)
    
    return complaint


def check_complaint_status(db, customer_id):
    complaint = db.query(Complaint).filter(Complaint.customer_id == customer_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail=f"Complaint for customer {customer_id} not found")
    
    return complaint.status

def escalate_complaint(db, customer_id):
    complaint = db.query(Complaint).filter(Complaint.customer_id == customer_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail=f"Complaint for customer {customer_id} not found")
    
    enforce_status_transition(complaint.status, "escalated")
    
    complaint.status = "escalated"
    db.commit()
    db.refresh(complaint)
    
    return complaint

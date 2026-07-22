from __future__ import annotations
import re

from CRM_Agent.model import ComplaintStatus
from .services import create_complaint, update_complaint_priority, close_complaint, check_complaint_status, escalate_complaint
from datetime import datetime


def classify_intent(text: str):
    lower_text = text.lower()
    lower_text = re.findall(r"\b\w+\b", lower_text)

    if any(greeting in lower_text for greeting in ["hello","hi","hey"]):
        return {"intent": "greeting"}

    if any(keyword in lower_text for keyword in [
        "create complaint",
        "new complaint",
        "file complaint",
        "register",
        "issue",
        "problem"
    ]):
        return {"intent":"create_complaint"}

        # Status
    if "status" in text:
        return {"intent": "check_status"}

    # Priority
    if "priority" in text:
        return {"intent": "update_priority"}

    # Close
    if any(word in text for word in [
        "close",
        "resolved",
        "fixed"
    ]):
        return {"intent": "close_complaint"}

    # Escalate
    if any(word in text for word in [
        "escalate",
        "manager",
        "technical support"
    ]):
        return {"intent": "escalate"}

    return {"intent": "unknown"}


def generate_priority(intent):
    if intent in {"create_complaint", "escalate"}:
        return 3
    if intent in {"update_priority"}:
        return 2
    return 1


def generate_response(intent, customer_id, db):
    if intent == "greeting":
        return "Hello! How can I assist you today?"
    elif intent == "create_complaint":
        create_complaint(db, {"customer_id": customer_id, "description": "New complaint", "status": ComplaintStatus.open, "priority": generate_priority(intent), "created_at": datetime.now()})
        return  "Complaint created successfully."
           
    elif intent == "update_priority":
        update_complaint_priority(db, customer_id, generate_priority(intent))
        return  "Complaint priority updated successfully."
           
    elif intent == "close_complaint":
        close_complaint(db, customer_id)
        return  "Complaint closed successfully."
        
    elif intent == "check_status":
        status = check_complaint_status(db, customer_id)
        return f"Complaint status is: {status}"
            
    elif intent == "escalate":
        escalate_complaint(db, customer_id)
        return "Complaint escalated successfully."
    else :
        return "I'm sorry, I didn't understand your request. Could you please clarify?"
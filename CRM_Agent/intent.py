from __future__ import annotations
from .services import create_complaint, update_complaint_priority, close_complaint, check_complaint_status, escalate_complaint
from datetime import datetime


def classify_intent(text: str):
    lower_text = text.lower()
    if any(greeting in lower_text for greeting in ["hello", "hi", "hey"]):
        return "greeting"
    if any(keyword in lower_text for keyword in ["create complaint", "new complaint", "file complaint", "register", "issue", "problem"]):
        return "create_complaint"
    if any(keyword in lower_text for keyword in ["update priority", "change priority"]):
        return "update_priority"
    if any(keyword in lower_text for keyword in ["close complaint", "resolve complaint"]):
        return "close_complaint"
    if any(keyword in lower_text for keyword in ["check status", "status of complaint"]):
        return "check_status"
    if any(keyword in lower_text for keyword in ["escalate", "raise complaint"]):
        return "escalate"

    return "unknown"


def generate_priority(intent):
    if intent in {"create_complaint", "escalate"}:
        return 3
    if intent in {"update_priority"}:
        return 2
    return 1


def generate_response(intent, customer_id, db):
    if intent == "greeting":
        return "Hello! How can I assist you today?"
    if intent == "create_complaint":
        create_complaint(db, {"customer_id": customer_id, "description": "New complaint", "status": "open", "priority": generate_priority(intent), "created_at": datetime.now()})
        return {
            "message": "Complaint created successfully.",
            "complaint_id": None,
            "customer_id": customer_id,
        }
    if intent == "update_priority":
        update_complaint_priority(db, customer_id, generate_priority(intent))
        return {
            "message": "Complaint priority updated successfully.",
            "complaint_id": None,
            "customer_id": customer_id,
        }
    if intent == "close_complaint":
        close_complaint(db, customer_id)
        return {
            "message": "Complaint closed successfully.",
            "complaint_id": None,
            "customer_id": customer_id,
        }
    if intent == "check_status":
        check_complaint_status(db, customer_id)
        return {
            "message": "Complaint status is unavailable in this demo UI.",
            "complaint_id": None,
            "customer_id": customer_id,
        }
    if intent == "escalate":
        escalate_complaint(db, customer_id)
        return {
            "message": "Complaint escalated successfully.",
            "complaint_id": None,
            "customer_id": customer_id,
        }
    return "I'm sorry, I didn't understand your request. Could you please clarify?"
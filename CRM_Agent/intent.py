#use llm to classify intent and generate response for CRM agent
from datetime import datetime

from CRM_Agent.model import Complaint

from .routes import router

def classify_intent(text: str):

    llm_model = "Qwen2.5-3B-Instruct"
    # Define a set of intents and their corresponding keywords
    intents = {
        "greeting": ["hello", "hi", "hey"],
        "create_complaint": ["complaint", "issue", "problem"],
        "update_priority": ["priority", "urgent", "high"],
        "close_complaint": ["close", "resolve", "finish"],
        "check_status": ["status", "progress", "update"],
        "escalate": ["escalate", "urgent", "immediate"],
        "unknown": []
    }
    llm_prompt = f"Classify the intent of the following text: '{text}'. Possible intents are: {', '.join(intents.keys())}. Return the intent and confidence score."
    llm_response = llm_model.generate(llm_prompt)
    
    return {
        "intent": llm_response.intent,
        "confidence": llm_response.confidence
    }

def generate_priority(intent):
    
    prompt = f"Based on the intent '{intent}', determine the appropriate priority level for the complaint. Return a priority level between 3 (highest) and 1 (lowest). e.g keywords: urgent, immediate, critical -> 3; important, high -> 2; low, minor -> 1"
    llm_model = "Qwen2.5-3B-Instruct"
    llm_response = llm_model.generate(prompt)
    return int(llm_response.strip()) if llm_response.strip().isdigit() else 2  # Default to medium priority if not a number

def generate_response(intent, customer_id, db):
    
    # Based on the intent, generate a response using the LLM
    llm_model = "Qwen2.5-3B-Instruct"
    if intent == "greeting":
        response_prompt = "Generate a friendly greeting response."
        llm_response = llm_model.generate(response_prompt)
    elif intent == "create_complaint":
        create_complaint = router.create_complaint(
            customer_id=customer_id, 
            description= intent, 
            status="open", 
            priority=generate_priority(intent),
            created_at= datetime.now().isoformat(),
        )
        return {"message": f"Complaint created successfully with ID: {create_complaint.id}"}
    elif intent == "update_priority":
        update_priority = router.update_complaint_priority(
            customer_id=customer_id,
            complaint_id= db.query(Complaint).filter(Complaint.customer_id == customer_id).first().id,
            priority=generate_priority(intent)
        )
        return {"message": f"Complaint priority updated successfully with ID: {update_priority.id}"}
    elif intent == "close_complaint":
        close_complaint = router.close_complaint(
            customer_id=customer_id,
            complaint_id= db.query(Complaint).filter(Complaint.customer_id == customer_id).first().id,
            status="closed"
        )
        return {"message": f"Complaint closed successfully with ID: {close_complaint.id}"}
    elif intent == "check_status":
        check_status = router.get_complaint_status(
            customer_id=customer_id,
            complaint_id= db.query(Complaint).filter(Complaint.customer_id == customer_id).first().id,
            status= db.query(Complaint).filter(Complaint.customer_id == customer_id).first().status
        )
        return {"message": f"Complaint status is: {check_status.status}"}
    elif intent == "escalate":
        escalate_complaint = router.escalate_complaint(
            customer_id=customer_id,
            complaint_id= db.query(Complaint).filter(Complaint.customer_id == customer_id).first().id,
            status="escalated"
        )
        return {"message": f"Complaint escalated successfully with ID: {escalate_complaint.id}"}
    else:
        response_prompt = "Generate a generic response indicating that the request is not understood."
        llm_response = llm_model.generate(response_prompt)

    return llm_response
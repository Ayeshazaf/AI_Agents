from __future__ import annotations

from .model import Task
from .services import create_task, delete_task, update_task


def classify_intent(text: str):
    if any(greeting in text.lower() for greeting in ["hello", "hi", "hey"]):
        return "greeting"
    elif any(keyword in text.lower() for keyword in ["create", "new", "add"]):
        return "create_task"
    elif any(keyword in text.lower() for keyword in ["update", "modify", "change"]):
        return "update_task"
    elif any(keyword in text.lower() for keyword in ["delete", "remove", "discard"]):
        return "delete_task"
    
    return {"intent": "unknown", "confidence": 0.5}


def extract_task_title(text: str):
    
    return "Task Title"


def extract_task_piriority(text: str):
    
    return "medium"


def extract_task_due_date(text: str):
    
    return "tomorrow"

def generate_response(intent, text, db):
    if intent == "greeting":
        return {"message": "Hello! How can I assist you with your tasks today?"}
    if intent == "create_task":
        created_task = create_task(
            db,
            {
                "title": extract_task_title(text),
                "description": text,
                "status": "pending",
                "priority": extract_task_piriority(text),
                "due_date": extract_task_due_date(text),
            },
        )
        return {"message": f"Task created successfully with ID: {created_task.id}"}
    if intent == "update_task":
        existing_task = db.query(Task).filter(Task.title == extract_task_title(text)).first()
        if not existing_task:
            return {"message": "Task not found"}
        updated_task = update_task(
            task_id=existing_task.id,
            title=extract_task_title(text),
            description=text,
            status=existing_task.status,
            priority=extract_task_piriority(text),
            due_date=extract_task_due_date(text),
            db=db,
        )
        return {"message": f"Task updated successfully with ID: {updated_task.id}"}
    if intent == "delete_task":
        existing_task = db.query(Task).filter(Task.title == extract_task_title(text)).first()
        if not existing_task:
            return {"message": "Task not found"}
        delete_task(existing_task.id, db)
        return {"message": f"Task deleted successfully with ID: {existing_task.id}"}
    return {"message": "Task intent is unknown."}
from __future__ import annotations

from .model import Task
from .services import create_task, delete_task, update_task

llm_model = "Qwen2.5-3B-Instruct"

def classify_intent(text: str):
    llm_prompt = f"""
You are a task management assistant. Classify the intent of the following user message into one of the following categories: greeting, create_task, update_task, delete_task, unknown.
User message: "{text}"
Return the intent as a JSON object with the following format:
{{"intent": "greeting", "confidence"}}"""

    llm_response = llm_model.generate(llm_prompt)
    
    return llm_response


def extract_task_title(text: str):
    llm_prompt = f"""
You are a task management assistant. Extract the title of the task from the following user message.
User message: "{text}"
Return the title as a string. If no title can be extracted, return "No title found"."""
    llm_generated_title = llm_model.generate(llm_prompt)
    if not llm_generated_title:
        llm_prompt2 = f"""
You are a task management assistant. Ask the user for the title of the task by asking what task they want to create in a friendly language. Return the question as a string."""
        llm_response = llm_model.generate(llm_prompt2)
        return llm_response
    return llm_generated_title.strip() 


def extract_task_piriority(text: str):
    llm_prompt = f"""
You are a task management assistant. Extract the priority of the task from the following user message.
User message: "{text}"
Return the priority as a string. If no priority can be extracted, return medium priority."""
    llm_generated_priority = llm_model.generate(llm_prompt)
    return llm_generated_priority.strip() if llm_generated_priority else "medium priority"


def extract_task_due_date(text: str):
    llm_prompt = f"""
You are a task management assistant. Extract the due date of the task from the following user message.
User message: "{text}"  
Return the due date as a string. If no due date can be extracted, return "tomorrow"."""
    llm_generated_due_date = llm_model.generate(llm_prompt)
    return llm_generated_due_date.strip() if llm_generated_due_date else "tomorrow"

def generate_response(intent, text, db):
    if intent == "greeting":
        llm_prompt = f"""
You are a task management assistant. Respond to the following user message in a friendly and helpful manner.
User message: "{text}"
Return the response as a string."""
        llm_response = llm_model.generate(llm_prompt)
        return {"message": llm_response.strip() if llm_response else "Hello! How can I assist you with your tasks today?"}
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
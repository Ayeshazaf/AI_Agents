from .model import TaskStatus
from fastapi import HTTPException
from .model import Task
from datetime import datetime

ALLOWED_TRANSITIONS = {
    "pending": ["in_progress"],
    "in_progress": ["completed"],
    "completed": []
}

def enforce_status_transition(current_status: TaskStatus, new_status: TaskStatus):
    if current_status == new_status:
        return  # No transition needed

    if current_status not in ALLOWED_TRANSITIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid current status: {current_status}"
        )
    if new_status not in ALLOWED_TRANSITIONS[current_status]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot transition from {current_status} to {new_status}"
        )
        
def create_task(db, task_data):
    new_task = Task(**task_data)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

def update_task(task_id, title, description, status, priority, due_date, db):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    enforce_status_transition(task.status, status)
    
    task.title = title
    task.description = description
    task.status = status
    task.priority = priority
    task.due_date = due_date
    task.updated_at = datetime.now()
    
    db.commit()
    db.refresh(task)
    
    return task

def delete_task(task_id, db):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    db.delete(task)
    db.commit()
    
    return {"message": f"Task {task_id} deleted"}

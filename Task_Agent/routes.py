from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from .model import Task
from shared.database import get_db
from datetime import datetime
from .services import enforce_status_transition
from shared.logging_config import logger
from shared.init_db import Base

router = APIRouter()

class TaskCreate(BaseModel):
    id: int
    title: str = Field(..., min_length=1)
    description: str
    status: str
    priority: str
    
class TaskResponse(BaseModel):
    id: int
    title: str

@router.get("/tasks")
async def read_tasks(db: Session = Depends(get_db)):  
    logger.info("Fetching all tasks")
    tasks = db.query(Task).all()
    logger.info(f"Retrieved {len(tasks)} tasks from the database")
    return tasks

@router.post("/tasks", response_model=TaskResponse)
async def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    logger.info(f"Creating a new task with title: {task.title}")
    try:
        db_task = Task(**task.model_dump())
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        logger.info(f"Task created with ID: {db_task.id}")
        return TaskResponse(**db_task.__dict__)
    except Exception as e:
        logger.error(f"Error occurred while creating task: {e}")
        raise

@router.get("/tasks/{task_id}")
async def read_task(task_id: int, db: Session = Depends(get_db)):
    logger.info(f"Fetching task with ID: {task_id}")
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        logger.info(f"Task found with ID: {task_id}")
        return TaskResponse(**task.__dict__)
    logger.warning(f"Task not found with ID: {task_id}")
    return {"message": f"Task {task_id} not found"}

@router.delete("/tasks/{task_id}")
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        logger.info(f"Deleting task with ID: {task_id}")
        task.updated_at = datetime.now()
        db.delete(task)
        db.commit()
        return {"message": f"Task {task_id} deleted"}
    logger.warning(f"Task not found with ID: {task_id}")
    return {"message": f"Task {task_id} not found"}

@router.put("/tasks/{task_id}")
async def update_task(task_id: int, task: TaskCreate, db: Session = Depends(get_db)):
    existing_task = db.query(Task).filter(Task.id == task_id).first()
    if existing_task:
        logger.info(f"Updating task with ID: {task_id}")
        for key, value in task.model_dump().items():
            setattr(existing_task, key, value)# Enforce transition logic
        
        enforce_status_transition(existing_task, task.status)
        existing_task.updated_at = datetime.now()
        db.commit()
        logger.info(f"Task updated with ID: {task_id}")
        return {"message": f"Task {task_id} updated", "task": task}
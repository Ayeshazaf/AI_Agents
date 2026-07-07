from fastapi import APIRouter, Depends, FastAPI
from pydantic import BaseModel, Field
from .model import Task
from shared.database import SessionLocal
router = APIRouter()
# tasks = []
db = SessionLocal()

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
async def read_tasks():  
    return db.query(Task).all()

@router.post("/tasks", response_model=TaskResponse)
async def create_task(task: TaskCreate):
    db_task = Task(**task.dict())
    task.updated_at = datetime.utcnow()
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return TaskResponse(**db_task.__dict__)

@router.get("/tasks/{task_id}")
async def read_task(task_id: int):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        return TaskResponse(**task.__dict__)
    return {"message": f"Task {task_id} not found"}

@router.delete("/tasks/{task_id}")
async def delete_task(task_id: int):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        task.updated_at = datetime.utcnow()
        db.delete(task)
        db.commit()
        return {"message": f"Task {task_id} deleted"}
    return {"message": f"Task {task_id} not found"}

@router.put("/tasks/{task_id}")
async def update_task(task_id: int, task: TaskCreate):
    existing_task = db.query(Task).filter(Task.id == task_id).first()
    if existing_task:
        for key, value in task.dict().items():
            setattr(existing_task, key, value)
        task.updated_at = datetime.utcnow()
        db.commit()
        return {"message": f"Task {task_id} updated", "task": task}
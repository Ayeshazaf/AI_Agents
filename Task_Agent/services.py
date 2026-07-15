from .model import TaskStatus
from fastapi import HTTPException

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
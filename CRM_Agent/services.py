from .model import ComplaintStatus
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
if new_status not in VALID_STATUSES[current_status]:
    raise HTTPException(
        status_code=400,
        detail=f"Cannot transition from {current_status} to {new_status}"
    )

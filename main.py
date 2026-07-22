from fastapi import FastAPI

import shared.init_db
from CRM_Agent.routes import router as crm_router
from Task_Agent.routes import router as task_router
from Reporting_Agent.routes import router as reporting_router
app = FastAPI()

app.include_router(task_router)
app.include_router(crm_router)
app.include_router(reporting_router)
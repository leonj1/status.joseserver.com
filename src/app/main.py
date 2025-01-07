from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import init_db, get_db
from app.models.incident import Incident
from app.schemas.incident import IncidentCreate, IncidentResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Initialize application state on startup.
    """
    app.state.boot_time = datetime.utcnow()
    await init_db()
    yield

app = FastAPI(
    title="Status Service",
    description="Health check service for joseserver.com",
    version="0.1.0",
    lifespan=lifespan
)

@app.get("/health")
async def health_check() -> JSONResponse:
    """
    Health check endpoint that returns the service status.
    """
    return JSONResponse(
        content={
            "status": "healthy",
            "version": app.version,
            "timestamp": str(app.state.boot_time)
        },
        status_code=200
    )

@app.post("/incidents", response_model=IncidentResponse)
async def create_incident(
    incident_data: IncidentCreate,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Create a new incident record.
    """
    incident = Incident(
        service=incident_data.service,
        previous_state=incident_data.previous_state,
        current_state=incident_data.current_state,
        title=incident_data.incident.title,
        description=incident_data.incident.description,
        components=incident_data.incident.components,
        url=str(incident_data.incident.url)
    )
    
    db.add(incident)
    await db.commit()
    await db.refresh(incident)
    
    return incident.to_dict()
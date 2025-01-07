from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, Depends, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import init_db, get_db
from app.models.incident import Incident
from app.models.history import IncidentHistory
from app.schemas.incident import IncidentCreate, IncidentResponse
from app.schemas.history import IncidentWithHistory, IncidentHistoryResponse

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

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://status.joseserver.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
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

@app.post("/incidents", response_model=IncidentWithHistory)
async def create_incident(
    incident_data: IncidentCreate,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Create a new incident record and record it in history.
    """
    # Create the incident
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
    
    # Create history entry
    history_entry = IncidentHistory(
        incident_id=incident.id,
        service=incident.service,
        previous_state=incident.previous_state,
        current_state=incident.current_state,
        title=incident.title,
        description=incident.description,
        components=incident.components,
        url=incident.url
    )
    
    db.add(history_entry)
    await db.commit()
    await db.refresh(incident)  # Refresh to get the new history
    
    return incident.to_dict()

@app.get("/incidents/{incident_id}/history", response_model=List[IncidentHistoryResponse])
async def get_incident_history(
    incident_id: int,
    db: AsyncSession = Depends(get_db)
) -> List[dict]:
    """
    Get the history of changes for a specific incident.
    """
    query = select(IncidentHistory).filter(IncidentHistory.incident_id == incident_id)
    result = await db.execute(query)
    history = result.scalars().all()
    
    return [entry.to_dict() for entry in history]

@app.get("/incidents/recent", response_model=List[IncidentWithHistory])
async def get_recent_incidents(
    start_date: Optional[datetime] = Query(
        None,
        description="Start date for incidents (ISO format). If not provided, returns most recent incidents."
    ),
    count: int = Query(
        10,
        ge=1,
        le=50,
        description="Number of incidents to return (max 50)"
    ),
    db: AsyncSession = Depends(get_db)
) -> List[dict]:
    """
    Get recent incidents with optional date filtering.
    Returns the most recent incidents by default, limited to 10 unless specified otherwise.
    """
    query = select(Incident).order_by(desc(Incident.created_at))
    
    if start_date:
        query = query.filter(Incident.created_at >= start_date)
    
    query = query.limit(count)
    
    result = await db.execute(query)
    incidents = result.scalars().all()
    
    return [incident.to_dict() for incident in incidents]
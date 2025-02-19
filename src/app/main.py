from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Optional
import random
from fastapi import FastAPI, Depends, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, and_

from app.core.database import init_db, get_db
from app.models.incident import Incident
from app.models.history import IncidentHistory
from app.schemas.incident import IncidentCreate, IncidentResponse, IncidentDetail
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
    count: Optional[int] = Query(
        None,  # No default, so None means "latest per service"
        ge=1,
        le=50,
        description="Number of incidents to return (max 50). If not provided, returns latest per service."
    ),
    db: AsyncSession = Depends(get_db)
) -> List[dict]:
    """
    Get recent incidents with optional date filtering.
    Returns the most recent incidents by default, limited to 10 unless specified otherwise.
    """
    # Base query to get all incidents
    base_query = select(Incident)

    if start_date:
        # When filtering by date, return all matching incidents
        base_query = base_query.filter(Incident.created_at >= start_date)

    if count is not None:
        # When count is provided, return that many most recent incidents
        query = (
            base_query
            .order_by(desc(Incident.created_at))
            .limit(count)
        )
    else:
        # Default behavior: return latest incident per service
        # First, get the latest incident per service using a CTE
        latest_per_service = (
            select(
                Incident.service,
                func.max(Incident.created_at).label('max_created_at')
            )
            .group_by(Incident.service)
            .cte('latest_per_service')
        )

        # Then join with the main table to get the full incident details
        query = (
            base_query
            .join(
                latest_per_service,
                and_(
                    Incident.service == latest_per_service.c.service,
                    Incident.created_at == latest_per_service.c.max_created_at
                )
            )
            .order_by(desc(Incident.created_at))
        )

    result = await db.execute(query)
    incidents = result.scalars().all()
    
    return [incident.to_dict() for incident in incidents]

@app.get("/incidents/generate", response_model=IncidentWithHistory)
async def generate_random_incident(
    state: Optional[str] = Query(
        None,
        description="Desired state for the incident",
        enum=["operational", "degraded", "outage", "maintenance"]
    ),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Generate and create a random incident for testing purposes.
    Optionally specify the desired state of the incident.
    """
    services = ["api", "database", "web", "auth", "storage", "compute"]
    states = ["operational", "degraded", "outage", "maintenance"]
    component_types = ["server", "database", "cache", "load-balancer", "api"]
    
    service = random.choice(services)
    # Use provided state or random if not provided
    current_state = state if state else random.choice(states)
    # Ensure previous state is different from current
    previous_state = random.choice([s for s in states if s != current_state])
    
    # Generate 1-3 random components
    components = random.sample(component_types, random.randint(1, 3))
    
    # Generate incident title based on service and state
    titles = [
        f"{service.title()} Service {current_state.title()} Detected",
        f"Unexpected {current_state.title()} in {service.title()} System",
        f"{service.title()} Performance {current_state.title()}",
        f"Investigating {service.title()} Service Issues"
    ]
    
    descriptions = [
        f"Our monitoring system detected {current_state} status in the {service} service affecting {', '.join(components)}.",
        f"We are investigating reports of {current_state} performance in the {service} system.",
        f"Engineers are responding to {current_state} alerts from {service} service components.",
        f"Automated systems detected abnormal behavior in {service} service {components[0]}."
    ]
    
    incident_data = IncidentCreate(
        service=service,
        previous_state=previous_state,
        current_state=current_state,
        incident=IncidentDetail(
            title=random.choice(titles),
            description=random.choice(descriptions),
            components=components,
            url=f"https://status.joseserver.com/incidents/{service}-{int(datetime.utcnow().timestamp())}"
        )
    )
    
    # Use the existing create_incident logic
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
    await db.refresh(incident)
    
    return incident.to_dict()

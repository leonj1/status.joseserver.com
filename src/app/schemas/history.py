from datetime import datetime
from pydantic import BaseModel
from app.schemas.incident import IncidentDetail

class IncidentHistoryResponse(BaseModel):
    id: int
    incident_id: int
    recorded_at: datetime
    service: str
    previous_state: str
    current_state: str
    incident: IncidentDetail

    class Config:
        from_attributes = True

class IncidentWithHistory(BaseModel):
    id: int
    service: str
    previous_state: str
    current_state: str
    created_at: datetime
    incident: IncidentDetail
    history: list[IncidentHistoryResponse]

    class Config:
        from_attributes = True
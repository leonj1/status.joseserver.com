from datetime import datetime
from typing import List
from pydantic import BaseModel, HttpUrl

class IncidentDetail(BaseModel):
    title: str
    description: str
    components: List[str]
    url: HttpUrl

class IncidentCreate(BaseModel):
    service: str
    previous_state: str
    current_state: str
    incident: IncidentDetail

class IncidentResponse(BaseModel):
    id: int
    service: str
    previous_state: str
    current_state: str
    created_at: datetime
    incident: IncidentDetail

    class Config:
        from_attributes = True
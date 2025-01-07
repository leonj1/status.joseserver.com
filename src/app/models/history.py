from datetime import datetime
from typing import List
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class IncidentHistory(Base):
    __tablename__ = "incident_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    incident_id: Mapped[int] = mapped_column(ForeignKey("incidents.id"))
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    service: Mapped[str] = mapped_column(String(100))
    previous_state: Mapped[str] = mapped_column(String(50))
    current_state: Mapped[str] = mapped_column(String(50))
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(String(1000))
    components: Mapped[List[str]] = mapped_column(JSON)
    url: Mapped[str] = mapped_column(String(500))

    def to_dict(self):
        """Convert the history entry to a dictionary."""
        return {
            "id": self.id,
            "incident_id": self.incident_id,
            "recorded_at": self.recorded_at,
            "service": self.service,
            "previous_state": self.previous_state,
            "current_state": self.current_state,
            "incident": {
                "title": self.title,
                "description": self.description,
                "components": self.components,
                "url": self.url
            }
        }
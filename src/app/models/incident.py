from datetime import datetime
from typing import List
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(primary_key=True)
    service: Mapped[str] = mapped_column(String(100))
    previous_state: Mapped[str] = mapped_column(String(50))
    current_state: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Incident details
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(String(1000))
    components: Mapped[List[str]] = mapped_column(JSON)
    url: Mapped[str] = mapped_column(String(500))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if 'created_at' not in kwargs:
            self.created_at = datetime.utcnow()

    def to_dict(self):
        """Convert the model instance to a dictionary matching the response schema."""
        return {
            "id": self.id,
            "service": self.service,
            "previous_state": self.previous_state,
            "current_state": self.current_state,
            "created_at": self.created_at,
            "incident": {
                "title": self.title,
                "description": self.description,
                "components": self.components,
                "url": self.url
            }
        }
"""Database access layer for incident persistence."""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.incident import IncidentModel


class IncidentRepository:
    """
    Handles all DB interactions for incidents.
    """

    def __init__(self, db: Session):
        """Create a repository bound to the provided SQLAlchemy session."""
        self.db = db

    def create(self, incident: IncidentModel) -> IncidentModel:
        """Persist a new incident and return the refreshed instance."""
        self.db.add(incident)
        self.db.commit()
        self.db.refresh(incident)
        return incident

    def get_by_id(self, incident_id: str) -> Optional[IncidentModel]:
        """Return an incident by ID, or `None` if not found."""
        return (
            self.db.query(IncidentModel)
            .filter(IncidentModel.id == incident_id)
            .first()
        )

    def list(
        self,
        severity: Optional[str] = None,
        erp_module: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[IncidentModel]:
        """List incidents, optionally filtered by severity, module, and status."""
        query = self.db.query(IncidentModel)

        if severity:
            query = query.filter(IncidentModel.severity == severity)
        if erp_module:
            query = query.filter(IncidentModel.erp_module == erp_module)
        if status:
            query = query.filter(IncidentModel.status == status)

        return query.order_by(IncidentModel.created_at.desc()).all()

    def update_status(
        self, incident: IncidentModel, status: str
    ) -> IncidentModel:
        """Update an incident's status and return the refreshed instance."""
        incident.status = status
        self.db.commit()
        self.db.refresh(incident)
        return incident

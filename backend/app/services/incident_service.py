"""Domain service for incident creation, listing, and status updates."""

import uuid
from datetime import datetime

from app.schemas.incident import (
    IncidentCreateRequest,
    IncidentStatus,
)
from app.services.enrichment_service import EnrichmentService
from app.repositories.incident_repository import IncidentRepository
from app.models.incident import IncidentModel
from app.db.session import get_db


class IncidentService:
    """
    Orchestrates incident creation, enrichment, and persistence.
    """

    def __init__(self):
        """Initialize the service and its dependencies."""
        self.enrichment_service = EnrichmentService()

    def create_incident(self, payload: IncidentCreateRequest):
        """Create, enrich, and persist a new incident."""
        with get_db() as db:
            repo = IncidentRepository(db)

            enrichment = self.enrichment_service.enrich(payload)

            incident = IncidentModel(
                id=str(uuid.uuid4()),
                title=payload.title,
                description=payload.description,
                erp_module=payload.erp_module,
                environment=payload.environment,
                business_unit=payload.business_unit,
                severity=enrichment["severity"],
                category=enrichment["category"],
                auto_summary=enrichment["auto_summary"],
                suggested_action=enrichment["suggested_action"],
                status=IncidentStatus.OPEN,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            return repo.create(incident)

    def list_incidents(self, severity=None, erp_module=None, status=None):
        """Return incidents matching the optional filter parameters."""
        with get_db() as db:
            repo = IncidentRepository(db)
            return repo.list(severity, erp_module, status)

    def get_incident_by_id(self, incident_id: str):
        """Return an incident by ID, or `None` if it does not exist."""
        with get_db() as db:
            repo = IncidentRepository(db)
            return repo.get_by_id(incident_id)

    def update_incident_status(self, incident_id: str, status: IncidentStatus):
        """Update the status for an existing incident and persist the change."""
        with get_db() as db:
            repo = IncidentRepository(db)
            incident = repo.get_by_id(incident_id)
            if not incident:
                return None

            incident.updated_at = datetime.utcnow()
            return repo.update_status(incident, status)

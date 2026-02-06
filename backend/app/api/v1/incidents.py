"""Incident API routes (v1)."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.schemas.incident import (
    ERPModule,
    IncidentCreateRequest,
    IncidentStatus,
    IncidentResponse,
    IncidentStatusUpdateRequest,
    Severity,
)
from app.services.incident_service import IncidentService

router = APIRouter()

incident_service = IncidentService()


@router.post(
    "/incidents",
    response_model=IncidentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new ERP incident",
)
def create_incident(payload: IncidentCreateRequest):
    """
    Creates a new incident and enriches it with severity, category,
    and optional AI-generated metadata.
    """
    return incident_service.create_incident(payload)


@router.get(
    "/incidents",
    response_model=List[IncidentResponse],
    summary="List incidents",
)
def list_incidents(
    severity: Severity | None = None,
    erp_module: ERPModule | None = None,
    status: IncidentStatus | None = None,
):
    """
    Returns all incidents with optional filters.
    """
    return incident_service.list_incidents(
        severity=severity,
        erp_module=erp_module,
        status=status,
    )


@router.get(
    "/incidents/{incident_id}",
    response_model=IncidentResponse,
    summary="Get incident details",
)
def get_incident(incident_id: UUID):
    """Fetch a single incident by its ID."""
    incident = incident_service.get_incident_by_id(str(incident_id))
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found",
        )
    return incident


@router.patch(
    "/incidents/{incident_id}/status",
    response_model=IncidentResponse,
    summary="Update incident status",
)
def update_incident_status(
    incident_id: UUID,
    payload: IncidentStatusUpdateRequest,
):
    """Update the status of an incident."""
    incident = incident_service.update_incident_status(
        incident_id=str(incident_id),
        status=payload.status,
    )
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found",
        )
    return incident

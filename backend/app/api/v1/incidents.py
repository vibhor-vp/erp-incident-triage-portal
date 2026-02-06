"""Incident API routes (v1)."""

from fastapi import APIRouter, HTTPException, status
from typing import List

from app.schemas.incident import (
    IncidentCreateRequest,
    IncidentResponse,
    IncidentStatusUpdateRequest,
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
    severity: str | None = None,
    erp_module: str | None = None,
    status: str | None = None,
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
def get_incident(incident_id: str):
    """Fetch a single incident by its ID."""
    incident = incident_service.get_incident_by_id(incident_id)
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
    incident_id: str,
    payload: IncidentStatusUpdateRequest,
):
    """Update the status of an incident."""
    incident = incident_service.update_incident_status(
        incident_id=incident_id,
        status=payload.status,
    )
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found",
        )
    return incident

"""Pydantic schemas and enums for incident-related API payloads."""

from datetime import datetime
from typing import Optional
from enum import Enum

from pydantic import BaseModel, Field


class ERPModule(str, Enum):
    """Supported ERP modules for incident classification."""

    AP = "AP"
    AR = "AR"
    GL = "GL"
    INVENTORY = "INVENTORY"
    HR = "HR"
    PAYROLL = "PAYROLL"


class Environment(str, Enum):
    """Deployment environments in which an incident can occur."""

    PROD = "PROD"
    TEST = "TEST"


class Severity(str, Enum):
    """Incident severity levels."""

    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


class Category(str, Enum):
    """High-level incident categories."""

    CONFIGURATION = "CONFIGURATION_ISSUE"
    DATA = "DATA_ISSUE"
    INTEGRATION = "INTEGRATION_FAILURE"
    SECURITY = "SECURITY_ACCESS"
    UNKNOWN = "UNKNOWN"


class IncidentStatus(str, Enum):
    """Lifecycle states for an incident."""

    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class IncidentCreateRequest(BaseModel):
    """Request body for creating a new incident."""

    title: str = Field(..., min_length=5)
    description: str = Field(..., min_length=10)
    erp_module: ERPModule
    environment: Environment
    business_unit: str


class IncidentStatusUpdateRequest(BaseModel):
    """Request body for updating an incident's status."""

    status: IncidentStatus


class IncidentResponse(BaseModel):
    """Response model for an incident returned by the API."""

    id: str
    title: str
    description: str
    erp_module: ERPModule
    environment: Environment
    business_unit: str
    severity: Severity
    category: Category
    auto_summary: Optional[str]
    suggested_action: Optional[str]
    status: IncidentStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration for ORM attribute loading."""

        from_attributes = True

"""SQLAlchemy model definitions for incidents."""

from sqlalchemy import (
    Column,
    String,
    DateTime,
    Text,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class IncidentModel(Base):
    """Database model representing an ERP incident."""

    __tablename__ = "incidents"

    id = Column(UUID(as_uuid=False), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)

    erp_module = Column(String(50), nullable=False, index=True)
    environment = Column(String(10), nullable=False)
    business_unit = Column(String(100), nullable=False)

    severity = Column(String(5), nullable=False, index=True)
    category = Column(String(50), nullable=False)

    auto_summary = Column(Text, nullable=True)
    suggested_action = Column(Text, nullable=True)

    status = Column(String(20), nullable=False, index=True)

    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)


# Helpful composite indexes for common queries
Index(
    "idx_incidents_severity_module",
    IncidentModel.severity,
    IncidentModel.erp_module,
)

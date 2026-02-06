"""Incident enrichment logic (rule-based with optional AI stub)."""

from app.schemas.incident import (
    Severity,
    Category,
    IncidentCreateRequest,
)
# from openai import OpenAI  # uncomment when wiring real OpenAI


class EnrichmentService:
    """
    Handles incident enrichment using rule-based logic
    and optional OpenAI summarization.
    """

    def enrich(self, payload: IncidentCreateRequest) -> dict:
        """Enrich an incident payload with severity, category, and metadata."""
        severity = self._determine_severity(payload)
        category = self._determine_category(payload)

        summary, suggested_action = self._ai_enrich(payload)

        return {
            "severity": severity,
            "category": category,
            "auto_summary": summary,
            "suggested_action": suggested_action,
        }

    def _determine_severity(self, payload: IncidentCreateRequest) -> Severity:
        """Infer severity from the incident description and environment."""
        text = payload.description.lower()

        if payload.environment == "Prod" and any(
            word in text for word in ["down", "failed", "stuck", "error"]
        ):
            return Severity.P1
        if "delay" in text or "slow" in text:
            return Severity.P2
        return Severity.P3

    def _determine_category(self, payload: IncidentCreateRequest) -> Category:
        """Infer a category from keywords in the incident description."""
        text = payload.description.lower()

        if "permission" in text or "access" in text:
            return Category.SECURITY
        if "integration" in text or "interface" in text:
            return Category.INTEGRATION
        if "data" in text or "record" in text:
            return Category.DATA
        if "config" in text or "setup" in text:
            return Category.CONFIGURATION
        return Category.UNKNOWN

    def _ai_enrich(self, payload: IncidentCreateRequest):
        """
        Stubbed AI enrichment.
        In production this would call OpenAI.
        """
        # client = OpenAI()
        # response = client.responses.create(...)

        summary = f"Issue reported in {payload.erp_module} module affecting {payload.business_unit}"
        suggested_action = "Review recent changes and validate system logs."

        return summary, suggested_action

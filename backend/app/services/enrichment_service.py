"""Incident enrichment logic (rule-based with OpenAI augmentation)."""

from __future__ import annotations

import json

from openai import OpenAI

from app.core.config import settings
from app.schemas.incident import Category, Environment, IncidentCreateRequest, Severity


AI_ENRICH_PROMPT = """You are an ERP incident triage assistant.

Given an incident report, classify it into one of the allowed categories and
produce:
- a short, user-facing summary (1-3 sentences)
- a concrete suggested action (1-3 bullets or 1-2 sentences)

Be accurate, concise, and avoid fabricating details.
"""

AI_ENRICH_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "category": {"type": "string", "enum": [c.value for c in Category]},
        "auto_summary": {"type": "string", "minLength": 1},
        "suggested_action": {"type": "string", "minLength": 1},
    },
    "required": ["category", "auto_summary", "suggested_action"],
}


class EnrichmentService:
    """
    Handles incident enrichment using rule-based logic
    and optional OpenAI summarization.
    """

    def __init__(self) -> None:
        """Initialize the enrichment service and optional OpenAI client."""
        self._client: OpenAI | None = None
        if settings.OPENAI_API_KEY:
            self._client = OpenAI(api_key=settings.OPENAI_API_KEY)

        self._analysis_cache: dict[str, dict | None] = {}

    def enrich(self, payload: IncidentCreateRequest) -> dict:
        """Enrich an incident payload with severity, category, and metadata."""
        severity = self._determine_severity(payload)

        openai_analysis = self._openai_analyze(payload)

        if openai_analysis:
            category = openai_analysis.get("category")
            summary = openai_analysis.get("auto_summary")
            suggested_action = openai_analysis.get("suggested_action")
        else:
            category = self._determine_category(payload)
            summary = "NA"
            suggested_action = "NA"

        return {
            "severity": severity,
            "category": category,
            "auto_summary": summary,
            "suggested_action": suggested_action,
        }

    def _determine_severity(self, payload: IncidentCreateRequest) -> Severity:
        """Infer severity from the incident description and environment."""
        text = payload.description.lower()

        if payload.environment == Environment.PROD or any(
            word in text for word in ["down", "failed", "stuck", "error"]
        ):
            return Severity.P1
        if "delay" in text or "slow" in text:
            return Severity.P2
        return Severity.P3

    def _determine_category(self, payload: IncidentCreateRequest) -> Category:
        """Infer a category, preferring OpenAI classification when available."""
        analysis = self._openai_analyze(payload)
        if analysis and "category" in analysis:
            try:
                return Category(analysis["category"])
            except Exception:
                pass

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
        Produce AI-generated summary and suggested action.

        Uses OpenAI when configured; otherwise falls back to a deterministic stub.
        """
        analysis = self._openai_analyze(payload)
        if analysis:
            summary = analysis.get("auto_summary")
            suggested_action = analysis.get("suggested_action")
            if summary and suggested_action:
                return str(summary), str(suggested_action)

        summary = f"Issue reported in {payload.erp_module} module affecting {payload.business_unit}"
        suggested_action = "Review recent changes and validate system logs."

        return summary, suggested_action

    def _openai_analyze(self, payload: IncidentCreateRequest) -> dict | None:
        """Return OpenAI-derived category, summary, and suggested action."""
        if not self._client:
            return None

        input_text = "\n".join(
            [
                f"Title: {payload.title}",
                f"Description: {payload.description}",
                f"ERP module: {payload.erp_module}",
                f"Environment: {payload.environment}",
                f"Business unit: {payload.business_unit}",
            ]
        )

        try:
            response = self._client.responses.create(
                model=settings.OPENAI_MODEL,
                instructions=AI_ENRICH_PROMPT,
                input=input_text,
                text={
                    "format": {
                        "type": "json_schema",
                        "name": "incident_enrichment",
                        "description": "Incident enrichment output",
                        "schema": AI_ENRICH_SCHEMA,
                        "strict": True,
                    }
                },
                temperature=0.2,
            )
            analysis = json.loads(response.output_text)
        except Exception:
            analysis = None

        return analysis

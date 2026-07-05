"""Safety and input validation controls for biomedical research requests."""

from __future__ import annotations

import re

from pydantic import BaseModel, Field, field_validator


INJECTION_PATTERNS = (
    "ignore previous instructions",
    "reveal your system prompt",
    "developer message",
    "exfiltrate",
    "api key",
    "secret",
    "run this code",
    "delete files",
)

MEDICAL_ADVICE_PATTERNS = (
    "what dose",
    "dosage",
    "should i take",
    "treat my",
    "diagnose me",
    "patient-specific",
)


class SafetyDecision(BaseModel):
    """Safety screening result."""

    allowed: bool
    reason: str


class ResearchRequest(BaseModel):
    """Validated user request for a biomedical research dossier."""

    disease: str = Field(min_length=2, max_length=120)
    research_goal: str = Field(min_length=5, max_length=600)

    @field_validator("disease", "research_goal")
    @classmethod
    def validate_plain_text(cls, value: str) -> str:
        """Reject control-heavy or path-like input before agent execution."""

        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Input cannot be empty.")
        if re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", cleaned):
            raise ValueError("Input contains unsupported control characters.")
        return cleaned


def screen_request(request: ResearchRequest) -> SafetyDecision:
    """Apply basic safety and prompt-injection checks."""

    text = f"{request.disease} {request.research_goal}".lower()
    for pattern in INJECTION_PATTERNS:
        if pattern in text:
            return SafetyDecision(allowed=False, reason="Prompt injection or secret-seeking request.")
    for pattern in MEDICAL_ADVICE_PATTERNS:
        if pattern in text:
            return SafetyDecision(allowed=False, reason="Patient-specific medical advice is out of scope.")
    return SafetyDecision(allowed=True, reason="Research request is in scope.")

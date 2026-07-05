"""Shared typed models for agents, API, reports, and tests."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class SourceName(StrEnum):
    """Supported biomedical source systems."""

    PUBMED = "PubMed"
    UNIPROT = "UniProt"
    PUBCHEM = "PubChem"
    CLINICAL_TRIALS = "ClinicalTrials.gov"


class EvidenceItem(BaseModel):
    """One retrieved or synthesized evidence item."""

    source: SourceName | str
    title: str
    url: str | None = None
    summary: str
    confidence: float = Field(ge=0.0, le=1.0)
    metadata: dict[str, str] = Field(default_factory=dict)


class DiscoveryHypothesis(BaseModel):
    """One in silico drug discovery hypothesis generated from evidence."""

    target: str
    mechanism: str
    candidate_strategy: str
    rationale: str
    evidence_sources: list[str]
    novelty_score: float = Field(ge=0.0, le=1.0)
    feasibility_score: float = Field(ge=0.0, le=1.0)
    evidence_score: float = Field(ge=0.0, le=1.0)
    risk_flags: list[str] = Field(default_factory=list)

    @property
    def overall_score(self) -> float:
        """Return a conservative weighted prioritization score."""

        return round(
            (0.25 * self.novelty_score)
            + (0.35 * self.feasibility_score)
            + (0.40 * self.evidence_score),
            3,
        )


class AgentStep(BaseModel):
    """Progress marker for the user interface and logs."""

    name: str
    status: str
    detail: str


class ResearchDossier(BaseModel):
    """Final structured research output."""

    disease: str
    research_goal: str
    executive_summary: str
    evidence: list[EvidenceItem]
    discovery_hypotheses: list[DiscoveryHypothesis] = Field(default_factory=list)
    limitations: list[str]
    agent_steps: list[AgentStep]
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ResearchResponse(BaseModel):
    """API response for a research run."""

    dossier: ResearchDossier
    markdown: str

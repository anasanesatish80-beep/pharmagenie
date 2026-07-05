"""Evidence ranking agent."""

from pharmagenie.models import AgentStep, EvidenceItem


class EvidenceRankingAgent:
    """Ranks and reconciles evidence from domain agents."""

    name = "Evidence Ranking Agent"

    def rank(self, evidence: list[EvidenceItem]) -> tuple[list[EvidenceItem], AgentStep]:
        """Sort evidence by confidence while preserving source attribution."""

        ranked = sorted(evidence, key=lambda item: item.confidence, reverse=True)
        return ranked, AgentStep(
            name=self.name,
            status="completed",
            detail=f"Ranked {len(ranked)} evidence items by source confidence.",
        )

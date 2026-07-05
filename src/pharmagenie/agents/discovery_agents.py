"""Drug discovery-focused hypothesis generation agents."""

from pharmagenie.ai.synthesis import DiscoverySynthesisService
from pharmagenie.models import DiscoveryHypothesis, EvidenceItem


class TargetDiscoveryAgent:
    """Generates target hypotheses from retrieved biomedical evidence."""

    name = "Target Discovery Agent"

    def __init__(self) -> None:
        self.synthesis = DiscoverySynthesisService()

    async def generate(
        self,
        disease: str,
        research_goal: str,
        evidence: list[EvidenceItem],
    ) -> list[DiscoveryHypothesis]:
        """Create conservative in silico target hypotheses."""

        return await self.synthesis.synthesize(disease, research_goal, evidence)


class CandidatePrioritizationAgent:
    """Ranks discovery hypotheses for follow-up."""

    name = "Candidate Prioritization Agent"

    def prioritize(self, hypotheses: list[DiscoveryHypothesis]) -> list[DiscoveryHypothesis]:
        """Rank hypotheses by conservative weighted score."""

        return sorted(hypotheses, key=lambda hypothesis: hypothesis.overall_score, reverse=True)

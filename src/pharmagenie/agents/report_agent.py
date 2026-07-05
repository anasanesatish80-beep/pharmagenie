"""Report agent for final dossier assembly."""

from pharmagenie.models import AgentStep, EvidenceItem, ResearchDossier


class ReportAgent:
    """Builds the final structured dossier."""

    name = "Report Agent"

    def build(
        self,
        disease: str,
        research_goal: str,
        evidence: list[EvidenceItem],
        steps: list[AgentStep],
        discovery_hypotheses: list | None = None,
    ) -> ResearchDossier:
        """Create a research dossier with explicit limitations."""

        steps.append(
            AgentStep(
                name=self.name,
                status="completed",
                detail="Generated structured research dossier.",
            )
        )
        return ResearchDossier(
            disease=disease,
            research_goal=research_goal,
            executive_summary=(
                f"PharmaGenie generated an in silico drug discovery dossier for {disease}. "
                "It prioritizes evidence-backed hypotheses for human review and experimental "
                "follow-up; it does not validate efficacy or safety."
            ),
            evidence=evidence,
            discovery_hypotheses=discovery_hypotheses or [],
            limitations=[
                "In silico discovery support only; not medical advice or clinical decision support.",
                "Generated hypotheses require wet-lab validation, safety testing, and clinical review.",
                "Source clients attempt live retrieval and use explicit fallbacks when a source is unavailable.",
            ],
            agent_steps=steps,
        )

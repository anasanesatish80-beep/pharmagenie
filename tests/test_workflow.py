import pytest

from pharmagenie.agents import CoordinatorAgent
from pharmagenie.safety import ResearchRequest


@pytest.mark.asyncio
async def test_coordinator_returns_placeholder_dossier() -> None:
    request = ResearchRequest(
        disease="glioblastoma",
        research_goal="Summarize early-stage biomedical research evidence.",
    )

    dossier = await CoordinatorAgent().run(request)

    assert dossier.disease == "glioblastoma"
    assert len(dossier.evidence) == 4
    assert len(dossier.discovery_hypotheses) == 1
    assert any(step.name == "Planner Agent" for step in dossier.agent_steps)

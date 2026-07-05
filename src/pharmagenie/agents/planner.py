"""Planner agent for deciding which specialist agents should run."""

from pharmagenie.agents.domain_agents import (
    ClinicalTrialAgent,
    CompoundAgent,
    LiteratureAgent,
    ProteinAgent,
)
from pharmagenie.models import AgentStep


class PlannerAgent:
    """Creates the research execution plan."""

    name = "Planner Agent"

    def create_plan(self, disease: str, research_goal: str) -> tuple[list[object], AgentStep]:
        """Return the ordered specialist agents for a biomedical research task."""

        agents = [LiteratureAgent(), ProteinAgent(), CompoundAgent(), ClinicalTrialAgent()]
        return agents, AgentStep(
            name=self.name,
            status="completed",
            detail=f"Planned {len(agents)} source-focused subtasks for {disease}.",
        )

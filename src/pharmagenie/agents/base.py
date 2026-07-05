"""Shared agent abstractions."""

from abc import ABC, abstractmethod

from pharmagenie.models import AgentStep, EvidenceItem


class BaseResearchAgent(ABC):
    """Base class for deterministic scaffolding around ADK agent roles."""

    name: str

    def step(self, status: str, detail: str) -> AgentStep:
        """Return a standard progress event."""

        return AgentStep(name=self.name, status=status, detail=detail)

    @abstractmethod
    async def run(self, disease: str, research_goal: str) -> list[EvidenceItem]:
        """Execute the agent role and return evidence."""

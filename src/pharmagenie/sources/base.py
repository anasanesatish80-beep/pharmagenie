"""Base source client contracts."""

from abc import ABC, abstractmethod

from pharmagenie.models import EvidenceItem


class BiomedicalSourceClient(ABC):
    """Protocol-like base class for mockable biomedical source clients."""

    @abstractmethod
    async def search(self, disease: str, research_goal: str) -> list[EvidenceItem]:
        """Search a trusted source and return normalized evidence."""

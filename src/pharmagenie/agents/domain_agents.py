"""Domain-specific research agents."""

from pharmagenie.agents.base import BaseResearchAgent
from pharmagenie.mcp_servers.tools import (
    search_clinical_trials,
    search_pubchem,
    search_pubmed,
    search_uniprot,
)
from pharmagenie.models import EvidenceItem


class LiteratureAgent(BaseResearchAgent):
    """Collects literature evidence from PubMed."""

    name = "Literature Agent"

    async def run(self, disease: str, research_goal: str) -> list[EvidenceItem]:
        return await search_pubmed(disease, research_goal)


class ProteinAgent(BaseResearchAgent):
    """Collects protein target evidence from UniProt."""

    name = "Protein Agent"

    async def run(self, disease: str, research_goal: str) -> list[EvidenceItem]:
        return await search_uniprot(disease, research_goal)


class CompoundAgent(BaseResearchAgent):
    """Collects compound evidence from PubChem."""

    name = "Compound Agent"

    async def run(self, disease: str, research_goal: str) -> list[EvidenceItem]:
        return await search_pubchem(disease, research_goal)


class ClinicalTrialAgent(BaseResearchAgent):
    """Collects clinical trial evidence."""

    name = "Clinical Trial Agent"

    async def run(self, disease: str, research_goal: str) -> list[EvidenceItem]:
        return await search_clinical_trials(disease, research_goal)

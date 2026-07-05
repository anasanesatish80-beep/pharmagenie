"""MCP-style tool wrappers around source clients.

These functions are intentionally framework-light so they can be unit tested
without a running MCP server. The next implementation phase can register them
with the MCP Python SDK.
"""

from pharmagenie.models import EvidenceItem
from pharmagenie.sources.clinical_trials import ClinicalTrialsClient
from pharmagenie.sources.pubchem import PubChemClient
from pharmagenie.sources.pubmed import PubMedClient
from pharmagenie.sources.uniprot import UniProtClient


async def search_pubmed(disease: str, research_goal: str) -> list[EvidenceItem]:
    """Search PubMed through the PubMed source boundary."""

    return await PubMedClient().search(disease, research_goal)


async def search_uniprot(disease: str, research_goal: str) -> list[EvidenceItem]:
    """Search UniProt through the UniProt source boundary."""

    return await UniProtClient().search(disease, research_goal)


async def search_pubchem(disease: str, research_goal: str) -> list[EvidenceItem]:
    """Search PubChem through the PubChem source boundary."""

    return await PubChemClient().search(disease, research_goal)


async def search_clinical_trials(disease: str, research_goal: str) -> list[EvidenceItem]:
    """Search ClinicalTrials.gov through the trial source boundary."""

    return await ClinicalTrialsClient().search(disease, research_goal)

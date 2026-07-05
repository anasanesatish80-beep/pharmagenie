"""ADK-compatible function tools wrapping PharmaGenie source clients."""

import asyncio

from pharmagenie.agents import CoordinatorAgent
from pharmagenie.mcp_servers.tools import (
    search_clinical_trials,
    search_pubchem,
    search_pubmed,
    search_uniprot,
)
from pharmagenie.safety import ResearchRequest


def _run(coro):
    """Run async source code from synchronous ADK function tools."""

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    raise RuntimeError(f"Cannot run synchronous ADK wrapper inside active event loop {loop}.")


def pubmed_tool(disease: str, research_goal: str) -> dict:
    """Retrieve PubMed literature evidence for a disease and research goal."""

    items = _run(search_pubmed(disease, research_goal))
    return {"status": "success", "evidence": [item.model_dump(mode="json") for item in items]}


def uniprot_tool(disease: str, research_goal: str) -> dict:
    """Retrieve UniProt protein and target evidence for a disease and research goal."""

    items = _run(search_uniprot(disease, research_goal))
    return {"status": "success", "evidence": [item.model_dump(mode="json") for item in items]}


def pubchem_tool(disease: str, research_goal: str) -> dict:
    """Retrieve PubChem compound evidence for a disease and research goal."""

    items = _run(search_pubchem(disease, research_goal))
    return {"status": "success", "evidence": [item.model_dump(mode="json") for item in items]}


def clinical_trials_tool(disease: str, research_goal: str) -> dict:
    """Retrieve ClinicalTrials.gov evidence for a disease and research goal."""

    items = _run(search_clinical_trials(disease, research_goal))
    return {"status": "success", "evidence": [item.model_dump(mode="json") for item in items]}


def discovery_tool(disease: str, research_goal: str) -> dict:
    """Generate an in silico drug discovery dossier for a disease and research goal."""

    request = ResearchRequest(disease=disease, research_goal=research_goal)
    dossier = _run(CoordinatorAgent().run(request))
    return {"status": "success", "dossier": dossier.model_dump(mode="json")}

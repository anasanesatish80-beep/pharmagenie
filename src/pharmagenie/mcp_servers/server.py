"""Runnable FastMCP server exposing PharmaGenie biomedical tools."""

from mcp.server.fastmcp import FastMCP

from pharmagenie.mcp_servers.tools import (
    search_clinical_trials,
    search_pubchem,
    search_pubmed,
    search_uniprot,
)

mcp = FastMCP(
    "pharmagenie",
    instructions=(
        "Source-backed biomedical retrieval tools for in silico drug discovery. "
        "Outputs are evidence objects, not clinical recommendations."
    ),
)


@mcp.tool()
async def pubmed_search(disease: str, research_goal: str) -> list[dict]:
    """Search PubMed for biomedical literature evidence."""

    items = await search_pubmed(disease, research_goal)
    return [item.model_dump(mode="json") for item in items]


@mcp.tool()
async def uniprot_search(disease: str, research_goal: str) -> list[dict]:
    """Search UniProt for protein and target evidence."""

    items = await search_uniprot(disease, research_goal)
    return [item.model_dump(mode="json") for item in items]


@mcp.tool()
async def pubchem_search(disease: str, research_goal: str) -> list[dict]:
    """Search PubChem for compound evidence."""

    items = await search_pubchem(disease, research_goal)
    return [item.model_dump(mode="json") for item in items]


@mcp.tool()
async def clinical_trials_search(disease: str, research_goal: str) -> list[dict]:
    """Search ClinicalTrials.gov for clinical trial landscape evidence."""

    items = await search_clinical_trials(disease, research_goal)
    return [item.model_dump(mode="json") for item in items]


if __name__ == "__main__":
    mcp.run()

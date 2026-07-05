"""ClinicalTrials.gov-only MCP server."""

from mcp.server.fastmcp import FastMCP

from pharmagenie.mcp_servers.tools import search_clinical_trials

mcp = FastMCP("pharmagenie-clinical-trials")


@mcp.tool()
async def clinical_trials_search(disease: str, research_goal: str) -> list[dict]:
    """Search ClinicalTrials.gov for clinical trial landscape evidence."""

    items = await search_clinical_trials(disease, research_goal)
    return [item.model_dump(mode="json") for item in items]


if __name__ == "__main__":
    mcp.run()

"""PubChem-only MCP server."""

from mcp.server.fastmcp import FastMCP

from pharmagenie.mcp_servers.tools import search_pubchem

mcp = FastMCP("pharmagenie-pubchem")


@mcp.tool()
async def pubchem_search(disease: str, research_goal: str) -> list[dict]:
    """Search PubChem for compound evidence."""

    items = await search_pubchem(disease, research_goal)
    return [item.model_dump(mode="json") for item in items]


if __name__ == "__main__":
    mcp.run()

"""UniProt-only MCP server."""

from mcp.server.fastmcp import FastMCP

from pharmagenie.mcp_servers.tools import search_uniprot

mcp = FastMCP("pharmagenie-uniprot")


@mcp.tool()
async def uniprot_search(disease: str, research_goal: str) -> list[dict]:
    """Search UniProt for protein and target evidence."""

    items = await search_uniprot(disease, research_goal)
    return [item.model_dump(mode="json") for item in items]


if __name__ == "__main__":
    mcp.run()

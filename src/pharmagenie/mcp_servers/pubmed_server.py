"""PubMed-only MCP server."""

from mcp.server.fastmcp import FastMCP

from pharmagenie.mcp_servers.tools import search_pubmed

mcp = FastMCP("pharmagenie-pubmed")


@mcp.tool()
async def pubmed_search(disease: str, research_goal: str) -> list[dict]:
    """Search PubMed for biomedical literature evidence."""

    items = await search_pubmed(disease, research_goal)
    return [item.model_dump(mode="json") for item in items]


if __name__ == "__main__":
    mcp.run()

import os
import re
import sys
import uuid
from urllib.parse import parse_qs, urlparse

from loguru import logger
from mcp.server.fastmcp import Context, FastMCP
from pydantic import Field

from solargis.documentation_mcp_server.models import SearchResult
from solargis.documentation_mcp_server.server_utils import (
    read_kb_documentation_impl,
    search_kb_documentation_impl,
)

logger.remove()
logger.add(sys.stderr, level=os.getenv("FASTMCP_LOG_LEVEL", "WARNING"))

SESSION_UUID = str(uuid.uuid4())

mcp = FastMCP(
    "solargis.documentation-mcp-server",
    instructions="""
    # Solargis Documentation MCP server

    This server provides tools to access Solargis documentation/knowledge base, and search for content.

    ## Best Practices

    - For long documentation pages, make multiple calls to `read_documentation` with different `start_index` values for pagination
    - For very long documents (>30,000 characters), stop reading if you've found the needed information
    - When searching, use specific technical terms rather than general phrases
    - Always cite the documentation URL when providing information to users

    ## Tool Selection Guide

    - Use `search_documentation` when: You need to find knowledge base documentation about specific Solargis resource
    - Use `read_documentation` when: You have a specific knowledge base documentation URL and need its content
    """,
    dependencies=[
        "httpx",
        "pydantic",
        "beautifulsoup4",
    ],
)

@mcp.tool()
async def read_documentation(
    ctx: Context,
    url: str = Field(description="URL of the Solargis knowledge base documentation page to read"),
    max_length: int = Field(
        default=5000,
        description="Maximum number of characters to return.",
        gt=0,
        lt=1000000,
    ),
    start_index: int = Field(
        default=0,
        description="On return output starting at this character index, useful if a previous fetch was truncated and more content is required.",
        ge=0,
    ),
) -> str:
    """Fetch and convert a Solargis knowledge base documentation page to Markdown format.

    ## Usage

    This tool retrieves the content of a Solargis knowledge base documentation page and converts it to Markdown format.
    For long documents, you can make multiple calls with different start_index values to retrieve
    the entire content in chunks.

    ## URL Requirements

    - Must be from the kb.solargis.com domain
    - Must contain article-slug query
    - Must contain x-versiontype=Knowledgebase query

    ## Example slugs

    - https://kb.solargis.com/api/document/get-article-body?article-slug=solargis-time-series-and-tmy-api&x-versiontype=Knowledgebase
    - https://kb.solargis.com/api/document/get-article-body?article-slug=evaluate-add-ons&x-versiontype=Knowledgebase

    ## Output Format

    The output is formatted as Markdown text with:
    - Preserved headings and structure
    - Code blocks for examples
    - Lists and tables converted to Markdown format

    ## Handling Long Documents

    If the response indicates the document was truncated, you have several options:

    1. **Continue Reading**: Make another call with start_index set to the end of the previous response
    2. **Stop Early**: For very long documents (>30,000 characters), if you've already found the specific information needed, you can stop reading

    Args:
        ctx: MCP context for logging and error handling
        url: URL of the Solargis knowledge base documentation page to read
        max_length: Maximum number of characters to return
        start_index: On return output starting at this character index

    Returns:
        Markdown content of the Solargis knowledge base documentation
    """
    url_str = str(url)
    parsed_url = urlparse(url_str)
    query_params = parse_qs(parsed_url.query)

    if not re.match(r"^https?://kb\.solargis\.com/", url_str):
        await ctx.error(f"Invalid URL: {url_str}. URL must be from the kb.solargis.com domain")
        raise ValueError("URL must be from the kb.solargis.com domain")

    if "article-slug" not in query_params:
        await ctx.error(f"Invalid URL: {url_str}. URL must contain article-slug query parameter")
        raise ValueError("URL must contain article-slug query parameter")

    if "x-versiontype" not in query_params:
        await ctx.error(f"Invalid URL: {url_str}. URL must contain x-versiontype query parameter")
        raise ValueError("URL must contain x-versiontype query parameter")

    if version_value := query_params["x-versiontype"][0] != "Knowledgebase":
        await ctx.error(f"Invalid URL: {url_str}. x-versiontype must be 'Knowledgebase', got '{version_value}'")
        raise ValueError("x-versiontype must be 'Knowledgebase'")

    return await read_kb_documentation_impl(ctx, url, max_length, start_index, SESSION_UUID)


@mcp.tool()
async def search_documentation(
    ctx: Context,
    search_phrase: str = Field(description="Search phrase to use"),
    limit: int = Field(
        default=11,
        description="Maximum number of results to return",
        ge=1,
        le=99,
    ),
) -> list[SearchResult]:
    """Search Solargis knowledge base documentation.

    ## Usage

    This tool searches across all Solargis knowledge base documentation for pages matching your search phrase.
    Use it to find relevant documentation when you don't have a specific URL.

    ## Search Tips

    - Use specific technical terms rather than general phrases
    - Include precise names to narrow results (e.g., "time-series api" instead of just "ts api")
    - Use quotes for exact phrase matching (e.g., "Solargis units (SGU)")
    - Include abbreviations and alternative terms to improve results

    ## Result Interpretation

    Each result includes:
    - rank_order: The relevance ranking (lower is more relevant)
    - url: The documentation page URL
    - title: The page title
    - breadcrumb: The page site location hierarchy

    Args:
        ctx: MCP context for logging and error handling
        search_phrase: Search phrase to use
        limit: Maximum number of results to return

    Returns:
        List of search results with URLs, titles, and breadcrumbs
    """
    return await search_kb_documentation_impl(ctx, search_phrase, limit, SESSION_UUID)


def main():
    logger.info("Starting Solargis documentation MCP server")
    mcp.run()


if __name__ == "__main__":
    main()

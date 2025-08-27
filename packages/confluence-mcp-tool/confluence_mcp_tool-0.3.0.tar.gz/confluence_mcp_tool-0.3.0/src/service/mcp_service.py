import json
import logging
from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from confluence.main import ConfluenceTool, ConfluenceToolInputSchema
from confluence.search import ConfluenceSearch

logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP(
    name="confluence_mcp",
    instructions="Provides tools for interacting with Atlassian Confluence.",
)


@mcp.tool()
async def get_confluence_content(
    page_url: Annotated[
        str, Field(description="The Confluence page URL to retrieve content from")
    ],
):
    """Fetch content from a Confluence page using the page's URL.

    Args:
        page_url: The Confluence page URL to retrieve content from

    Returns:
        str: JSON string containing either:
            - {"output": ConfluenceToolOutputSchema} on success
            - {"error": str} on failure
    """
    try:
        confluence_tool = ConfluenceTool()
        content = confluence_tool.run(ConfluenceToolInputSchema(page_url=page_url))
        return json.dumps(
            {
                "output": content.model_dump(),
            },
            ensure_ascii=False,
        )
    except Exception as e:
        return json.dumps(
            {"error": f"Failed to process Confluence page: {str(e)}"},
            ensure_ascii=False,
        )


@mcp.tool(tags={"confluence", "read"})
async def confluence_search(
    cql: Annotated[
        str,
        Field(
            description=(
                "Search query - can be either a simple text (e.g. 'project documentation') or a CQL query string. "
                "Simple queries use 'siteSearch' by default, to mimic the WebUI search, with an automatic fallback "
                "to 'text' search if not supported. Examples of CQL:\n"
                "- Basic search: 'type=page'\n"
                "- Search by title: 'title~\"Meeting Notes\"'\n"
                "- Use siteSearch: 'siteSearch ~ \"important concept\"'\n"
                "- Use text search: 'text ~ \"important concept\"'\n"
                "- Recent content: 'created >= \"2023-01-01\"'\n"
                "- Content with specific label: 'label=documentation'\n"
                "- Recently modified content: 'lastModified > startOfMonth(\"-1M\")'\n"
                "- Content modified this year: 'creator = currentUser() AND lastModified > startOfYear()'\n"
                "- Content you contributed to recently: 'contributor = currentUser() AND lastModified > startOfWeek()'\n"
                "- Content watched by user: 'watcher = \"user@domain.com\" AND type = page'\n"
                '- Exact phrase in content: \'text ~ "\\"Urgent Review Required\\"" AND label = "pending-approval"\'\n'
                '- Title wildcards: \'title ~ "Minutes*")\'\n'
                'Note: Special identifiers need proper quoting in CQL: '
                "reserved words, numeric IDs, and identifiers with special characters. "
                "Space keys filters should be applied using the spaces_filter parameter."
            )
        ),
    ],
    spaces_filter: Annotated[
        str,
        Field(
            description=(
                "(Optional) Comma-separated list of space keys to filter results by. "
                "Overrides the environment variable CONFLUENCE_SPACES_FILTER if provided."
            ),
            default="",
        ),
    ] = "",
    limit: Annotated[
        int,
        Field(
            description="Maximum number of results (1-50)",
            default=10,
            ge=1,
            le=50,
        ),
    ] = 10,
):
    """Search Confluence content using simple terms or CQL.

    Args:
        cql: Search query - can be simple text or a CQL query string.
        spaces_filter: Comma-separated list of space keys to filter by.
        limit: Maximum number of results (1-50).

    Returns:
        JSON string representing a list of simplified Confluence page objects.
    """
    search_tool = ConfluenceSearch()
    if cql and not any(
        x in cql for x in ["=", "~", ">", "<", " AND ", " OR ", "currentUser()"]
    ):
        original_query = cql
        try:
            query = f'siteSearch ~ "{original_query}"'
            logger.info(
                f"Converting simple search term to CQL using siteSearch: {query}"
            )
            pages = search_tool.search(
                cql=query,
                page_url="",
                spaces_filter=spaces_filter,
                limit=limit,
            )
        except Exception as e:
            logger.warning(f"siteSearch failed ('{e}'), falling back to text search.")
            query = f'text ~ "{original_query}"'
            logger.info(f"Falling back to text search with CQL: {query}")
            pages = search_tool.search(
                cql=query,
                page_url="",
                spaces_filter=spaces_filter,
                limit=limit,
            )
    else:
        try:
            pages = search_tool.search(
                cql=cql, page_url="", spaces_filter=spaces_filter, limit=limit
            )
        except Exception as e:
            return json.dumps(
                {"error": f"Failed to search Confluence: {str(e)}"}, ensure_ascii=False
            )

    search_results = [page.to_simplified_dict() for page in pages]
    return json.dumps(search_results, indent=2, ensure_ascii=False)


def main() -> None:
    """Start the MCP service."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()

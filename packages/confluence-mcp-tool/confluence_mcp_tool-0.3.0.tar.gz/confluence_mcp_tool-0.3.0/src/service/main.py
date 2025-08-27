"""FastAPI service for the Confluence tool."""

from email.mime import base

from atlassian import Confluence
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

from confluence.main import ConfluenceTool, ConfluenceToolInputSchema
from confluence.search import ConfluenceSearch

load_dotenv()

app = FastAPI()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


class ToolInput(BaseModel):
    """Input model for the Confluence tool endpoint."""

    input: str  # e.g., Confluence page URL
    args: dict = {}  # optional, more args from user


class SeachToolInput(BaseModel):
    """Input model for the Confluence search endpoint."""

    cql: str
    base_url: str
    space_key: str
    args: dict = {}  # optional, more args from user


@app.post("/tool/confluence_reader/run")
async def run_tool(tool_input: ToolInput):
    """Run the Confluence tool with the given input.

    Args:
        tool_input: The input parameters for the tool

    Returns:
        The tool's output or an error message
    """
    try:
        page_url = tool_input.input
        confluence_tool = ConfluenceTool()
        content = confluence_tool.run(ConfluenceToolInputSchema(page_url=page_url))
        return {
            "output": content,
        }
    except Exception as e:
        return {"error": f"Failed to process Confluence page: {str(e)}"}


@app.post("/tool/confluence_reader/search")
async def confluence_search(search_input: SeachToolInput):
    """Search Confluence using CQL and return results."""
    try:
        cql = search_input.cql
        page_url = search_input.base_url
        limit = search_input.args.get("limit", 10)
        space_key = search_input.space_key
        search_tool = ConfluenceSearch()
        result = search_tool.search(
            cql=cql,
            page_url=page_url,
            spaces_filter=space_key,
            limit=limit,
        )
        print(f"Search results: {result}")
        return {"output": result}
    except Exception as e:
        return {"error": f"Failed to search Confluence: {str(e)}"}


def main() -> None:
    """Start the FastAPI service.

    Launches the service on 0.0.0.0:8000 so it is accessible from outside the container.
    """
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()

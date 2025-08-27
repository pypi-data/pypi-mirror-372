"""Confluence tool for retrieving Confluence page content."""

import os
import re

from atlassian import Confluence
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from confluence.utility.extract_confluence_page_ids import \
    extract_related_page_ids
from confluence.utility.extract_plantuml import \
    extract_and_decode_plantuml_from_confluence_macro

load_dotenv()


class ConfluenceToolInputSchema(BaseModel):
    """Tool for retrieving Confluence page content.

    Use this tool to get specifications from Confluence pages.
    """

    page_url: str = Field(..., description="Confluence page url.")


class PlantUmlSchema(BaseModel):
    """Schema for the extracted PlantUML content."""

    filename: str | None = Field(
        ..., description="Filename of the extracted PlantUML content."
    )
    plant_uml: str | None = Field(
        ..., description="PlantUML code extracted from the Confluence page."
    )


class ConfluenceToolOutputSchema(BaseModel):
    """Schema for the output of the ConfluenceTool."""

    title: str = Field(..., description="Title of the Confluence page.")
    content: str = Field(
        ..., description="Content of the Confluence page in HTML format."
    )
    plant_uml: PlantUmlSchema | None = Field(
        ..., description="PlantUML content extracted from the Confluence page."
    )
    related_pages_page_ids: list[str] | None = Field(
        ..., description="List of page IDs for related pages on Confluence."
    )


class ConfluenceToolConfig(BaseModel):
    """Configuration for the ConfluenceTool."""

    username: str = os.getenv("ATLASSIAN_USERNAME", "")
    api_key: str = os.getenv("ATLASSIAN_API_KEY", "")
    confluence_base_url: str = os.getenv("CONFLUENCE_URL", "")


# Default configuration at module level
DEFAULT_CONFLUENCE_CONFIG = ConfluenceToolConfig()


class ConfluenceTool:
    """Tool for retrieving Confluence page content based on the provided page identifier.

    Attributes:
        input_schema (ConfluenceToolInputSchema): The schema for the input data.
        output_schema (ConfluenceToolOutputSchema): The schema for the output data.
        base_url (str): The base URL for the Confluence site.
        username (str): The username for the Confluence site.
        password (str): The password for the Confluence site.
        space_key (str): The space key for the Confluence site.
        confluence (Confluence): The Confluence client.
    """

    input_schema = ConfluenceToolInputSchema
    output_schema = ConfluenceToolOutputSchema

    def __init__(self, config: ConfluenceToolConfig = DEFAULT_CONFLUENCE_CONFIG):
        """Initializes the ConfluenceTool."""
        self.username = config.username
        self.password = config.api_key

    def _parse_url(self, url: str) -> None:
        """
        Parses the Confluence URL to extract the sitename, base_url, space_key, and page_id.
        Set these values in the global variables.
        Raises:
            ValueError: If the URL does not match the expected format.
        Example:
            >>> confluence_url("https://example.atlassian.net/wiki/spaces/SPACE1/pages/123456789")
            {'sitename': 'example', 'base_url': 'https://example.atlassian.net/wiki', 'space_key': 'SPACE1', 'page_id': '123456789'}
        """

        # Try modern URL format first: /wiki/spaces/SPACE/pages/ID
        match = re.match(
            r"https://([^.]+)\.atlassian\.net/wiki/spaces/([^/]+)/pages/(\d+)", url
        )
        if match:
            sitename = match.group(1)
            space_key = match.group(2)
            page_id = match.group(3)
            self.base_url = f"https://{sitename}.atlassian.net/wiki"
            self.space_key = space_key
            self.page_id = page_id
            return

        # Try legacy viewpage.action format: /wiki/pages/viewpage.action?pageId=ID
        from urllib.parse import urlparse, parse_qs
        parsed_url = urlparse(url)
        if 'viewpage.action' in parsed_url.path:
            query_params = parse_qs(parsed_url.query)
            page_id = query_params.get('pageId', [None])[0]
            if page_id and parsed_url.netloc.endswith('.atlassian.net'):
                sitename = parsed_url.netloc.split('.')[0]
                self.base_url = f"https://{sitename}.atlassian.net/wiki"
                self.space_key = None  # Not available in viewpage.action URLs
                self.page_id = page_id
                return
        
        raise ValueError("Invalid Confluence URL format. Sitename not found.")

    def run(self, params: ConfluenceToolInputSchema) -> ConfluenceToolOutputSchema:
        """Execute the tool to retrieve and process a Confluence page.

        Args:
            params: Input parameters containing the page ID

        Returns:
            Processed page content including title, HTML, PlantUML, and related pages
        """
        self._parse_url(params.page_url)
        confluence = Confluence(
            url=self.base_url, username=self.username, password=self.password
        )
        page_data = confluence.get(
            f"rest/api/content/{self.page_id}?expand=body.storage"
        )

        content = None
        if page_data is not None:
            if isinstance(page_data, dict):
                content = (
                    page_data.get("body", {}).get("storage", {}).get("value", "") or ""
                )
            elif hasattr(page_data, "body"):
                content = (
                    getattr(page_data, "body", {}).get("storage", {}).get("value", "")
                    or ""
                )
        try:
            if content:
                plantuml_result = extract_and_decode_plantuml_from_confluence_macro(
                    content
                )
                if plantuml_result is not None:
                    _plant_uml, filename = plantuml_result
                    plant_uml_data = (
                        PlantUmlSchema(filename=filename, plant_uml=_plant_uml)
                        if _plant_uml
                        else None
                    )
                else:
                    plant_uml_data = None
            else:
                raise ValueError("No content found for the specified page ID.")
        except Exception:
            plant_uml_data = None

        _related_pages_page_ids = extract_related_page_ids(content or "")

        title = ""
        if isinstance(page_data, dict):
            title = page_data.get("title", "") or ""
        elif hasattr(page_data, "title"):
            title = getattr(page_data, "title", "")
        # else leave title as empty string

        return ConfluenceToolOutputSchema(
            title=title,
            content=content or "",
            plant_uml=plant_uml_data,
            related_pages_page_ids=(
                None if not _related_pages_page_ids else _related_pages_page_ids
            ),
        )


if __name__ == "__main__":
    from bs4 import BeautifulSoup

    confluence = ConfluenceTool()
    result = confluence.run(ConfluenceToolInputSchema(page_url=""))
    soup = BeautifulSoup(result.content, "html.parser")
    print(soup.prettify())
    print()
    print(result.plant_uml)
    print()
    print(result.related_pages_page_ids)

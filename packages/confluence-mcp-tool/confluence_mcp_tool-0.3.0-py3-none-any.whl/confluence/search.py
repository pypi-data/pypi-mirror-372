"""Module for Confluence search operations."""

import logging
import sys

import requests
from atlassian import Confluence
from dotenv import load_dotenv
from requests.exceptions import HTTPError

from confluence.main import ConfluenceToolConfig
from confluence.models.page import ConfluencePage
from confluence.models.search import ConfluenceSearchResult
from confluence.utility.parse_confluence_url import parse_confluence_url
from confluence.utils import quote_cql_identifier_if_needed

logger = logging.getLogger("confluence-tool")
DEFAULT_CONFLUENCE_CONFIG = ConfluenceToolConfig()

load_dotenv()


class ConfluenceSearch:
    """Class for handling Confluence search operations using CQL (Confluence Query Language)."""

    def __init__(self, config: ConfluenceToolConfig = DEFAULT_CONFLUENCE_CONFIG):
        """Initializes the ConfluenceTool."""
        self.username = config.username
        self.password = config.api_key
        self.base_url = config.confluence_base_url

    def search(
        self, cql: str, page_url: str, spaces_filter: str | None, limit: int = 10
    ) -> list[ConfluencePage]:
        """
        Search content using Confluence Query Language (CQL).

        Args:
            cql: Confluence Query Language string
            limit: Maximum number of results to return
            spaces_filter: Optional comma-separated list of space keys to filter by, overrides config

        Returns:
            List of ConfluencePage models containing search results

        Raises:
            MCPAtlassianAuthenticationError: If authentication fails with the Confluence API (401/403)
        """
        print(f"Searching Confluence with CQL: {cql} (limit={limit})", file=sys.stderr)
        if page_url:
            url_dict = parse_confluence_url(page_url)
            self.base_url = url_dict.get("base_url", self.base_url)
            self.space_key = url_dict.get("space_key", spaces_filter)
            self.page_id = url_dict.get("page_id", "")
        else:
            if not self.base_url:
                raise ValueError("Base URL must be provided if page_url is not set.")
        # Get the spaces filter from the URL which user provided
        if spaces_filter is None:
            spaces_filter = self.space_key

        if not cql:
            raise ValueError("CQL query must be provided for Confluence search.")

        try:
            # Apply spaces filter if present
            if spaces_filter:
                # Split spaces filter by commas and handle possible whitespace
                spaces = [s.strip() for s in spaces_filter.split(",")]

                # Build the space filter query part using proper quoting for each space key
                space_query = " OR ".join(
                    [
                        f"space = {quote_cql_identifier_if_needed(space)}"
                        for space in spaces
                    ]
                )

                # Add the space filter to existing query with parentheses
                if cql and space_query:
                    if (
                        "space = " not in cql
                    ):  # Only add if not already filtering by space
                        cql = f"({cql}) AND ({space_query})"
                else:
                    cql = space_query
                logger.info(f"Applied spaces filter to query: {cql}")

            # Initialize Confluence client with correct base URL
            confluence = Confluence(
                url=self.base_url, username=self.username, password=self.password
            )

            results = confluence.cql(cql=cql, limit=limit)

            if results is None:
                logger.error("Confluence API returned None for search results.")
                return []

            # Convert the response to a search result model
            search_result: ConfluenceSearchResult = (
                ConfluenceSearchResult.from_api_response(
                    data=results,
                    base_url=self.base_url,
                    cql_query=cql,
                )
            )

            # Process result excerpts as content
            processed_pages = []
            for page in search_result.results:
                for result_item in results.get("results", []):
                    if result_item.get("content", {}).get("id") == page.id:
                        excerpt = result_item.get("excerpt", "")
                        if excerpt:
                            page.content = excerpt
                        break
                processed_pages.append(page)

            return processed_pages
        except HTTPError as http_err:
            if http_err.response is not None and http_err.response.status_code in [
                401,
                403,
            ]:
                error_msg = (
                    f"Authentication failed for Confluence API ({http_err.response.status_code}). "
                    "Token may be expired or invalid. Please verify credentials."
                )
                logger.error(error_msg)
                raise ValueError(error_msg) from http_err
            else:
                logger.error(f"HTTP error during API call: {http_err}", exc_info=False)
                raise http_err
        except KeyError as e:
            logger.error(f"Missing key in search results: {str(e)}")
            return []
        except requests.RequestException as e:
            logger.error(f"Network error during search: {str(e)}")
            return []
        except (ValueError, TypeError) as e:
            logger.error(f"Error processing search results: {str(e)}")
            return []
        except Exception as e:  # noqa: BLE001 - Intentional fallback with logging
            logger.error(f"Unexpected error during search: {str(e)}")
            logger.debug("Full exception details for search:", exc_info=True)
            return []

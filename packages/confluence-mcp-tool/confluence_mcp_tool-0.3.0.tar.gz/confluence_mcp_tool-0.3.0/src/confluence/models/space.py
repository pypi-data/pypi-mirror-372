"""
Confluence space models.
This module provides Pydantic models for Confluence spaces.
"""

from typing import Any

from confluence.constants import CONFLUENCE_DEFAULT_ID, EMPTY_STRING, UNKNOWN
from confluence.models.base import ApiModel


class ConfluenceSpace(ApiModel):
    """
    Model representing a Confluence space.
    """

    id: str = CONFLUENCE_DEFAULT_ID
    key: str = EMPTY_STRING
    name: str = UNKNOWN
    type: str = "global"  # "global", "personal", etc.
    status: str = "current"  # "current", "archived", etc.

    @classmethod
    def from_api_response(
        cls, data: dict[str, Any], **kwargs: Any
    ) -> "ConfluenceSpace":
        """
        Create a ConfluenceSpace from a Confluence API response.

        Args:
            data: The space data from the Confluence API

        Returns:
            A ConfluenceSpace instance
        """
        if not data:
            return cls()

        return cls(
            id=str(data.get("id", CONFLUENCE_DEFAULT_ID)),
            key=data.get("key", EMPTY_STRING),
            name=data.get("name", UNKNOWN),
            type=data.get("type", "global"),
            status=data.get("status", "current"),
        )

    def to_simplified_dict(self) -> dict[str, Any]:
        """Convert to simplified dictionary for API response."""
        return {
            "key": self.key,
            "name": self.name,
            "type": self.type,
            "status": self.status,
        }

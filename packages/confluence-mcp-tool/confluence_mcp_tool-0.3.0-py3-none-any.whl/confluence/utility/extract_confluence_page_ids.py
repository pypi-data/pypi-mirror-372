"""Functions for extracting page IDs from Confluence URLs."""

import base64
import re
import struct


def get_page_id_from_shortened_url(shortened_url: str) -> str:
    """Convert a shortened Confluence URL to its page ID.

    Args:
        shortened_url: The shortened URL to convert

    Returns:
        The decoded page ID as a string
    """
    page_short_id = shortened_url.split("/")[-1:][0]
    page_short_id = page_short_id.replace("/", "\n").replace("-", "/").replace("_", "+")
    padded_id = page_short_id.ljust(11, "A") + "="
    decoded_id = base64.b64decode(padded_id)
    return str(struct.unpack("L", decoded_id)[0])


def extract_related_page_ids(input_str: str) -> list[str] | None:
    """Extract related page IDs from a string.

    Args:
        input_str (str): The input string containing the page IDs.

    Returns:
        list[str] | None: A list of extracted page IDs, or None if no matches were found.
    """
    # The regex patterns for page links and short URLs
    page_link_pattern = (
        r"https?:\/\/scbtechx\.atlassian\.net" r"\/wiki\/spaces\/\w+\/pages\/(\d+)"
    )
    shorturl_link_pattern = r"(https?:\/\/scbtechx.atlassian.net\/wiki\/x\/\w+)"

    # Find all matches
    page_link_matches = re.findall(page_link_pattern, input_str)
    shorturl_link_matches = re.findall(shorturl_link_pattern, input_str)
    shorturl_page_link_matches = [
        get_page_id_from_shortened_url(shortened_url)
        for shortened_url in shorturl_link_matches
    ]

    # Combine the matches
    page_link_matches.extend(shorturl_page_link_matches)

    # Remove duplicates and None values from individual matches
    page_link_matches = [pid for pid in set(page_link_matches) if pid is not None]

    # Return None if no valid matches were found, otherwise return the list
    return None if not page_link_matches else page_link_matches

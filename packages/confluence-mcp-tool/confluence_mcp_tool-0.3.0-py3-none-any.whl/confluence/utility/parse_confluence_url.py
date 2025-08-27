import re
from urllib.parse import unquote, urlparse


def parse_confluence_url(url):
    """
    Parse a Confluence URL, handling both complete and partial URLs
    """

    # Parse the URL
    parsed = urlparse(url)
    # Split the path into components
    path_parts = [part for part in parsed.path.split("/") if part]

    for i, part in enumerate(path_parts):
        print(f"  [{i}]: {part}")

    # Initialize variables
    wiki_type = None
    space_key = None
    page_id = None
    page_title = None
    url_type = "Unknown"

    # Determine URL type and extract components based on available parts
    if len(path_parts) >= 1 and path_parts[0] == "wiki":
        wiki_type = path_parts[0]

        if len(path_parts) == 1:
            url_type = "Confluence Root"

        elif len(path_parts) >= 2 and path_parts[1] == "spaces":
            if len(path_parts) == 2:
                url_type = "Spaces Root"

            elif len(path_parts) >= 3:
                space_key = path_parts[2]

                if len(path_parts) == 3:
                    url_type = "Space Overview"

                elif len(path_parts) >= 4 and path_parts[3] == "pages":
                    if len(path_parts) == 4:
                        url_type = "Space Pages List"

                    elif len(path_parts) >= 5:
                        page_id = path_parts[4]

                        if len(path_parts) == 5:
                            url_type = "Page (No Title)"

                        elif len(path_parts) >= 6:
                            page_title_encoded = path_parts[5]
                            page_title = unquote(page_title_encoded).replace("+", " ")
                            url_type = "Complete Page URL"

    # Return structured data
    return {
        "url_type": url_type,
        "domain": parsed.netloc,
        "space_key": space_key,
        "page_id": page_id,
        "page_title": page_title,
        "is_complete": url_type == "Complete Page URL",
    }

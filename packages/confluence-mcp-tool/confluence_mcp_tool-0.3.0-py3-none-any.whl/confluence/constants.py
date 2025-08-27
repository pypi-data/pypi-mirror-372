"""
Constants and default values for model conversions.

This module centralizes all default values and fallbacks used when
converting API responses to models, eliminating "magic strings" in
the codebase and providing a single source of truth for defaults.
"""

#
# Common defaults
#
EMPTY_STRING = ""
UNKNOWN = "Unknown"
UNASSIGNED = "Unassigned"
NONE_VALUE = "None"

#
# Confluence defaults
#
CONFLUENCE_DEFAULT_ID = "0"

# Space defaults
CONFLUENCE_DEFAULT_SPACE = {
    "key": EMPTY_STRING,
    "name": UNKNOWN,
    "id": CONFLUENCE_DEFAULT_ID,
}

# Version defaults
CONFLUENCE_DEFAULT_VERSION = {
    "number": 0,
    "when": EMPTY_STRING,
}

# Date/Time defaults
DEFAULT_TIMESTAMP = "1970-01-01T00:00:00.000+0000"

# Based on https://developer.atlassian.com/cloud/confluence/cql-functions/#reserved-words
# List might need refinement based on actual parser behavior
# Using lowercase for case-insensitive matching
RESERVED_CQL_WORDS = {
    "after",
    "and",
    "as",
    "avg",
    "before",
    "begin",
    "by",
    "commit",
    "contains",
    "count",
    "distinct",
    "else",
    "empty",
    "end",
    "explain",
    "from",
    "having",
    "if",
    "in",
    "inner",
    "insert",
    "into",
    "is",
    "isnull",
    "left",
    "like",
    "limit",
    "max",
    "min",
    "not",
    "null",
    "or",
    "order",
    "outer",
    "right",
    "select",
    "sum",
    "then",
    "was",
    "where",
    "update",
}

"""
Pipeline package - content aggregation, filtering, and digest generation.
"""

from .filter import ContentFilter
from .aggregate import aggregate_sources
from .digest import generate_digest

__all__ = ["ContentFilter", "aggregate_sources", "generate_digest"]


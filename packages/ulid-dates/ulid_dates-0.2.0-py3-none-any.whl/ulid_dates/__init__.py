"""ULID-Dates: A utility for handling ULID prefixes based on date ranges.

This package provides a simple function to calculate the 10-character ULID
timestamp prefixes that correspond to a given start and end date. This is
primarily useful for performing efficient, time-based range queries in databases
that use ULIDs as sortable keys.

Exports:
    ulid_prefix_range_for_dates: Calculates ULID prefixes for a date range.
"""

from .core import ulid_prefix_range_for_dates

__all__ = ["ulid_prefix_range_for_dates"]

from ulid import ULID
from datetime import datetime, timedelta


def ulid_prefix_range_for_dates(start: datetime, end: datetime) -> tuple[str, str]:
    """Calculates the 10-character ULID prefixes for a given date range.

    This is useful for time-based database queries where ULIDs are used as
    primary keys. By finding the prefixes for the start and end of a
    time range, you can efficiently scan for records within that range.

    For example, `... WHERE id >= 'start_prefix' AND id < 'end_prefix'`.

    Args:
        start: A datetime object for the beginning of the range (inclusive).
        end: A datetime object for the end of the range (exclusive).

    Returns:
        A tuple containing two 10-character ULID prefix strings:
        (start_prefix, end_prefix).

    Example:
    ```py
    from datetime import datetime, timedelta
    from ulid_dates import ulid_prefix_range_for_dates

    start_of_day = datetime(2023, 1, 1)
    end_of_day = start_of_day + timedelta(days=1)

    start, end = ulid_prefix_range_for_dates(start_of_day, end_of_day)
    ```
    """
    encoder = ULID()

    # Convert datetimes to millisecond timestamps.
    # .timestamp() returns seconds as a float, so we multiply by 1000.
    start_ms = int(start.timestamp() * 1000)
    end_ms = int(end.timestamp() * 1000)

    start_prefix = encoder.encode_timestamp(start_ms)
    end_prefix = encoder.encode_timestamp(end_ms)
    return start_prefix, end_prefix

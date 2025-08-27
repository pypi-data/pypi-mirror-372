from datetime import datetime, timedelta
from ulid_dates import ulid_prefix_range_for_dates
from hypothesis import given, strategies as st


def test_ulid_prefix_range_for_dates():
    """
    A basic test
    """
    start_date = datetime(2023, 1, 1)
    end_date = start_date + timedelta(days=1)

    start_prefix, end_prefix = ulid_prefix_range_for_dates(start_date, end_date)
    assert isinstance(start_prefix, str)
    assert isinstance(end_prefix, str)
    assert len(start_prefix) == 10
    assert len(end_prefix) == 10


def test_ulid_prefix_range_for_dates_with_known_values():
    """
    Tests ulid_prefix_range_for_dates against a known, hardcoded value
    to protect against regressions.
    """
    start_date = datetime(2023, 1, 1)
    end_date = start_date + timedelta(days=1)

    start_prefix, end_prefix = ulid_prefix_range_for_dates(start_date, end_date)

    assert start_prefix == "01GNM49240"
    assert end_prefix == "01GNPPNS40"


@given(
    start_date=st.datetimes(
        min_value=datetime(1970, 1, 1, 0, 0, 1), max_value=datetime(2200, 12, 31)
    ),
    time_delta=st.timedeltas(
        min_value=timedelta(milliseconds=1), max_value=timedelta(days=1000)
    ),
)
def test_ulid_prefix_properties_with_hypothesis(start_date, time_delta):
    """
    Tests that the ULID prefixes have correct properties for a wide range of dates.
    """
    end_date = start_date + time_delta

    start_prefix, end_prefix = ulid_prefix_range_for_dates(start_date, end_date)

    assert isinstance(start_prefix, str)
    assert isinstance(end_prefix, str)
    assert len(start_prefix) == 10
    assert len(end_prefix) == 10
    assert start_prefix <= end_prefix


def test_prefix_order_is_correctly_mapped_to_time():
    """
    Ensures that prefixes are correctly mapped to their timestamps and that
    chronological time order maps perfectly to the prefix's lexicographical order.
    """
    base_time = datetime(2024, 1, 1, 12, 0, 0)

    # Define times in order
    times = [
        base_time,
        base_time + timedelta(milliseconds=1),
        base_time + timedelta(seconds=2),
        base_time + timedelta(seconds=2, milliseconds=1),
        base_time + timedelta(seconds=2, milliseconds=2),
        base_time + timedelta(seconds=2, milliseconds=4),
        base_time + timedelta(seconds=2, milliseconds=999),
        base_time + timedelta(seconds=3),
    ]

    # Create a list of (timestamp, prefix) pairs
    time_prefix_pairs = [
        (t, ulid_prefix_range_for_dates(t, t + timedelta(seconds=1))[0])
        for t in sorted(times)
    ]

    # Create a new list by sorting the pairs based on the prefix
    sorted_by_prefix = sorted(time_prefix_pairs, key=lambda pair: pair[1])

    # Assert that the original list (sorted by time) is identical to the list sorted by prefix.
    assert time_prefix_pairs == sorted_by_prefix

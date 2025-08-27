import ulid_dates


def test_import_all_exposes_public_functions():
    """
    Tests that `from ulid_dates import *` exposes the public functions.
    """
    assert callable(ulid_dates.ulid_prefix_range_for_dates)

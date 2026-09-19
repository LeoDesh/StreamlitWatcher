import pytest

from garmin.utils.bucketing import calculate_bins_from_min_max_value


@pytest.mark.bucketing
def test_calculate_bins_values_from_min_max():
    bins = 5
    min_value = 1
    max_value = 6
    assert calculate_bins_from_min_max_value(min_value, max_value, bins) == list(
        range(1, 7)
    )

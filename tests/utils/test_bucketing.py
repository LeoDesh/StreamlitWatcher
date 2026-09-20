from contextlib import AbstractContextManager, nullcontext

import pytest

from garmin.utils.bucketing import (
    BinPlaner,
    BinStrategy,
    build_bins,
    calculate_bins_by_number,
    calculate_bins_by_size,
)


@pytest.mark.bucketing
@pytest.mark.parametrize(
    "start,step,interval,expected",
    [
        (1, 2, 4, list(range(1, 11, 2))),
        (1, 1, 0, [1, 2]),
        (1, 1, 4, list(range(1, 6, 1))),
        (1, 1.5, 4, [1, 2.5, 4, 5.5, 7.0]),
    ],
)
def test_build_bins(start: int, step: int, interval: int, expected: list[int]) -> None:
    assert build_bins(start, step, interval) == expected


@pytest.mark.bucketing
@pytest.mark.parametrize(
    "min_value,max_value,number_of_bins,expected",
    [
        (1, 9, 2, [1, 4, 2]),
        (1, 2, 1, [1, 1, 1]),
        (1, 13, 8, [1, 1.5, 8]),
        (1, 1, 1, [1, 0, 1]),
    ],
)
def test_calculate_bins_by_number(
    min_value: int, max_value: int, number_of_bins: int, expected: list[int]
) -> None:
    assert calculate_bins_by_number(min_value, max_value, number_of_bins) == expected


@pytest.mark.bucketing
@pytest.mark.parametrize(
    "min_value,max_value,size,expected",
    [
        (1, 10, 2, [1, 2, 5]),
        (0, 10, 2, [0, 2, 5]),
        (0, 10, 2.5, [0, 2.5, 4]),
        (0, 10, 3.5, [0, 3.5, 3]),
        (0, 1, 3.5, [0, 3.5, 1]),
    ],
)
def test_calculate_bins_by_size(
    min_value: int, max_value: int, size: float, expected: list[int]
) -> None:
    assert calculate_bins_by_size(min_value, max_value, size) == expected


@pytest.mark.bucketing
@pytest.mark.parametrize(
    "min_value,max_value,number_of_bins,enhancer,interval_start,interval_end,context",
    [
        (1, 10, 1, 0.5, 1, 10, nullcontext()),
        (5.0, 10.0, 5, 0.5, 2.5, 15.0, nullcontext()),
        (5.0, 10.0, None, 0.5, 2.5, 15.0, pytest.raises(ValueError)),
    ],
)
def test_bin_planer_initialization(
    min_value: float,
    max_value: float,
    number_of_bins: int,
    enhancer: float,
    interval_start: float,
    interval_end: float,
    context: AbstractContextManager,
):
    with context:
        bin_planer = BinPlaner(min_value, max_value, number_of_bins, enhancer=enhancer)
        assert bin_planer.interval_start == interval_start
        assert bin_planer.interval_end == interval_end


@pytest.mark.bucketing
@pytest.mark.parametrize(
    "min_value,max_value,number_of_bins,bin_size,strategy",
    [
        (1, 10, 1, None, BinStrategy.NUMBER),
        (5.0, 10.0, None, 1, BinStrategy.SIZE),
        (5, 10.0, 20, 0.5, BinStrategy.SIZE),
        (5, 10.0, 5, 0.5, BinStrategy.NUMBER),
    ],
)
def test_bin_planer_strategy(
    min_value: float,
    max_value: float,
    number_of_bins: int,
    bin_size: float,
    strategy: BinStrategy,
):
    bin_planer = BinPlaner(min_value, max_value, number_of_bins, bin_size)
    assert bin_planer.determine_strategy() == strategy

from dataclasses import dataclass
from enum import StrEnum, auto
from math import ceil


class BinStrategy(StrEnum):
    NUMBER = auto()
    SIZE = auto()


@dataclass
class BinPlaner[T]:
    min_value: T
    max_value: T
    number_of_bins: int | None = None
    bin_size: T | None = None
    enhancer: float = 0.02

    def __post_init__(self) -> None:
        self._validate_inputs()
        self._set_values()

    def determine_strategy(self) -> BinStrategy:
        if self.number_of_bins is not None and self.bin_size is not None:
            _, steps, _ = calculate_bins_by_number(
                self.min_value, self.max_value, self.number_of_bins
            )
            return BinStrategy.SIZE if steps < self.bin_size else BinStrategy.NUMBER
        return BinStrategy.SIZE if self.number_of_bins is None else BinStrategy.NUMBER

    def _validate_inputs(self) -> None:
        if self.number_of_bins is None and self.bin_size is None:
            raise ValueError("Either Number of Bins or Bin Size must be set.")
        if self.enhancer < 0:
            raise ValueError(f"Enhancer must be positive ({self.enhancer})")

    def _set_values(self) -> None:
        self.enhancer = self.enhancer if not isinstance(self.min_value, int) else 0
        self.interval_start = self.min_value * (1 - self.enhancer)
        self.interval_end = self.max_value * (1 + self.enhancer)

    def _calculate_bins_by_number(self) -> tuple[T, T, T]:
        return calculate_bins_by_number(
            self.interval_start, self.interval_end, self.number_of_bins
        )

    def _calculate_bins_by_size(self) -> tuple[T, T, T]:
        return calculate_bins_by_size(
            self.interval_start, self.interval_end, self.bin_size
        )

    def calculate_bins(self) -> list[T]:
        strategy = self.determine_strategy()
        bin_fundamentals = (
            self._calculate_bins_by_number()
            if strategy == BinStrategy.NUMBER
            else self._calculate_bins_by_size()
        )
        return build_bins(*bin_fundamentals)


def calculate_bins_by_number(
    min_value: float, max_value: float, number_of_bins: int
) -> list[float]:
    step = float(max_value - min_value) / number_of_bins
    return [min_value, step, number_of_bins]


def build_bins[T](start: T, step: T, intervals: int) -> list[T]:
    return (
        [start + step * interval for interval in range(intervals + 1)]
        if intervals > 0 and step > 0
        else list({start, start + step})
    )


def calculate_bins_by_size(
    min_value: float, max_value: float, bin_size: float
) -> tuple[float, float, float]:
    intervals = ceil(float(max_value - min_value) / bin_size)
    return [min_value, bin_size, intervals]


def create_bins_by_bounds(
    min_value: float,
    max_value: float,
    *,
    number_of_bins: int | None = None,
    bin_size: float | None = None,
    enhancer: float = 0.02,
) -> list[float]:
    planer = BinPlaner(min_value, max_value, number_of_bins, bin_size, enhancer)
    return planer.calculate_bins()


def create_bins_by_series(
    values: list[float],
    *,
    number_of_bins: int | None = None,
    bin_size: float | None = None,
    enhancer: float = 0.02,
) -> list[float]:
    min_value, max_value = min(values), max(values)
    planer = BinPlaner(min_value, max_value, number_of_bins, bin_size, enhancer)
    return planer.calculate_bins()

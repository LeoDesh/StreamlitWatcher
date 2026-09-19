def calculate_bins_from_min_max_value(
    min_value: float, max_value: float, number_of_bins: int
) -> list[float]:
    step = (max_value - min_value) / number_of_bins
    return sorted({min_value + step * idx for idx in range(number_of_bins + 1)})


def calculate_int_bins(min_value: int, max_value: int, bin_size: int) -> list[int]:
    intervals = int(float(max_value - min_value) // bin_size)
    return [min_value + bin_size * interval for interval in range(intervals + 2)]


def calculate_ticker_values(values: list[float], max_numb: int = 7) -> list[float]:
    sample_number = len(set(values))
    number_of_bins = min(sample_number, max_numb)
    min_val = min(values) * 0.98
    max_val = max(values) * 1.02
    return calculate_bins_from_min_max_value(min_val, max_val, number_of_bins)
